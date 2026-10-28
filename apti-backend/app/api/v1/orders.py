from typing import List
from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.order import Order
from app.schemas.order import (
    OrderCreateRequest,
    OrderResponse,
    PaymentWebhookPayload,
    BankTransferInfo
)
from app.schemas.common import APIResponse
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Đơn hàng & Thanh toán (Orders & Payments)"])


@router.post("/checkout", response_model=APIResponse[OrderResponse], status_code=status.HTTP_201_CREATED)
async def create_checkout_order(
    req: OrderCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Tạo đơn hàng mua gói luyện thi APTI.
    Hệ thống tự động sinh mã đơn hàng chuẩn, tạo mã QR VietQR Napas 24/7 tức thì kèm thông tin chuyển khoản.
    """
    order_res = await OrderService.create_order(db, current_user, req)
    return APIResponse(
        message="Tạo đơn hàng thành công! Quét mã VietQR để kích hoạt gói ngay tức thì.",
        data=order_res
    )


@router.get("/my-orders", response_model=APIResponse[List[OrderResponse]])
async def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lấy danh sách các đơn hàng đã đặt của người dùng."""
    stmt = (
        select(Order)
        .where(Order.user_id == current_user.id)
        .order_by(desc(Order.created_at))
    )
    orders = (await db.execute(stmt)).scalars().all()

    result = []
    for o in orders:
        plan = await o.awaitable_attrs.plan if hasattr(o, "awaitable_attrs") else None
        plan_name = plan.name if plan else o.plan_id
        result.append(OrderResponse(
            id=o.id,
            plan_id=o.plan_id,
            plan_name=plan_name,
            amount_vnd=o.amount_vnd,
            status=o.status,
            payment_method=o.payment_method,
            qr_payment_url=o.qr_payment_url,
            created_at=o.created_at,
            paid_at=o.paid_at
        ))
    return APIResponse(data=result)


@router.get("/{order_id}", response_model=APIResponse[OrderResponse])
async def get_order_detail(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Kiểm tra trạng thái đơn hàng (đã hoàn thành hay đang chờ quét mã)."""
    order = await db.get(Order, order_id)
    if not order or (order.user_id != current_user.id and current_user.role.value != "ADMIN"):
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng.")

    bank_info = BankTransferInfo(
        transfer_content=f"APTI {order.id}",
        qr_url=order.qr_payment_url or ""
    )

    return APIResponse(
        data=OrderResponse(
            id=order.id,
            plan_id=order.plan_id,
            plan_name=order.plan_id,
            amount_vnd=order.amount_vnd,
            status=order.status,
            payment_method=order.payment_method,
            qr_payment_url=order.qr_payment_url,
            bank_info=bank_info,
            created_at=order.created_at,
            paid_at=order.paid_at
        )
    )


@router.post("/webhook", response_model=APIResponse[None])
async def payment_webhook(
    request: Request,
    payload: PaymentWebhookPayload,
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook nhận thông báo thanh toán thành công từ cổng thanh toán / ngân hàng (SePay, Casso, VietQR, MoMo).
    BẢO MẬT: Bắt buộc xác thực chữ ký số HMAC-SHA256 để ngăn chặn giả mạo thông tin.
    """
    raw_body = await request.body()
    await OrderService.process_payment_webhook(db, payload, raw_body)
    return APIResponse(message="Xử lý thông báo thanh toán thành công.")


@router.post("/{order_id}/simulate-success", response_model=APIResponse[None])
async def simulate_order_payment_dev(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    API Giả lập thanh toán thành công (Dành cho môi trường phát triển & kiểm thử).
    Tự động nâng cấp tài khoản và kích hoạt thời hạn gói học tương ứng.
    """
    await OrderService.simulate_order_payment(db, order_id)
    return APIResponse(message=f"Đơn hàng {order_id} đã được kích hoạt thành công!")

