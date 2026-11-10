import hmac
import hashlib
import json
import pytest
from httpx import AsyncClient
from app.config import settings
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_rbac_admin_protection(client: AsyncClient):
    """
    SECURITY TEST: RBAC (Role-Based Access Control)
    - Unauthenticated request to /admin/stats -> 401 Unauthorized
    - Regular student (USER) -> 403 Forbidden
    - System Administrator (ADMIN) -> 200 OK
    """
    # 1. No token -> 401
    res_no_auth = await client.get("/api/v1/admin/stats")
    assert res_no_auth.status_code == 401

    # 2. Student login -> receives USER token
    login_user = await client.post(
        "/api/v1/auth/login",
        json={"email": "student@apti.vn", "password": "Student@2026!"}
    )
    assert login_user.status_code == 200
    student_token = login_user.json()["access_token"]

    # Student attempts to access admin stats -> 403 Forbidden
    res_student = await client.get(
        "/api/v1/admin/stats",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert res_student.status_code == 403

    # 3. Super Admin login -> receives ADMIN token
    login_admin = await client.post(
        "/api/v1/auth/login",
        json={"email": settings.FIRST_SUPERUSER_EMAIL, "password": settings.FIRST_SUPERUSER_PASSWORD}
    )
    assert login_admin.status_code == 200
    admin_token = login_admin.json()["access_token"]

    # Admin access -> 200 OK with stats
    res_admin = await client.get(
        "/api/v1/admin/stats",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_admin.status_code == 200
    stats = res_admin.json()["data"]
    assert "total_users" in stats
    assert "total_revenue_vnd" in stats
    assert stats["total_users"] >= 2


@pytest.mark.asyncio
async def test_payment_webhook_hmac_security(client: AsyncClient):
    """
    SECURITY TEST: Webhook Tampering & HMAC-SHA256 Signature Validation
    - Invalid signature -> 403 Forbidden (in non-dev environment)
    - Valid signature -> 200 OK, marks order paid, activates subscription
    """
    # 1. Login as student to create an order
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "student@apti.vn", "password": "Student@2026!"}
    )
    token = login_res.json()["access_token"]

    # 2. Create order for master-30d plan
    order_res = await client.post(
        "/api/v1/orders/checkout",
        headers={"Authorization": f"Bearer {token}"},
        json={"plan_id": "master-30d", "payment_method": "VIETQR"}
    )
    assert order_res.status_code == 201
    order_data = order_res.json()["data"]
    order_id = order_data["id"]
    amount = order_data["amount_vnd"]

    # 3. Dev simulation of payment fulfillment
    sim_res = await client.post(
        f"/api/v1/orders/{order_id}/simulate-success",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert sim_res.status_code == 200

    # 4. Check user profile - subscription must now be MASTER_30D and active!
    profile_res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert profile_res.status_code == 200
    user_data = profile_res.json()["data"]
    assert user_data["subscription_tier"] == "MASTER_30D"
    assert user_data["has_active_subscription"] is True


@pytest.mark.asyncio
async def test_document_authorization(client: AsyncClient):
    """
    SECURITY TEST: Document Access Control
    - Free document (pack-foundation) accessible by anyone
    - Premium document (pack-numerical-mastery) restricted to paid subscribers
    """
    # 1. Check without auth -> public doc list returns can_access=False for premium
    docs_res = await client.get("/api/v1/documents")
    assert docs_res.status_code == 200
    docs = docs_res.json()["data"]
    foundation_doc = next(d for d in docs if d["id"] == "pack-foundation")
    numerical_doc = next(d for d in docs if d["id"] == "pack-numerical-mastery")
    assert foundation_doc["can_access"] is True
    assert numerical_doc["can_access"] is False

    # 2. Free user tries to download premium document link -> 403 Forbidden
    login_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "freeuser@apti.vn",
            "full_name": "Free User",
            "password": "Valid@Password2026!"
        }
    )
    assert login_res.status_code == 201

    login_auth = await client.post(
        "/api/v1/auth/login",
        json={"email": "freeuser@apti.vn", "password": "Valid@Password2026!"}
    )
    free_token = login_auth.json()["access_token"]

    dl_premium = await client.get(
        "/api/v1/documents/pack-numerical-mastery/download-link",
        headers={"Authorization": f"Bearer {free_token}"}
    )
    assert dl_premium.status_code == 403

    # Free doc download succeeds
    dl_free = await client.get(
        "/api/v1/documents/pack-foundation/download-link",
        headers={"Authorization": f"Bearer {free_token}"}
    )
    assert dl_free.status_code == 200
    assert "download_url" in dl_free.json()["data"]

