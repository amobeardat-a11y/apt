import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import quote
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import verify_hmac_signature
from app.models.order import Order, OrderStatus, PaymentMethod
from app.models.plan import PricingPlan
from app.models.user import User, SubscriptionTier
from app.schemas.order import OrderCreateRequest, OrderResponse, BankTransferInfo, PaymentWebhookPayload


class OrderService:

    BANK_CODE = "MB"  # MB Bank
    BANK_ACCOUNT = "982601289999"
    ACCOUNT_NAME = "CONG TY TNHH APTI VIET NAM"

    @classmethod
    def generate_vietqr_url(cls, amount: int, order_id: str) -> str:
        """Generates standard VietQR Napas 24/7 instant QR code."""
        encoded_name = quote(cls.ACCOUNT_NAME)
        encoded_info = quote(f"APTI {order_id}")
        return (
            f"https://img.vietqr.io/image/{cls.BANK_CODE}-{cls.BANK_ACCOUNT}-compact2.png"
            f"?amount={amount}&addInfo={encoded_info}&accountName={encoded_name}"
        )

    @classmethod
    async def create_order(
        cls,
        db: AsyncSession,
        user: User,
        req: OrderCreateRequest
    ) -> OrderResponse:
        # Fetch plan
        plan = await db.get(PricingPlan, req.plan_id)
        if not plan or not plan.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gói học không tồn tại hoặc đã ngừng cung cấp."
            )

        # Generate unique Order ID: APTI-YYYYMMDD-HEX
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        rand_str = secrets.token_hex(3).upper()
        order_id = f"APTI-{date_str}-{rand_str}"

        # Generate QR payment URL
        qr_url = cls.generate_vietqr_url(plan.price_vnd, order_id)

        new_order = Order(
            id=order_id,
            user_id=user.id,
            plan_id=plan.id,
            amount_vnd=plan.price_vnd,
            status=OrderStatus.PENDING,
            payment_method=req.payment_method,
            qr_payment_url=qr_url
        )
        db.add(new_order)
        await db.commit()
        await db.refresh(new_order)

        bank_info = BankTransferInfo(
            bank_name="MB Bank (Ngân hàng Quân Đội)",
            account_number=cls.BANK_ACCOUNT,
            account_holder=cls.ACCOUNT_NAME,
            transfer_content=f"APTI {order_id}",
            qr_url=qr_url
        )

        return OrderResponse(
            id=new_order.id,
            plan_id=plan.id,
            plan_name=plan.name,
            amount_vnd=new_order.amount_vnd,
            status=new_order.status,
            payment_method=new_order.payment_method,
            qr_payment_url=qr_url,
            bank_info=bank_info,
            created_at=new_order.created_at,
            paid_at=new_order.paid_at
        )

    @classmethod
    async def process_payment_webhook(
        cls,
        db: AsyncSession,
        payload: PaymentWebhookPayload,
        raw_body: bytes
    ) -> bool:
        """
        Secure Payment Webhook Handler:
        Validates HMAC signature to ensure request came from official payment gateway.
        """
        is_valid = verify_hmac_signature(
            raw_body,
            payload.signature,
            settings.PAYMENT_WEBHOOK_SECRET
        )
        if not is_valid and settings.ENVIRONMENT != "development":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chữ ký xác thực Webhook không hợp lệ."
            )

        stmt = select(Order).where(Order.id == payload.order_id)
        order = (await db.execute(stmt)).scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại.")

        if order.status == OrderStatus.COMPLETED:
            return True  # Idempotent response

        # Check amount
        if payload.amount < order.amount_vnd:
            order.status = OrderStatus.FAILED
            await db.commit()
            raise HTTPException(status_code=400, detail="Số tiền thanh toán không khớp.")

        await cls._fulfill_order(db, order, payload.transaction_code)
        return True

    @classmethod
    async def simulate_order_payment(cls, db: AsyncSession, order_id: str) -> Order:
        """Dev simulation for instant payment testing."""
        order = await db.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại.")
        if order.status == OrderStatus.COMPLETED:
            return order

        tx_code = f"SIM-{secrets.token_hex(4).upper()}"
        await cls._fulfill_order(db, order, tx_code)
        return order

    @classmethod
    async def _fulfill_order(cls, db: AsyncSession, order: Order, transaction_code: str):
        order.status = OrderStatus.COMPLETED
        order.transaction_code = transaction_code
        now = datetime.now(timezone.utc)
        order.paid_at = now

        # Update User Subscription
        user = await db.get(User, order.user_id)
        plan = await db.get(PricingPlan, order.plan_id)
        if user and plan:
            # Map plan_id to SubscriptionTier
            tier_map = {
                "starter-7d": SubscriptionTier.STARTER_7D,
                "master-30d": SubscriptionTier.MASTER_30D
            }
            user.subscription_tier = tier_map.get(plan.id, SubscriptionTier.STARTER_7D)
            
            # Extend existing subscription if still active, or start fresh from now
            start_time = now
            if user.subscription_expires_at and user.subscription_expires_at > now:
                start_time = user.subscription_expires_at
            
            user.subscription_expires_at = start_time + timedelta(days=plan.duration_days)

        await db.commit()

