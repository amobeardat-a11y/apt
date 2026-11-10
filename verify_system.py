"""
APTI Full End-to-End Test & Verification Suite
Kiểm thử toàn diện Frontend & Backend, Bảo mật OWASP, Luồng làm bài, Thanh toán VietQR và Linh vật
"""

import subprocess
import time
import sys
import os
import urllib.request
import json
import httpx

BACKEND_DIR = r"c:\Users\cp\Downloads\New folder (3)\apti-backend"
FRONTEND_DIR = r"c:\Users\cp\Downloads\New folder (3)\apti-frontend"

def main():
    print("=" * 70)
    print(" BẮT ĐẦU KIỂM THỬ TOÀN DIỆN HỆ THỐNG APTI (FRONTEND & BACKEND)")
    print("=" * 70)

    # 1. Start Backend in background subprocess
    print("\n[1/6] Khởi động APTI Backend FastAPI...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=BACKEND_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # 2. Start Frontend static server on port 5500
    print("[2/6] Khởi động APTI Frontend HTTP Server (Port 5500)...")
    frontend_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", "5500", "--directory", FRONTEND_DIR, "--bind", "127.0.0.1"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    try:
        # Wait for servers to be ready
        print("Đang chờ máy chủ sẵn sàng...")
        backend_ready = False
        frontend_ready = False

        for _ in range(20):
            time.sleep(0.5)
            if not backend_ready:
                try:
                    r = urllib.request.urlopen("http://127.0.0.1:8000/api/v1/health", timeout=1)
                    if r.status == 200:
                        backend_ready = True
                except Exception:
                    pass
            if not frontend_ready:
                try:
                    r = urllib.request.urlopen("http://127.0.0.1:5500/index.html", timeout=1)
                    if r.status == 200:
                        frontend_ready = True
                except Exception:
                    pass
            if backend_ready and frontend_ready:
                break

        assert backend_ready, "Lỗi: Không thể kết nối tới Backend FastAPI trên cổng 8000!"
        assert frontend_ready, "Lỗi: Không thể kết nối tới Frontend trên cổng 5500!"
        print("-> Cả 2 máy chủ đã khởi động thành công và sẵn sàng nhận kết nối!")

        client = httpx.Client(base_url="http://127.0.0.1:8000/api/v1", timeout=10.0)

        # 3. Test Frontend Static Assets & No 404s
        print("\n[3/6] Kiểm thử tài nguyên tĩnh Frontend (Assets, Images, CSS, JS)...")
        assets_to_check = [
            "http://127.0.0.1:5500/index.html",
            "http://127.0.0.1:5500/css/design-tokens.css",
            "http://127.0.0.1:5500/css/components.css",
            "http://127.0.0.1:5500/css/layout.css",
            "http://127.0.0.1:5500/css/animations.css",
            "http://127.0.0.1:5500/js/main.js",
            "http://127.0.0.1:5500/js/services/apiClient.js",
            "http://127.0.0.1:5500/js/modules/authController.js",
            "http://127.0.0.1:5500/js/modules/toastManager.js",
            "http://127.0.0.1:5500/js/modules/quizController.js",
            "http://127.0.0.1:5500/js/modules/mascotInteractive.js",
            "http://127.0.0.1:5500/js/modules/soundEffects.js",
            "http://127.0.0.1:5500/js/modules/themeManager.js",
            "http://127.0.0.1:5500/js/modules/uiInteractions.js",
            "http://127.0.0.1:5500/assets/mascot/emtee-transparent.png",
            "http://127.0.0.1:5500/assets/icons/3-apti-app-icon.svg"
        ]

        for asset_url in assets_to_check:
            res = urllib.request.urlopen(asset_url)
            assert res.status == 200, f"Lỗi 404: {asset_url}"
        print(f"-> Kiểm tra {len(assets_to_check)} tệp tài nguyên: 100% TỒN TẠI VÀ CHÍNH XÁC (200 OK)!")

        # 4. Test Backend Security & OWASP Headers
        print("\n[4/6] Kiểm thử An ninh Bảo mật (OWASP Top 10 Security & Headers)...")
        root_res = httpx.get("http://127.0.0.1:8000/")
        assert root_res.status_code == 200
        headers = root_res.headers
        assert headers.get("X-Content-Type-Options") == "nosniff", "Thiếu header nosniff"
        assert headers.get("X-Frame-Options") == "DENY", "Thiếu header chống clickjacking DENY"
        assert headers.get("X-XSS-Protection") == "1; mode=block", "Thiếu header chống XSS"
        assert "Strict-Transport-Security" in headers, "Thiếu header HSTS"
        print("-> Tiêu đề bảo vệ HTTP (Security Headers): ĐẠT CHUẨN OWASP")

        # 5. Test User Journey: Register -> Login -> Anti-Cheat Quiz -> VietQR Checkout -> Fulfill
        print("\n[5/6] Kiểm thử Luồng Trải nghiệm Người dùng (End-to-End User Journey)...")
        
        # A. Register new student
        test_email = f"learner_{int(time.time())}@apti.vn"
        reg_res = client.post("/auth/register", json={
            "email": test_email,
            "full_name": "Trần Thị Học Viên",
            "password": "Learner@2026Password!",
            "phone": "0987654321"
        })
        assert reg_res.status_code == 201, f"Lỗi đăng ký: {reg_res.text}"
        print("  ✓ Đăng ký tài khoản mới: THÀNH CÔNG")

        # B. Login
        login_res = client.post("/auth/login", json={
            "email": test_email,
            "password": "Learner@2026Password!"
        })
        assert login_res.status_code == 200, f"Lỗi đăng nhập: {login_res.text}"
        token = login_res.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}
        print("  ✓ Đăng nhập nhận JWT Access Token & Refresh Token: THÀNH CÔNG")

        # C. Quiz anti-cheat check
        q_res = client.get("/quiz/questions?limit=5", headers=auth_headers)
        assert q_res.status_code == 200
        questions = q_res.json()["data"]
        assert len(questions) > 0
        for q in questions:
            assert "correct_index" not in q, "LỖI BẢO MẬT: Lộ đáp án đúng trong câu hỏi!"
            assert "explanation" not in q, "LỖI BẢO MẬT: Lộ lời giải trước khi nộp bài!"
        print(f"  ✓ Tải {len(questions)} câu hỏi trắc nghiệm (Bảo mật Anti-Cheat, không lộ đáp án): THÀNH CÔNG")

        # D. Submit quiz for server grading
        q1 = questions[0]
        sub_res = client.post("/quiz/submit", headers=auth_headers, json={
            "mode": "PRACTICE",
            "time_spent_seconds": 65,
            "answers": [{"question_id": q1["id"], "selected_index": 1}]
        })
        assert sub_res.status_code == 200
        result = sub_res.json()["data"]
        assert "score_percentage" in result
        assert "mascot_message" in result
        assert len(result["reviews"]) == 1
        print(f"  ✓ Nộp bài chấm điểm trên Server (Điểm: {result['score_percentage']}%, Em Tee phản hồi): THÀNH CÔNG")

        # E. Create Order & VietQR
        order_res = client.post("/orders/checkout", headers=auth_headers, json={
            "plan_id": "master-30d",
            "payment_method": "VIETQR"
        })
        assert order_res.status_code == 201
        order_data = order_res.json()["data"]
        order_id = order_data["id"]
        assert "vietqr.io" in order_data["qr_payment_url"]
        assert order_data["bank_info"]["account_number"] == "982601289999"
        print(f"  ✓ Tạo đơn hàng VietQR Napas 24/7 ({order_id}, 249.000 VNĐ, MB Bank): THÀNH CÔNG")

        # F. Fulfill payment
        sim_res = client.post(f"/orders/{order_id}/simulate-success", headers=auth_headers)
        assert sim_res.status_code == 200
        print("  ✓ Kích hoạt đơn hàng thanh toán thành công: THÀNH CÔNG")

        # G. Verify subscription upgrade
        me_res = client.get("/auth/me", headers=auth_headers)
        assert me_res.status_code == 200
        user_info = me_res.json()["data"]
        assert user_info["subscription_tier"] == "MASTER_30D"
        assert user_info["has_active_subscription"] is True
        print("  ✓ Nâng cấp tài khoản lên MASTER_30D (MT Master): THÀNH CÔNG")

        # H. Verify premium document unlocked
        doc_res = client.get("/documents/pack-numerical-mastery/download-link", headers=auth_headers)
        assert doc_res.status_code == 200
        assert "download_url" in doc_res.json()["data"]
        print("  ✓ Mở khóa tải tài liệu bản quyền Chuyên sâu PDF: THÀNH CÔNG")

        # 6. Admin RBAC Verification
        print("\n[6/6] Kiểm thử Phân quyền Quản trị (Admin RBAC & Dashboard)...")
        admin_login = client.post("/auth/login", json={
            "email": "admin@apti.vn",
            "password": "Apti@2026Admin!"
        })
        assert admin_login.status_code == 200
        admin_token = admin_login.json()["access_token"]
        stats_res = client.get("/admin/stats", headers={"Authorization": f"Bearer {admin_token}"})
        assert stats_res.status_code == 200
        stats = stats_res.json()["data"]
        print(f"  ✓ Dashboard Admin: {stats['total_users']} Học viên | Doanh thu: {stats['total_revenue_vnd']:,} VNĐ | Đề thi: {stats['total_questions_bank']} câu")

        print("\n" + "=" * 70)
        print(" KẾT QUẢ: TOÀN BỘ 100% CÁC BÀI KIỂM THỬ ĐỀU VƯỢT QUA XUẤT SẮC!")
        print("=" * 70)

    finally:
        print("\nĐang dọn dẹp các tiến trình máy chủ...")
        backend_proc.terminate()
        frontend_proc.terminate()
        backend_proc.wait()
        frontend_proc.wait()
        print("Đã hoàn tất dọn dẹp an toàn.")

if __name__ == "__main__":
    main()
