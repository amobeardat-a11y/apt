import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    # 1. Weak password rejected by security policy
    weak_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "trainee@apti.vn",
            "full_name": "Nguyen Trainee",
            "password": "123"  # Too weak
        }
    )
    assert weak_res.status_code == 422

    # 2. Strong password registration accepted
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "trainee@apti.vn",
            "full_name": "Nguyen Trainee",
            "password": "Valid@Password2026!"
        }
    )
    assert reg_res.status_code == 201
    assert reg_res.json()["success"] is True

    # 3. Login success
    login_res = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "trainee@apti.vn",
            "password": "Valid@Password2026!"
        }
    )
    assert login_res.status_code == 200
    data = login_res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    # 4. Get profile with access token
    token = data["access_token"]
    me_res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 200
    assert me_res.json()["data"]["email"] == "trainee@apti.vn"


@pytest.mark.asyncio
async def test_brute_force_lockout(client: AsyncClient):
    # Attempt 5 consecutive failed logins
    for i in range(5):
        res = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "student@apti.vn",
                "password": f"WrongPassword{i}!"
            }
        )
        if i < 4:
            assert res.status_code == 401
        else:
            # 5th attempt triggers lockout
            assert res.status_code in [401, 423]

    # Subsequent attempt is locked out (423)
    locked_res = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "student@apti.vn",
            "password": "WrongPasswordAgain!"
        }
    )
    assert locked_res.status_code == 423

