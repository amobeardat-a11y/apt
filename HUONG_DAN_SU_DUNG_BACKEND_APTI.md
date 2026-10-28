# HƯỚNG DẪN SỬ DỤNG VÀ TÀI LIỆU KỸ THUẬT BACKEND APTI
## NỀN TẢNG LUYỆN THI APTITUDE TEST TIẾNG VIỆT
**Công nghệ:** FastAPI | Neon PostgreSQL Serverless | SQLAlchemy 2.0 Async | Pydantic v2 | OWASP Security

---

### MỤC LỤC
1. [TỔNG QUAN HỆ THỐNG VÀ KIẾN TRÚC](#1-tổng-quan-hệ-thống-và-kiến-trúc)
2. [HƯỚNG DẪN CÀI ĐẶT VÀ KHỞI CHẠY](#2-hướng-dẫn-cài-đặt-và-khởi-chạy)
3. [HƯỚNG DẪN CẤU HÌNH NEON POSTGRESQL CHI TIẾT](#3-hướng-dẫn-cấu-hình-neon-postgresql-chi-tiết)
4. [TÀI KHOẢN MẶC ĐỊNH VÀ PHÂN QUYỀN HỆ THỐNG (RBAC)](#4-tài-khoản-mặc-định-và-phân-quyền-hệ-thống-rbac)
5. [HƯỚNG DẪN CHI TIẾT CÁC PHÂN HỆ API](#5-hướng-dẫn-chi-tiết-các-phân-hệ-api)
   - [5.1. Phân hệ Xác thực & Bảo mật (Auth & Security)](#51-phân-hệ-xác-thực--bảo-mật-auth--security)
   - [5.2. Phân hệ Luyện thi & Đánh giá năng lực (Quiz & Assessment)](#52-phân-hệ-luyện-thi--đánh-giá-năng-lực-quiz--assessment)
   - [5.3. Phân hệ Gói học, Đơn hàng & VietQR (Plans, Orders & Payments)](#53-phân-hệ-gói-học-đơn-hàng--vietqr-plans-orders--payments)
   - [5.4. Phân hệ Tài liệu & Ebook (Document Packs)](#54-phân-hệ-tài-liệu--ebook-document-packs)
   - [5.5. Phân hệ Quản trị viên (Admin Dashboard)](#55-phân-hệ-quản-trị-viên-admin-dashboard)
   - [5.6. Phân hệ Giám sát hệ thống (Health Check)](#56-phân-hệ-giám-sát-hệ-thống-health-check)
6. [HƯỚNG DẪN MIGRATION CƠ SỞ DỮ LIỆU (ALEMBIC)](#6-hướng-dẫn-migration-cơ-sở-dữ-liệu-alembic)
7. [HƯỚNG DẪN CHẠY KIỂM THỬ TỰ ĐỘNG (PYTEST)](#7-hướng-dẫn-chạy-kiểm-thử-tự-động-pytest)
8. [BẢNG MÃ LỖI VÀ XỬ LÝ SỰ CỐ THƯỜNG GẶP (TROUBLESHOOTING)](#8-bảng-mã-lỗi-và-xử-lý-sự-cố-thường-gặp-troubleshooting)

---

### 1. TỔNG QUAN HỆ THỐNG VÀ KIẾN TRÚC

Hệ thống Backend **APTI** là nền tảng máy chủ cung cấp API cho ứng dụng luyện thi Aptitude Test tiếng Việt dành cho học viên chuẩn bị ứng tuyển Management Trainee (MT). 

Backend được xây dựng theo mô hình phân lớp hiện đại (**Clean Layered Architecture**):
* **API Route Layer (`app/api/v1/`)**: Tiếp nhận yêu cầu HTTP, kiểm tra Schema bằng Pydantic v2, điều hướng tới Service.
* **Service Layer (`app/services/`)**: Xử lý toàn bộ logic nghiệp vụ (tính điểm, phân tích đề thi, xác thực xoay vòng token, tạo mã VietQR).
* **Model & Persistence Layer (`app/models/`, `app/db/`)**: Tương tác cơ sở dữ liệu qua SQLAlchemy 2.0 Async ORM.
* **Security Core (`app/core/`)**: Chống Brute Force, Rate Limiting, OWASP Security Headers, băm Bcrypt, ký xác thực JWT.

```mermaid
flowchart TD
    Client["Frontend APTI (Web / Mobile)"] -->|HTTPS / REST API| MW["Security Middlewares (OWASP, Rate Limiter, Timing)"]
    MW --> Router["FastAPI Router (/api/v1)"]
    Router --> AuthCtrl["Auth Controller"]
    Router --> QuizCtrl["Quiz Controller"]
    Router --> OrderCtrl["Order & VietQR Controller"]
    Router --> AdminCtrl["Admin Controller"]
    
    AuthCtrl --> AuthSvc["Auth Service (Bcrypt, JWT Rotation)"]
    QuizCtrl --> QuizSvc["Quiz Service (Anti-Cheat, Server Grading)"]
    OrderCtrl --> OrderSvc["Order Service (VietQR, HMAC Webhook)"]
    AdminCtrl --> AdminSvc["Admin & Analytics Service"]
    
    AuthSvc --> ORM["SQLAlchemy 2.0 Async ORM"]
    QuizSvc --> ORM
    OrderSvc --> ORM
    AdminSvc --> ORM
    
    ORM --> NeonDB[("Neon PostgreSQL Serverless (SSL Encrypted)")]
```

---

### 2. HƯỚNG DẪN CÀI ĐẶT VÀ KHỞI CHẠY

#### 2.1. Yêu cầu môi trường
* **Python**: Phiên bản `3.10` trở lên (Khuyến nghị Python 3.12 - 3.14).
* **Trình quản lý gói**: `pip`.

#### 2.2. Các bước cài đặt
Di chuyển vào thư mục backend và cài đặt các thư viện cần thiết:
```bash
cd "c:\Users\cp\Downloads\New folder (3)\apti-backend"
python -m pip install -r requirements.txt
```

#### 2.3. Khởi động máy chủ API
Có 2 cách khởi động:

* **Cách 1 (Khuyên dùng)**: Chạy qua script [run.py](file:///c:/Users/cp/Downloads/New%20folder%20(3)/apti-backend/run.py):
```bash
python run.py
```

* **Cách 2**: Chạy trực tiếp bằng `uvicorn`:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Khi khởi động thành công, terminal sẽ thông báo:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process
2026-10-28 [INFO] apti.main - Đang khởi động APTI - Aptitude Test Tiếng Việt v1.0.0...
2026-10-28 [INFO] apti.main - Cơ sở dữ liệu đã sẵn sàng và đồng bộ hóa các bảng thành công.
2026-10-28 [INFO] apti.seed - Hoàn tất khởi tạo dữ liệu mặc định thành công.
```

#### 2.4. Các đường dẫn truy cập quan trọng
| Công cụ | Đường dẫn URL | Chức năng |
| :--- | :--- | :--- |
| **Trang chủ API** | `http://localhost:8000/` | Trả về thông tin phiên bản và tình trạng máy chủ |
| **Swagger UI** | `http://localhost:8000/docs` | Giao diện thử nghiệm API tương tác trực tiếp (Interactive Documentation) |
| **ReDoc** | `http://localhost:8000/redoc` | Tài liệu đặc tả kỹ thuật chi tiết theo chuẩn OpenAPI 3.1 |
| **Health Check** | `http://localhost:8000/api/v1/health` | Đo độ trễ (latency ms) và tình trạng kết nối tới database |

---

### 3. HƯỚNG DẪN CẤU HÌNH NEON POSTGRESQL CHI TIẾT

Hệ thống được thiết kế tối ưu riêng biệt cho **Neon PostgreSQL Serverless**:

#### Bước 1: Đăng ký và tạo Project trên Neon
1. Mở trình duyệt truy cập: [https://console.neon.tech](https://console.neon.tech)
2. Đăng ký tài khoản (qua GitHub, Google hoặc Email).
3. Nhấp vào **"Create Project"**:
   - **Project Name**: `apti-database`
   - **Postgres Version**: `16` hoặc `17`
   - **Region**: Chọn `AWS Singapore (ap-southeast-1)` hoặc `AWS US East (Ohio)` để có độ trễ tối ưu.
4. Nhấp **Create Project**.

#### Bước 2: Sao chép chuỗi kết nối (Connection String)
Tại giao diện **Dashboard của Project**:
1. Chọn mục **Connection Details**.
2. Chọn loại kết nối: **Pooled connection** (khuyên dùng) hoặc **Direct connection**.
3. Chọn ngôn ngữ/driver: **Python** hoặc **PostgreSQL**.
4. Chuỗi kết nối có định dạng tương tự:
   ```
   postgresql://neondb_owner:AbCd1234EfGh@ep-sweet-glade-a5b6c7d8-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

#### Bước 3: Cấu hình vào file `.env`
Mở file [apti-backend/.env](file:///c:/Users/cp/Downloads/New%20folder%20(3)/apti-backend/.env), tìm đến dòng `DATABASE_URL` và đổi giao thức thành `postgresql+asyncpg://`:
```env
# Đổi tiền tố thành postgresql+asyncpg:// và giữ nguyên tham số ?ssl=require
DATABASE_URL=postgresql+asyncpg://neondb_owner:AbCd1234EfGh@ep-sweet-glade-a5b6c7d8-pooler.us-east-2.aws.neon.tech/neondb?ssl=require
```

#### Bước 4: Khởi động lại Server
Khi server khởi chạy lại, SQLAlchemy sẽ tự động kết nối Neon qua kênh mã hóa SSL và đồng bộ toàn bộ bảng dữ liệu vào Neon PostgreSQL.

> [!NOTE]
> **Cơ chế Fallback an toàn:** Nếu bạn chưa có kết nối Internet hoặc chưa có tài khoản Neon, hệ thống sẽ sử dụng SQLite Async nội bộ (`sqlite+aiosqlite:///./apti.db`) để bạn kiểm thử các chức năng hoàn toàn bình thường mà không bị gián đoạn.

---

### 4. TÀI KHOẢN MẶC ĐỊNH VÀ PHÂN QUYỀN HỆ THỐNG (RBAC)

Khi máy chủ khởi động lần đầu, trình seeder tự động nạp sẵn 2 tài khoản mẫu:

| Loại tài khoản | Email đăng nhập | Mật khẩu mặc định | Vai trò & Quyền hạn |
| :--- | :--- | :--- | :--- |
| **Quản trị viên (Admin)** | `admin@apti.vn` | `Apti@2026Admin!` | Toàn quyền xem thống kê dashboard, thêm/sửa/xóa câu hỏi, quản lý người dùng, duyệt đơn hàng |
| **Học viên mẫu (Student)** | `student@apti.vn` | `Student@2026!` | Quyền học viên (làm đề thi mẫu, xem lịch sử làm bài, mua gói nâng cấp) |

#### Bảng ma trận phân quyền (Access Matrix):
| Chức năng | Khách vãng lai (Guest) | Học viên miễn phí | Học viên có gói (7d/30d) | Quản trị viên (Admin) |
| :--- | :---: | :---: | :---: | :---: |
| Xem danh mục & giới thiệu đề thi |  |  |  |  |
| Làm đề thi mẫu cơ bản (max 5 câu) |  |  |  |  |
| Lưu lịch sử tiến độ & thi thử Mock Test | ❌ |  |  |  |
| Xem ngân hàng câu hỏi nâng cao (600+ câu) | ❌ | ❌ |  |  |
| Tải Ebook chuyên sâu PDF | ❌ | ❌ |  |  |
| Xem Dashboard quản trị & Doanh thu | ❌ | ❌ | ❌ |  |

---

### 5. HƯỚNG DẪN CHI TIẾT CÁC PHÂN HỆ API

#### 5.1. Phân hệ Xác thực & Bảo mật (`/api/v1/auth`)

##### 1. Đăng ký tài khoản (`POST /api/v1/auth/register`)
* **Mô tả**: Tạo tài khoản học viên mới. Mật khẩu phải đáp ứng chính sách bảo mật nghiêm ngặt.
* **Payload yêu cầu**:
```json
{
  "email": "nguyenvana@gmail.com",
  "full_name": "Nguyễn Văn A",
  "password": "Password@2026!",
  "phone": "0988123456"
}
```
* **Chính sách mật khẩu (Password Strength)**:
  - Tối thiểu 8 ký tự.
  - Ít nhất 1 chữ in hoa (`A-Z`).
  - Ít nhất 1 chữ in thường (`a-z`).
  - Ít nhất 1 chữ số (`0-9`).
  - Ít nhất 1 ký tự đặc biệt (`!@#$%^&*...`).

##### 2. Đăng nhập (`POST /api/v1/auth/login`)
* **Mô tả**: Xác thực người dùng, trả về Access Token và Refresh Token.
* **Cơ chế chống Brute-Force**: Nhập sai mật khẩu liên tiếp 5 lần sẽ kích hoạt trạng thái khóa tài khoản trong 15 phút (`HTTP 423 Locked`).
* **Payload**:
```json
{
  "email": "nguyenvana@gmail.com",
  "password": "Password@2026!"
}
```
* **Phản hồi mẫu**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "uR8x1...token_urlsafe...",
  "token_type": "bearer",
  "expires_in_seconds": 3600,
  "user": {
    "id": 1,
    "email": "nguyenvana@gmail.com",
    "full_name": "Nguyễn Văn A",
    "role": "USER",
    "subscription_tier": "FREE",
    "has_active_subscription": false
  }
}
```

##### 3. Làm mới Token (`POST /api/v1/auth/refresh`)
* **Mô tả**: Sử dụng `refresh_token` để nhận `access_token` mới khi token cũ hết hạn (Token Rotation). Refresh token cũ sẽ lập tức bị thu hồi để chống đánh cắp phiên.

##### 4. Đăng xuất (`POST /api/v1/auth/logout`)
* **Mô tả**: Hủy bỏ phiên đăng nhập và thu hồi toàn bộ Refresh Token của tài khoản. Yêu cầu Header `Authorization: Bearer <access_token>`.

##### 5. Xem & Cập nhật Hồ sơ cá nhân (`GET` & `PUT /api/v1/auth/me`)
* **Mô tả**: Lấy thông tin tài khoản, avatar, ngày hết hạn gói học đang kích hoạt.

---

#### 5.2. Phân hệ Luyện thi & Đánh giá năng lực (`/api/v1/quiz`)

##### 1. Lấy danh mục dạng đề thi (`GET /api/v1/quiz/categories`)
* Trả về danh sách: `Số học (numerical)`, `Logic (logical)`, `Ngôn ngữ (verbal)`, `Hình ảnh (abstract)` kèm số lượng câu hỏi hiện có.

##### 2. Lấy danh sách câu hỏi làm bài (`GET /api/v1/quiz/questions`)
* **Query Params**:
  - `category_id`: `numerical` | `logical` | `verbal` | `abstract` (hoặc bỏ trống để lấy ngẫu nhiên hỗn hợp).
  - `mode`: `PRACTICE` | `MOCK_EXAM`.
  - `limit`: Số câu hỏi (mặc định 10).
* **BẢO MẬT ĐỀ THI ĐẶC BIỆT**: API tuyệt đối **không trả về** trường `correct_index` hay `explanation`. Dù học viên bấm `F12` kiểm tra gói tin HTTP cũng không thể thấy trước đáp án.

##### 3. Nộp bài và Chấm điểm trên Server (`POST /api/v1/quiz/submit`)
* **Payload nộp bài**:
```json
{
  "category_id": "numerical",
  "mode": "PRACTICE",
  "time_spent_seconds": 125,
  "answers": [
    { "question_id": 1, "selected_index": 1 },
    { "question_id": 2, "selected_index": 0 }
  ]
}
```
* **Phản hồi**:
  - Tỷ lệ phần trăm điểm số (`score_percentage`).
  - Phân tích điểm theo từng dạng câu hỏi (Ví dụ: Số học 100%, Logic 50%).
  - Lời giải chi tiết từng bước bằng tiếng Việt, đáp án đúng và mẹo giải nhanh từ cựu MT.
  - Lời thoại khích lệ động viên từ linh vật **Em Tee** được điều chỉnh tương ứng với thang điểm của bạn.

##### 4. Xem lịch sử làm bài (`GET /api/v1/quiz/history`)
* Dành cho học viên đã đăng nhập, theo dõi biểu đồ tiến bộ điểm số qua từng ngày.

##### 5. Bảng xếp hạng (`GET /api/v1/quiz/leaderboard`)
* Tôn vinh top 10 học viên có thành tích giải đề xuất sắc nhất.

---

#### 5.3. Phân hệ Gói học, Đơn hàng & VietQR (`/api/v1/plans` & `/api/v1/orders`)

##### 1. Danh sách gói học (`GET /api/v1/plans`)
* Trả về các gói:
  - **Gói 7 Ngày** (Khởi động): `99.000 VNĐ`
  - **Gói 30 Ngày** (Chinh phục MT): `249.000 VNĐ`

##### 2. Tạo đơn hàng thanh toán VietQR (`POST /api/v1/orders/checkout`)
* **Payload**:
```json
{
  "plan_id": "master-30d",
  "payment_method": "VIETQR"
}
```
* **Phản hồi**: Hệ thống tự động tạo mã đơn hàng duy nhất dạng `APTI-20261028-XXXX`, kèm đường link ảnh mã QR chuẩn Napas 24/7 và thông tin chuyển khoản chính xác:
```json
{
  "data": {
    "id": "APTI-20261028-8C4F1A",
    "plan_name": "Gói 30 Ngày",
    "amount_vnd": 249000,
    "qr_payment_url": "https://img.vietqr.io/image/MB-982601289999-compact2.png?amount=249000&addInfo=APTI%20APTI-20261028-8C4F1A...",
    "bank_info": {
      "bank_name": "MB Bank (Ngân hàng Quân Đội)",
      "account_number": "982601289999",
      "account_holder": "CONG TY TNHH APTI VIET NAM",
      "transfer_content": "APTI APTI-20261028-8C4F1A"
    }
  }
}
```

##### 3. Giả lập thanh toán thành công trong môi trường Dev (`POST /api/v1/orders/{order_id}/simulate-success`)
* Tiện ích dành riêng cho đội ngũ phát triển và kiểm thử: Nhấp một nút để giả lập đơn hàng đã chuyển khoản thành công. Hệ thống sẽ tự động cộng thêm số ngày tương ứng vào tài khoản học viên.

##### 4. Webhook xác nhận thanh toán (`POST /api/v1/orders/webhook`)
* Cổng tiếp nhận callback từ ngân hàng/cổng thanh toán.
* **Bắt buộc xác thực chữ ký số HMAC-SHA256**: Ngăn chặn kẻ xấu giả mạo thông báo thanh toán thành công để mở khóa gói học trái phép.

---

#### 5.4. Phân hệ Tài liệu & Ebook (`/api/v1/documents`)

* `GET /api/v1/documents`: Danh sách tài liệu luyện thi. Trường `can_access` sẽ tự động trả về `true` hoặc `false` tùy thuộc vào việc tài khoản người dùng đã nâng cấp gói hay chưa.
* `GET /api/v1/documents/{id}/download-link`: Cấp link tải an toàn, kiểm tra quyền sở hữu trước khi cho phép tải tệp PDF bản quyền.

---

#### 5.5. Phân hệ Quản trị viên (`/api/v1/admin`)

* `GET /api/v1/admin/stats`: Báo cáo thống kê toàn diện theo thời gian thực:
  - Tổng số người dùng đăng ký.
  - Số lượng học viên đang có gói trả phí hoạt động.
  - Tổng doanh thu (VNĐ).
  - Tổng số lượt nộp bài trắc nghiệm và điểm số trung bình toàn hệ thống.
  - Trạng thái kết nối cơ sở dữ liệu Neon.
* `GET /api/v1/admin/users`: Danh sách học viên có phân trang, tìm kiếm theo tên hoặc email.
* `PUT /api/v1/admin/users/{user_id}`: Khóa/mở khóa tài khoản học viên, thay đổi quyền hạn hoặc tặng thêm ngày sử dụng gói học.

---

### 6. HƯỚNG DẪN MIGRATION CƠ SỞ DỮ LIỆU (ALEMBIC)

Khi bạn bổ sung hoặc thay đổi cột trong các tệp model tại `app/models/`:

1. **Tạo bản migration mới tự động**:
```bash
cd "c:\Users\cp\Downloads\New folder (3)\apti-backend"
python -m alembic revision --autogenerate -m "ten_thay_doi_moi"
```
2. **Nâng cấp database lên bản mới nhất**:
```bash
python -m alembic upgrade head
```
3. **Quay lui về phiên bản trước (nếu cần rollback)**:
```bash
python -m alembic downgrade -1
```

---

### 7. HƯỚNG DẪN CHẠY KIỂM THỬ TỰ ĐỘNG (PYTEST)

Toàn bộ các luồng nghiệp vụ nhạy cảm đều có bộ kiểm thử tự động tại thư mục [tests/](file:///c:/Users/cp/Downloads/New%20folder%20(3)/apti-backend/tests/):

Chạy lệnh kiểm thử:
```bash
cd "c:\Users\cp\Downloads\New folder (3)\apti-backend"
python -m pytest tests -v
```

**Chi tiết các ca kiểm thử bảo mật đã chạy thành công (100% Passed)**:
1. `test_register_and_login`: Kiểm tra từ chối mật khẩu yếu và đăng nhập thành công cấp đủ JWT token.
2. `test_brute_force_lockout`: Kiểm tra cơ chế tự động khóa tài khoản sau 5 lần nhập sai liên tiếp.
3. `test_quiz_integrity_no_answer_leak`: Đảm bảo API trả câu hỏi thi không chứa đáp án để chống F12 gian lận.
4. `test_quiz_submission_and_grading`: Kiểm tra quy trình nộp bài, tính điểm và lời thoại linh vật Em Tee.
5. `test_owasp_security_headers`: Kiểm tra đầy đủ các Header bảo mật (CSP, HSTS, X-Frame-Options, Nosniff).
6. `test_health_check`: Kiểm tra độ sống của kết nối cơ sở dữ liệu.

---

### 8. BẢNG MÃ LỖI VÀ XỬ LÝ SỰ CỐ THƯỜNG GẶP (TROUBLESHOOTING)

| Mã lỗi HTTP | Nguyên nhân | Cách khắc phục |
| :--- | :--- | :--- |
| **`401 Unauthorized`** | Token không tồn tại, hết hạn, hoặc mật khẩu đăng nhập không đúng. | Đăng nhập lại hoặc gọi API `/api/v1/auth/refresh` với Refresh Token. |
| **`423 Locked`** | Tài khoản bị tạm khóa do nhập sai mật khẩu 5 lần liên tiếp. | Chờ hết 15 phút đếm ngược hoặc nhờ Admin mở khóa trong `/api/v1/admin/users`. |
| **`429 Too Many Requests`** | Gửi quá số lượng yêu cầu cho phép trong 1 phút (Rate Limit). | Kiểm tra header `Retry-After` trong response để biết số giây cần chờ trước khi thử lại. |
| **`403 Forbidden`** | Người dùng cố tình truy cập tài liệu/tính năng chỉ dành cho Gói học trả phí hoặc Admin. | Mua gói 7 Ngày / 30 Ngày hoặc đăng nhập bằng tài khoản Quản trị viên. |
| **`422 Unprocessable Entity`** | Dữ liệu gửi lên không đúng định dạng Pydantic (ví dụ mật khẩu thiếu chữ hoa, số). | Đọc chi tiết lỗi trong mảng `detail` trả về để chỉnh sửa payload đúng định dạng. |
| **`Neon Database Sleep`** | Neon Serverless tự đưa compute endpoint về trạng thái Sleep sau thời gian không hoạt động. | Hệ thống đã có cơ chế `pool_pre_ping=True` tự động đánh thức endpoint trong 1-2 giây đầu tiên. |

