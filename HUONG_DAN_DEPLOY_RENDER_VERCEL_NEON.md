# HƯỚNG DẪN TRIỂN KHAI TOÀN DIỆN (DEPLOYMENT GUIDE)
## BACKEND (RENDER) • FRONTEND (VERCEL) • DATABASE (NEON POSTGRESQL)
**Nền tảng:** APTI – Luyện Aptitude Test Tiếng Việt cho Người Mới Bắt Đầu Management Trainee

---

### MỤC LỤC
1. [KIẾN TRÚC TRIỂN KHAI ĐÁM MÂY (DEPLOYMENT ARCHITECTURE)](#1-kiến-trúc-triển-khai-đám-mây-deployment-architecture)
2. [BƯỚC 1: KHỞI TẠO CƠ SỞ DỮ LIỆU NEON POSTGRESQL](#2-bước-1-khởi-tạo-cơ-sở-dữ-liệu-neon-postgresql)
3. [BƯỚC 2: TRIỂN KHAI BACKEND FASTAPI LÊN RENDER](#3-bước-2-triển-khai-backend-fastapi-lên-render)
4. [BƯỚC 3: TRIỂN KHAI FRONTEND LÊN VERCEL](#4-bước-3-triển-khai-frontend-lên-vercel)
5. [BƯỚC 4: KẾT NỐI VÀ CẤU HÌNH CORS GIỮA HAI BÊN](#5-bước-4-kết-nối-và-cấu-hình-cors-giữa-hai-bên)
6. [BƯỚC 5: KIỂM THỬ VÀ NGHIỆM THU HỆ THỐNG TRÊN MÔI TRƯỜNG THẬT](#6-bước-5-kiểm-thử-và-nghiệm-thu-hệ-thống-trên-môi-trường-thật)
7. [BẢNG XỬ LÝ SỰ CỐ THƯỜNG GẶP (TROUBLESHOOTING)](#7-bảng-xử-lý-sự-cố-thường-gặp-troubleshooting)

---

### 1. KIẾN TRÚC TRIỂN KHAI ĐÁM MÂY (DEPLOYMENT ARCHITECTURE)

Hệ thống **APTI** được thiết kế theo mô hình tách biệt (*Decoupled Modern Cloud Architecture*) giúp tối ưu hiệu năng, giảm chi phí lưu trữ (0đ với các gói Free Tier) và đảm bảo an toàn dữ liệu:

```mermaid
flowchart LR
    User["Học viên MT (Trình duyệt Web / Mobile)"] -->|HTTPS (Edge CDN)| Vercel["Frontend trên VERCEL<br>(apti-frontend/)<br>• HTML5 / CSS3 / ES Modules<br>• VietQR Napas 24/7 Flow<br>• Dual-Mode Client"]
    
    Vercel -->|REST API / Bearer JWT| Render["Backend trên RENDER<br>(apti-backend/)<br>• FastAPI + Uvicorn<br>• OWASP Top 10 Security<br>• Anti-Cheat Quiz Engine<br>• Port Auto-Binding"]
    
    Render -->|SSL Encrypted / asyncpg| Neon[("Database trên NEON<br>PostgreSQL Serverless<br>• Auto-Scaling Compute<br>• Connection Pooling<br>• 0.5 GiB Storage Free")]
```

| Thành phần | Nền tảng Cloud | Vai trò & Đặc điểm |
| :--- | :--- | :--- |
| **Cơ sở dữ liệu** | **Neon PostgreSQL** | Cơ sở dữ liệu quan hệ Serverless, tự động co giãn, hỗ trợ SSL bắt buộc, kết nối qua `asyncpg`. |
| **Máy chủ API** | **Render.com** | Máy chủ Python Web Service chạy FastAPI, tự động chạy migration Alembic và nạp dữ liệu mẫu khi deploy. |
| **Giao diện Web** | **Vercel** | Mạng phân phối nội dung toàn cầu (Global Edge CDN), tự động nén tài nguyên, hỗ trợ Clean URLs. |

---

### 2. BƯỚC 1: KHỞI TẠO CƠ SỞ DỮ LIỆU NEON POSTGRESQL

#### 2.1. Đăng ký & Tạo Project
1. Truy cập [https://console.neon.tech](https://console.neon.tech) và đăng nhập (bằng tài khoản GitHub hoặc Google).
2. Nhấp vào nút **"Create Project"**:
   - **Project Name**: `apti-database`
   - **Postgres version**: Chọn bản mới nhất (`Postgres 16` hoặc `17`).
   - **Region**: Khuyến nghị chọn `AWS Singapore (ap-southeast-1)` để có độ trễ kết nối từ Việt Nam thấp nhất (< 40ms).
3. Nhấp **"Create Project"**.

#### 2.2. Lấy chuỗi kết nối (Connection String)
1. Tại trang **Dashboard**, tìm phần **Connection Details**.
2. Đánh dấu chọn **"Pooled connection"** (chế độ tối ưu cho Serverless FastAPI).
3. Chọn ngôn ngữ/driver: **Python** hoặc **asyncpg**.
4. Bạn sẽ nhận được chuỗi kết nối có dạng:
   ```
   postgresql://neondb_owner:npg_AbCd1234EfGh@ep-sweet-glade-a5b6c7d8-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
   ```
5. **Lưu ý quan trọng**: Giữ nguyên chuỗi này để nhập vào Render ở Bước 2. Hệ thống APTI Backend đã có hàm `normalize_database_url` tự động chuẩn hóa giao thức thành `postgresql+asyncpg://` và cấu hình SSL `require` mà bạn không cần phải sửa tay!

---

### 3. BƯỚC 2: TRIỂN KHAI BACKEND FASTAPI LÊN RENDER

Render cung cấp 2 cách triển khai: **Cách 1: Triển khai thủ công qua Web Dashboard** (dễ thao tác cho người mới) hoặc **Cách 2: Triển khai tự động bằng Blueprint `render.yaml`**.

#### Cách 1: Triển khai qua Web Dashboard Render (Khuyên dùng)
1. Đăng nhập tại [https://dashboard.render.com](https://dashboard.render.com).
2. Nhấp nút **"New +"** ở góc trên cùng bên phải ➔ Chọn **"Web Service"**.
3. Chọn **"Build and deploy from a Git repository"** ➔ Kết nối với repository GitHub của bạn (`amobeardat-a11y/apt`).
4. Điền các thông số cấu hình chính xác như sau:

| Mục thiết lập | Giá trị cần điền | Giải thích |
| :--- | :--- | :--- |
| **Name** | `apti-backend` | Tên dịch vụ (URL sẽ là `https://apti-backend.onrender.com`) |
| **Region** | `Singapore (Southeast Asia)` | Đặt cùng Region với Neon DB để tốc độ tối đa |
| **Branch** | `main` | Nhánh code nguồn |
| **Root Directory** | `apti-backend` | **BẮT BUỘC:** Vì thư mục backend nằm trong thư mục con |
| **Runtime** | `Python 3` | Môi trường Python |
| **Build Command** | `pip install -r requirements.txt && python -m alembic upgrade head` | Cài đặt gói và tự động nâng cấp bảng Neon DB |
| **Start Command** | `python run.py` | Chạy FastAPI tự động nhận diện `$PORT` Render cấp |
| **Instance Type** | `Free` | Miễn phí 0đ/tháng |

5. **Thiết lập Biến Môi Trường (Environment Variables)**:
   Cuộn xuống mục **Advanced** ➔ Nhấp **"Add Environment Variable"** và thêm các biến sau:

```env
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://neondb_owner:YOUR_PASSWORD@ep-xyz-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
SECRET_KEY=apti-production-secret-key-64chars-random-replace-this-securely
BACKEND_CORS_ORIGINS=https://*.vercel.app,http://localhost:5500,http://127.0.0.1:5500
RATE_LIMIT_ENABLED=true
RATE_LIMIT_GENERAL_PER_MINUTE=120
RATE_LIMIT_AUTH_PER_MINUTE=15
PAYMENT_WEBHOOK_SECRET=apti-webhook-secret-key-neon-secure-2026
FIRST_SUPERUSER_EMAIL=admin@apti.vn
FIRST_SUPERUSER_PASSWORD=Apti@2026Admin!
FIRST_SUPERUSER_NAME=APTI Administrator
```

6. Nhấp **"Create Web Service"**.
   - Render sẽ bắt đầu cài đặt thư viện phụ thuộc, kết nối Neon, chạy migrations Alembic và nạp sẵn tài khoản Admin, câu hỏi mẫu, đề thi vào Neon PostgreSQL.
   - Khi hoàn tất, Render sẽ hiển thị trạng thái `Live` và cấp cho bạn một URL dạng:  
     👉 **`https://apti-backend-xxxx.onrender.com`**

#### Cách 2: Triển khai 1-Click bằng Blueprint `render.yaml`
Dự án đã có sẵn tệp cấu hình chuẩn [render.yaml](file:///c:/Users/cp/Downloads/New%20folder%20(3)/render.yaml):
1. Tại Dashboard Render ➔ Chọn **"New +"** ➔ **"Blueprint"**.
2. Chọn repository của bạn ➔ Render sẽ tự động đọc `render.yaml`, tự tạo biến bảo mật ngẫu nhiên `SECRET_KEY` và yêu cầu bạn nhập chuỗi `DATABASE_URL` của Neon.

---

### 4. BƯỚC 3: TRIỂN KHAI FRONTEND LÊN VERCEL

#### 4.1. Cập nhật URL Backend vào Frontend
Mở tệp [apti-frontend/js/config.js](file:///c:/Users/cp/Downloads/New%20folder%20(3)/apti-frontend/js/config.js), thay thế URL mặc định bằng domain Render bạn vừa nhận được ở Bước 2:
```javascript
// Thay đổi thành URL Render thực tế của bạn:
export const DEFAULT_PRODUCTION_API_URL = 'https://apti-backend-xxxx.onrender.com/api/v1';
```
*(Commit và push thay đổi này lên GitHub).*

#### 4.2. Các bước triển khai trên Vercel
1. Đăng nhập tại [https://vercel.com](https://vercel.com) (bằng tài khoản GitHub).
2. Tại trang **Overview**, nhấp nút **"Add New..."** ➔ Chọn **"Project"**.
3. Tìm repository `amobeardat-a11y/apt` ➔ Nhấp **"Import"**.
4. Cấu hình các mục quan trọng:
   - **Project Name**: `apti-frontend` (hoặc tên bạn muốn)
   - **Framework Preset**: Chọn `Other`
   - **Root Directory**: Nhấp nút **Edit** ➔ Chọn thư mục **`apti-frontend`** ➔ Nhấp **Continue**.
   - **Build and Output Settings**: Giữ mặc định (không cần nhập lệnh build vì tệp tĩnh đã sẵn sàng).
5. Nhấp nút **"Deploy"**.
   - Vercel sẽ tự động đọc tệp [vercel.json](file:///c:/Users/cp/Downloads/New%20folder%20(3)/apti-frontend/vercel.json), áp dụng các quy tắc bảo mật Header, tối ưu cache cho ảnh linh vật Em Tee và cấp domain dạng:  
     👉 **`https://apti-frontend.vercel.app`** (hoặc `https://apt-xxxx.vercel.app`).

---

### 5. BƯỚC 4: KẾT NỐI VÀ CẤU HÌNH CORS GIỮA HAI BÊN

Để Frontend Vercel gửi được yêu cầu API và JWT Token sang Backend Render mà không bị trình duyệt chặn CORS:

1. Trong [app/main.py](file:///c:/Users/cp/Downloads/New%20folder%20(3)/apti-backend/app/main.py), hệ thống đã cài đặt sẵn bộ lọc linh hoạt:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=settings.BACKEND_CORS_ORIGINS,
       allow_origin_regex=r"^https://.*\.vercel\.app$",
       allow_credentials=True,
       allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
       allow_headers=["*"],
       expose_headers=["X-Process-Time-Ms", "Retry-After"]
   )
   ```
   *Biểu thức `allow_origin_regex` cho phép **mọi nhánh preview deployment và domain chính thức trên Vercel** đều kết nối được ngay lập tức!*
2. Nếu bạn dùng Custom Domain riêng (ví dụ `https://apti.vn`):
   - Vào Dashboard Render ➔ Chọn Service `apti-backend` ➔ Mục **Environment**.
   - Thêm domain vào biến `BACKEND_CORS_ORIGINS`:
     ```env
     BACKEND_CORS_ORIGINS=https://apti.vn,https://*.vercel.app,http://localhost:5500
     ```
   - Nhấp **"Save Changes"** để Render tự động cập nhật.

---

### 6. BƯỚC 5: KIỂM THỬ VÀ NGHIỆM THU HỆ THỐNG TRÊN MÔI TRƯỜNG THẬT

Sau khi hoàn tất triển khai cả 3 dịch vụ, hãy kiểm tra danh sách nghiệm thu:

- [x] **Kiểm tra Health Check API**:  
  Truy cập `https://apti-backend.onrender.com/api/v1/health`.  
  Phản hồi mong đợi: `{"status": "UP", "database": {"status": "HEALTHY", "target": "Neon PostgreSQL Serverless"}}`.
- [x] **Kiểm tra Tài liệu Swagger UI**:  
  Truy cập `https://apti-backend.onrender.com/docs`.
- [x] **Kiểm tra Trang chủ Frontend Vercel**:  
  Mở trang `https://apti-frontend.vercel.app`, linh vật Em Tee 3D hiển thị sắc nét, không bị lỗi viền phông.
- [x] **Kiểm tra Đăng nhập & Xác thực**:  
  Bấm nút **Đăng nhập** trên thanh Menu ➔ Bấm nút điền nhanh **"Học viên: student@apti.vn"** ➔ Đăng nhập thành công, thanh menu chuyển sang hiển thị tên học viên và gói học.
- [x] **Kiểm tra Đề thi & Chấm điểm Server**:  
  Cuộn xuống phần **Luyện đề trực tuyến**, trả lời câu hỏi và bấm **Nộp bài thi**. Hệ thống gửi lên Backend Render chấm điểm, trả về tỷ lệ phần trăm và lời thoại động viên của Em Tee.
- [x] **Kiểm tra Thanh toán VietQR Napas 24/7**:  
  Chọn Gói 30 Ngày ➔ Popup hiển thị ảnh mã VietQR MB Bank sắc nét ➔ Bấm nút **"Kích hoạt thử nghiệm ngay (Dev Sim)"** ➔ Tài khoản lập tức được nâng cấp lên hạng **MT Master**!

---

### 7. BẢNG XỬ LÝ SỰ CỐ THƯỜNG GẶP (TROUBLESHOOTING)

| Tình huống / Triệu chứng | Nguyên nhân kỹ thuật | Hướng khắc phục nhanh |
| :--- | :--- | :--- |
| **Lần đầu tải trang API trên Render mất 40-50 giây** | Gói Free Tier của Render tự động đưa ứng dụng về chế độ "Ngủ" (Spin down) nếu sau 15 phút không có lượt truy cập. | Đây là cơ chế tiết kiệm tài nguyên của Render Free. Khi có yêu cầu mới, Render sẽ tự khởi động lại. Muốn giữ ấm 24/7, có thể dùng dịch vụ miễn phí như **UptimeRobot** hoặc **cron-job.org** ping URL `/api/v1/health` mỗi 10 phút. |
| **Lỗi `TypeError: can't compare offset-naive and offset-aware datetimes`** | Database trả về trường datetime không kèm thông tin múi giờ. | Đã được xử lý triệt để trong mã nguồn thông qua hàm `ensure_utc()`. |
| **Lỗi CORS trên Vercel `Access-Control-Allow-Origin missing`** | Tên miền Vercel chưa được cấp phép trong danh sách CORS của Backend. | Thêm domain Vercel vào biến `BACKEND_CORS_ORIGINS` trên Render hoặc kiểm tra `allow_origin_regex` trong `main.py`. |
| **Neon báo lỗi `connection limit exceeded`** | Neon Serverless giới hạn số lượng kết nối trực tiếp đồng thời trên gói Free. | Đảm bảo chuỗi kết nối sử dụng endpoint có hậu tố **`-pooler`** (Pooled Connection) và thiết lập `pool_recycle=300`. |
| **Frontend báo `Chế độ Offline`** | Backend Render đang khởi động hoặc chưa điền đúng URL Render trong `config.js`. | Kiểm tra lại biến `DEFAULT_PRODUCTION_API_URL` trong [js/config.js](file:///c:/Users/cp/Downloads/New%20folder%20(3)/apti-frontend/js/config.js) và đảm bảo Backend Render có trạng thái `Live`. |

