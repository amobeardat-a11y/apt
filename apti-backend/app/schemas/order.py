from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.models.order import OrderStatus, PaymentMethod


class OrderCreateRequest(BaseModel):
    plan_id: str
    payment_method: PaymentMethod = PaymentMethod.VIETQR


class BankTransferInfo(BaseModel):
    bank_name: str = "MB Bank (Ngân hàng Quân Đội)"
    account_number: str = "982601289999"
    account_holder: str = "CONG TY TNHH APTI VIET NAM"
    transfer_content: str
    qr_url: str


class OrderResponse(BaseModel):
    id: str
    plan_id: str
    plan_name: str
    amount_vnd: int
    status: OrderStatus
    payment_method: PaymentMethod
    qr_payment_url: Optional[str] = None
    bank_info: Optional[BankTransferInfo] = None
    created_at: datetime
    paid_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PaymentWebhookPayload(BaseModel):
    order_id: str
    transaction_code: str
    amount: int
    signature: str
    metadata: Optional[Dict[str, Any]] = None

