# APTI Backend API - Nền tảng Ôn luyện Aptitude Test Tiếng Việt

Backend chuyên nghiệp xây dựng bằng **FastAPI**, tuân thủ nghiêm ngặt tiêu chuẩn bảo mật **OWASP Top 10** và tích hợp chuẩn cơ sở dữ liệu **Neon PostgreSQL Serverless (AWS / GCP)**.

---

## 1. Tính năng nổi bật & Kiến trúc Bảo mật (Security First)

###  Bảo mật & Kiểm soát truy cập (Security & Access Control)
* **JWT Access Token & Refresh Token Rotation**:
  * `Access Token` ngắn hạn (60 phút) mang thông tin định danh và phân quyền.
  * `Refresh Token` dài hạn (7 ngày) được **băm một chiều bằng SHA-256** và lưu trong database. Mỗi khi làm mới, token cũ bị thu hồi ngay lập tức (Token Rotation) để vô hiệu hóa nguy cơ replay attack và trộm cắp phiên.
* **Mật khẩu chuẩn An toàn cao**:
  * Băm bằng thuật toán **Bcrypt** với độ phức tạp `rounds = 12` kèm muối ngẫu nhiên (salt).
  * Quy tắc mật khẩu bắt buộc: Tối thiểu 8 ký tự, có chữ hoa, chữ thường, chữ số và ký tự đặc biệt (`!@#$%^&*...`).
* **Chống Brute-Force & Khóa tài khoản tự động**:
  * Tự động đếm số lần đăng nhập sai. Nếu nhập sai quá 5 lần liên tiếp, tài khoản bị tạm khóa 15 phút (`HTTP 423 Locked`).
* **Giới hạn tần suất yêu cầu (Rate Limiting)**:
  * Thuật toán trượt thời gian (Sliding Window Rate Limiter) độc lập theo IP và định tuyến.
  * Giới hạn nghiêm ngặt các endpoint nhạy cảm (`/api/v1/auth/login`, `/api/v1/auth/register`) để chống DDoS và dò mật khẩu.
* **Bảo vệ tính toàn vẹn đề thi (Anti-Cheating)**:
  * Trong luồng làm bài (`GET /quiz/questions`), trường `correct_index` và `explanation` **bị cắt bỏ hoàn toàn** trên server. Người làm bài không thể dùng Developer Tools (F12) hay HTTP Inspector để xem trước đáp án.
  * Toàn bộ việc chấm điểm được thực hiện khép kín trên Server (`POST /quiz/submit`).
* **Bảo mật thanh toán (HMAC-SHA256 Webhook)**:
  * Webhook xác nhận giao diện chuyển khoản (VietQR / MB Bank / MoMo) bắt buộc đối soát chữ ký số mật mã `HMAC-SHA256`.
* **Bộ tiêu đề bảo vệ HTTP (OWASP Recommended Security Headers)**:
  * `Content-Security-Policy (CSP)`
  * `Strict-Transport-Security (HSTS)`
  * `X-Content-Type-Options: nosniff`
  * `X-Frame-Options: DENY` (Chống Clickjacking)
  * `X-XSS-Protection: 1; mode=block`
  * `Referrer-Policy: strict-origin-when-cross-origin`
* **Safe Exception Handling**: Tự động chặn và ẩn toàn bộ vết lỗi hệ thống (Stack trace), tên bảng DB hoặc thông tin máy chủ, chỉ trả về mã lỗi thân thiện.

---

## 2. Kết nối Cơ sở Dữ liệu Neon PostgreSQL Serverless

Hệ thống được thiết kế đặc thù tối ưu cho kiến trúc **Neon Serverless**:

* **Async Driver**: Sử dụng `asyncpg` kết hợp `SQLAlchemy 2.0 Async`.
* **SSL bắt buộc**: Tự động nhận diện cấu hình Neon và kích hoạt `sslmode=require` / `ssl='require'`.
* **Connection Pooling cho Serverless**:
  * `pool_recycle = 300` (5 phút): Tự động tái tạo kết nối, tương thích hoàn hảo với cơ chế Sleep/Wakeup của Neon Compute Endpoint.
  * `pool_pre_ping = True`: Kiểm tra trạng thái kết nối còn sống trước khi thực thi truy vấn.
* **Hỗ trợ Fallback linh hoạt**: Nếu chưa cấu hình Neon, hệ thống tự động chạy trên SQLite Async nội bộ để chạy thử nghiệm ngay lập tức.

### Hướng dẫn kết nối Neon Postgres:
1. Đăng ký/Đăng nhập tại [https://console.neon.tech](https://console.neon.tech).
2. Tạo project mới (ví dụ: `apti-db`).
3. Tại trang **Dashboard**, chọn tab **Connection Details**, sao chép chuỗi **Connection string**.
4. Mở file `.env` trong thư mục `apti-backend/`, dán vào biến `DATABASE_URL`:
   ```env
   DATABASE_URL=postgresql+asyncpg://neondb_owner:YOUR_NEON_PASSWORD@ep-sweet-glade-123456.us-east-2.aws.neon.tech/neondb?ssl=require
   ```

---

## 3. Cấu trúc Thư mục

```
apti-backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── admin.py          # Quản trị hệ thống, thống kê doanh thu, người dùng
│   │   │   ├── auth.py           # Đăng ký, đăng nhập, JWT, refresh token, đổi mật khẩu
│   │   │   ├── documents.py      # Ebook, tài liệu giải đề Aptitude tiếng Việt
│   │   │   ├── health.py         # Kiểm tra trạng thái máy chủ & kết nối Neon DB
│   │   │   ├── orders.py         # Đơn hàng, tạo mã VietQR tự động, xử lý Webhook
│   │   │   ├── plans.py          # Gói 7 Ngày, Gói 30 Ngày Chinh phục MT
│   │   │   └── quiz.py           # Đề thi, chấm điểm server, bảng xếp hạng
│   │   └── router.py             # Router tổng hợp API v1
│   ├── core/
│   │   ├── dependencies.py       # RBAC (User, Admin), Subscription Guard
│   │   ├── middleware.py         # Security Headers, Timing, Safe Exception
│   │   ├── rate_limiter.py       # Sliding Window Rate Limiter
│   │   └── security.py           # Bcrypt hashing, JWT signer, HMAC-SHA256
│   ├── db/
│   │   ├── base.py               # DeclarativeBase & TimestampMixin
│   │   ├── seed.py               # Tự động nạp tài khoản admin, gói học, đề thi mẫu
│   │   └── session.py            # Async Engine & Sessionmaker cho Neon
│   ├── models/                   # SQLAlchemy 2.0 ORM Models
│   │   ├── document.py
│   │   ├── order.py
│   │   ├── plan.py
│   │   ├── quiz.py
│   │   └── user.py
│   ├── schemas/                  # Pydantic v2 Models (Validation & Serialization)
│   │   ├── auth.py
│   │   ├── common.py
│   │   ├── document.py
│   │   ├── order.py
│   │   ├── plan.py
│   │   ├── quiz.py
│   │   └── user.py
│   ├── services/                 # Business Logic Layer
│   │   ├── auth_service.py
│   │   ├── order_service.py
│   │   └── quiz_service.py
│   ├── config.py                 # Pydantic Settings & Biến môi trường
│   └── main.py                   # FastAPI Application Entrypoint
├── alembic/                      # Database Migrations (Tự động cập nhật Schema)
├── tests/                        # Bộ kiểm thử tự động Pytest
│   ├── test_auth.py
│   ├── test_quiz.py
│   └── test_security.py
├── .env.example                  # Mẫu biến môi trường
├── .env                          # Biến môi trường đang áp dụng
├── requirements.txt              # Danh sách thư viện Python
├── run.py                        # Script khởi chạy nhanh máy chủ
└── README.md                     # Tài liệu hướng dẫn chi tiết
```

---

## 4. Hướng dẫn Khởi chạy Máy chủ

### Bước 1: Cài đặt thư viện phụ thuộc
```bash
cd "apti-backend"
python -m pip install -r requirements.txt
```

### Bước 2: Khởi động Server API
```bash
python run.py
```
Hoặc dùng uvicorn trực tiếp:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Server sẽ tự động:
1. Đồng bộ các bảng vào Database Neon PostgreSQL (hoặc SQLite).
2. Tự động nạp tài khoản Super Admin, các gói học (7 Ngày, 30 Ngày), tài liệu và ngân hàng câu hỏi ban đầu.
3. Mở cổng `8000`.

### Bước 3: Truy cập Tài liệu API Trực quan
* **Swagger UI (Interactive API Docs)**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
* **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 5. Tài khoản Mặc định khi Khởi tạo (Seed Accounts)

Hệ thống đã tự động tạo sẵn 2 tài khoản mẫu:

| Loại tài khoản | Email | Mật khẩu mặc định | Quyền hạn |
| :--- | :--- | :--- | :--- |
| **Quản trị viên (Super Admin)** | `admin@apti.vn` | `Apti@2026Admin!` | Toàn quyền quản trị, thêm sửa xóa câu hỏi, xem thống kê, quản lý người dùng |
| **Học viên mẫu (Student)** | `student@apti.vn` | `Student@2026!` | Tài khoản học viên cơ bản |

---

## 6. Chạy Kiểm thử Tự động (Automated Tests)

Chạy bộ kiểm thử toàn diện bằng `pytest`:
```bash
python -m pytest tests -v
```

Kết quả:
* Kiểm thử bảo mật chính sách mật khẩu & chống Brute Force: **PASSED**
* Kiểm thử chống rò rỉ đáp án đề thi: **PASSED**
* Kiểm thử chấm điểm & phân tích kết quả: **PASSED**
* Kiểm thử tiêu đề bảo mật OWASP: **PASSED**
* Kiểm thử kết nối Neon DB Health: **PASSED**

