import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

sys.stdout.reconfigure(encoding='utf-8')

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, start=150, end=150):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', start), ('right', end)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_callout(doc, text, title="LƯU Ý QUAN TRỌNG", bg_hex="F0EFFF", border_color="5348CD"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.rows[0].cells[0]
    cell.width = Inches(6.5)
    set_cell_background(cell, bg_hex)
    set_cell_margins(cell, top=140, bottom=140, start=200, end=200)
    
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>'
        f'  <w:top w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    run_title = p.add_run(f"📌 {title}: ")
    run_title.font.name = "Segoe UI"
    run_title.font.bold = True
    run_title.font.size = Pt(10.5)
    run_title.font.color.rgb = RGBColor(83, 72, 205)
    
    run_text = p.add_run(text)
    run_text.font.name = "Segoe UI"
    run_text.font.size = Pt(10)
    run_text.font.color.rgb = RGBColor(50, 50, 60)
    
    # spacing after table
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

def add_code_block(doc, code_str):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.rows[0].cells[0]
    cell.width = Inches(6.5)
    set_cell_background(cell, "2D3142")
    set_cell_margins(cell, top=120, bottom=120, start=180, end=180)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(code_str)
    run.font.name = "Consolas"
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(230, 240, 255)
    
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

def format_row(row, bg_hex, text_color, bold=False, font_size=10):
    for cell in row.cells:
        set_cell_background(cell, bg_hex)
        set_cell_margins(cell, top=100, bottom=100, start=140, end=140)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        for p in cell.paragraphs:
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            for r in p.runs:
                r.font.name = "Segoe UI"
                r.font.size = Pt(font_size)
                r.font.bold = bold
                r.font.color.rgb = text_color

def create_document():
    doc = docx.Document()
    
    # Page Margins
    for sec in doc.sections:
        sec.top_margin = Inches(0.8)
        sec.bottom_margin = Inches(0.8)
        sec.left_margin = Inches(0.8)
        sec.right_margin = Inches(0.8)
        sec.header.is_linked_to_previous = False
        p_hdr = sec.header.paragraphs[0]
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_hdr = p_hdr.add_run("APTI • Hướng Dẫn Triển Khai Cloud: Render - Vercel - Neon")
        r_hdr.font.name = "Segoe UI"
        r_hdr.font.size = Pt(8.5)
        r_hdr.font.color.rgb = RGBColor(160, 160, 175)

    # Document Header / Banner
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(4)
    r_t = p_title.add_run("HƯỚNG DẪN TRIỂN KHAI TOÀN DIỆN (DEPLOYMENT GUIDE)\n")
    r_t.font.name = "Segoe UI"
    r_t.font.size = Pt(18)
    r_t.font.bold = True
    r_t.font.color.rgb = RGBColor(83, 72, 205) # #5348CD Indigo Pop

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(8)
    r_s = p_sub.add_run("BACKEND (RENDER) • FRONTEND (VERCEL) • DATABASE (NEON POSTGRESQL)\n")
    r_s.font.name = "Segoe UI"
    r_s.font.size = Pt(12)
    r_s.font.bold = True
    r_s.font.color.rgb = RGBColor(245, 72, 153) # #F54899 Hot Pink

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_before = Pt(0)
    p_meta.paragraph_format.space_after = Pt(16)
    r_m = p_meta.add_run("Nền tảng: APTI – Luyện Aptitude Test Tiếng Việt cho Người Mới Bắt Đầu Management Trainee\nTháng 11/2026 • Kiến trúc Đám mây Serverless & Edge CDN 0đ/tháng")
    r_m.font.name = "Segoe UI"
    r_m.font.size = Pt(9.5)
    r_m.font.italic = True
    r_m.font.color.rgb = RGBColor(110, 110, 130)

    # Divider
    p_div = doc.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_div.paragraph_format.space_after = Pt(14)
    r_div = p_div.add_run("━" * 55)
    r_div.font.color.rgb = RGBColor(210, 210, 230)

    def add_h1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(16)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = "Segoe UI"
        r.font.size = Pt(13.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(83, 72, 205)
        return h

    def add_h2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = "Segoe UI"
        r.font.size = Pt(11.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(31, 169, 122) # #1FA97A Mint
        return h

    def add_body(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.2
        r = p.add_run(text)
        r.font.name = "Segoe UI"
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(40, 40, 50)
        return p

    def add_bullet(text, level=0):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.left_indent = Inches(0.25 * (level + 1))
        r = p.add_run(text)
        r.font.name = "Segoe UI"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(40, 40, 50)
        return p

    # Section 1
    add_h1("1. KIẾN TRÚC TRIỂN KHAI ĐÁM MÂY (DEPLOYMENT ARCHITECTURE)")
    add_body(
        "Hệ thống APTI được thiết kế theo mô hình tách biệt (Decoupled Modern Cloud Architecture) "
        "giúp tối ưu hiệu năng, giảm chi phí lưu trữ (hoàn toàn 0đ với các gói Free Tier) và bảo mật tuyệt đối:"
    )

    t1 = doc.add_table(rows=4, cols=3)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    t1.autofit = False
    col_widths = [Inches(1.8), Inches(1.8), Inches(2.9)]
    
    headers = ["Thành phần", "Nền tảng Cloud", "Vai trò & Đặc điểm kỹ thuật"]
    for i, title in enumerate(headers):
        cell = t1.rows[0].cells[i]
        cell.width = col_widths[i]
        cell.paragraphs[0].text = title
    format_row(t1.rows[0], "5348CD", RGBColor(255, 255, 255), bold=True, font_size=10)

    rows_data = [
        ("Cơ sở dữ liệu", "Neon PostgreSQL Serverless", "Cơ sở dữ liệu quan hệ Serverless, tự động scale compute, hỗ trợ SSL bắt buộc, kết nối qua asyncpg, dung lượng 0.5 GiB free."),
        ("Máy chủ API", "Render.com Web Service", "Máy chủ Python Web Service chạy FastAPI + Uvicorn, tự động kích hoạt Alembic migrations và seed data khi khởi động."),
        ("Giao diện Web", "Vercel Edge Platform", "Mạng phân phối nội dung toàn cầu (Global Edge CDN), tự động nén tài nguyên gzip/brotli, hỗ trợ Clean URLs, latency cực thấp.")
    ]
    for row_idx, r_data in enumerate(rows_data):
        row = t1.rows[row_idx + 1]
        for col_idx, text in enumerate(r_data):
            cell = row.cells[col_idx]
            cell.width = col_widths[col_idx]
            cell.paragraphs[0].text = text
        bg = "FFFFFF" if row_idx % 2 == 0 else "F8F6FA"
        format_row(row, bg, RGBColor(40, 40, 50), bold=(col_idx==0), font_size=9.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Section 2
    add_h1("2. BƯỚC 1: KHỞI TẠO CƠ SỞ DỮ LIỆU NEON POSTGRESQL")
    add_h2("2.1. Đăng ký & Tạo Project trên Neon")
    add_bullet("Truy cập https://console.neon.tech và đăng nhập thuận tiện bằng tài khoản GitHub hoặc Google.")
    add_bullet("Nhấp vào nút \"Create Project\":")
    add_bullet("Project Name: Đặt tên gợi nhớ, ví dụ: apti-database.", level=1)
    add_bullet("Postgres version: Chọn bản mới nhất (Postgres 16 hoặc 17).", level=1)
    add_bullet("Region: KHUYẾN NGHỊ chọn AWS Singapore (ap-southeast-1) để đạt độ trễ từ Việt Nam < 40ms.", level=1)
    add_bullet("Nhấp \"Create Project\" để Neon khởi tạo cụm Serverless trong vài giây.")

    add_h2("2.2. Lấy chuỗi kết nối (Connection String)")
    add_bullet("Tại trang Dashboard của Project, tìm mục Connection Details.")
    add_bullet("Đánh dấu chọn mục \"Pooled connection\" (chế độ tối ưu hóa cực đại cho Serverless và FastAPI).")
    add_bullet("Chọn ngôn ngữ/driver: Python hoặc asyncpg.")
    add_bullet("Sao chép chuỗi kết nối chuẩn có định dạng như sau:")
    add_code_block(doc, "postgresql://neondb_owner:npg_AbCd1234EfGh@ep-sweet-glade-a5b6c7d8-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require")
    add_callout(
        doc,
        "Backend của APTI đã tích hợp sẵn hàm chuẩn hóa normalize_database_url() tự động nhận diện tham số sslmode=require của Neon và chuyển đổi thành dạng kết nối tương thích với asyncpg: postgresql+asyncpg://... với connect_args={'ssl': 'require'}. Bạn chỉ cần copy nguyên văn chuỗi từ Neon và dán vào Render!",
        title="TỰ ĐỘNG CHUẨN HÓA SSL CHO NEON"
    )

    # Section 3
    add_h1("3. BƯỚC 2: TRIỂN KHAI BACKEND FASTAPI LÊN RENDER")
    add_body("Render cung cấp 2 phương thức triển khai linh hoạt: qua Giao diện Web Dashboard (trực quan nhất) hoặc tự động qua tệp render.yaml.")
    
    add_h2("3.1. Triển khai qua Web Dashboard Render (Khuyên dùng)")
    add_bullet("Đăng nhập tại https://dashboard.render.com.")
    add_bullet("Nhấp nút \"New +\" ở góc trên cùng bên phải ➔ Chọn \"Web Service\".")
    add_bullet("Chọn \"Build and deploy from a Git repository\" ➔ Chọn repository GitHub chứa code: amobeardat-a11y/apt.")
    add_bullet("Điền thông số cấu hình chính xác theo bảng dưới đây:")

    t2 = doc.add_table(rows=9, cols=3)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    t2.autofit = False
    col_w2 = [Inches(1.8), Inches(2.7), Inches(2.0)]
    for i, title in enumerate(["Mục thiết lập", "Giá trị cần điền", "Giải thích ý nghĩa"]):
        cell = t2.rows[0].cells[i]
        cell.width = col_w2[i]
        cell.paragraphs[0].text = title
    format_row(t2.rows[0], "5348CD", RGBColor(255, 255, 255), bold=True, font_size=10)

    render_fields = [
        ("Name", "apti-backend", "Tên dịch vụ (URL sẽ là https://apti-backend.onrender.com)"),
        ("Region", "Singapore (Southeast Asia)", "Cùng khu vực với Neon DB để tốc độ truy vấn nhanh nhất"),
        ("Branch", "main", "Nhánh mã nguồn chính"),
        ("Root Directory", "apti-backend", "BẮT BUỘC: Vì mã nguồn backend nằm trong thư mục con"),
        ("Runtime", "Python 3", "Môi trường thực thi tiêu chuẩn của Render"),
        ("Build Command", "pip install -r requirements.txt && python -m alembic upgrade head", "Cài đặt thư viện và tự động cập nhật schema DB lên Neon"),
        ("Start Command", "python run.py", "Chạy FastAPI và tự động nhận diện biến $PORT của Render"),
        ("Instance Type", "Free", "Miễn phí hoàn toàn 0đ/tháng")
    ]
    for row_idx, r_data in enumerate(render_fields):
        row = t2.rows[row_idx + 1]
        for col_idx, text in enumerate(r_data):
            cell = row.cells[col_idx]
            cell.width = col_w2[col_idx]
            cell.paragraphs[0].text = text
        bg = "FFFFFF" if row_idx % 2 == 0 else "F8F6FA"
        format_row(row, bg, RGBColor(40, 40, 50), bold=(col_idx==0), font_size=9)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    add_h2("3.2. Cấu hình Biến Môi Trường (Environment Variables) trên Render")
    add_body("Trong phần Advanced ➔ Nhấp \"Add Environment Variable\" và nhập danh sách biến bí mật sau:")
    add_code_block(doc, 
        "ENVIRONMENT=production\n"
        "DEBUG=false\n"
        "DATABASE_URL=postgresql://neondb_owner:YOUR_PASSWORD@ep-xyz-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require\n"
        "SECRET_KEY=apti-production-secret-key-64chars-random-replace-this-securely\n"
        "BACKEND_CORS_ORIGINS=https://*.vercel.app,http://localhost:5500,http://127.0.0.1:5500\n"
        "RATE_LIMIT_ENABLED=true\n"
        "RATE_LIMIT_GENERAL_PER_MINUTE=120\n"
        "RATE_LIMIT_AUTH_PER_MINUTE=15\n"
        "PAYMENT_WEBHOOK_SECRET=apti-webhook-secret-key-neon-secure-2026\n"
        "FIRST_SUPERUSER_EMAIL=admin@apti.vn\n"
        "FIRST_SUPERUSER_PASSWORD=Apti@2026Admin!\n"
        "FIRST_SUPERUSER_NAME=APTI Administrator"
    )
    add_bullet("Nhấp \"Create Web Service\". Render sẽ tải code, cài đặt thư viện và chạy migration.")
    add_bullet("Khi hoàn tất, trạng thái sẽ là Live. Bạn nhận được link dạng: https://apti-backend-xxxx.onrender.com.")

    # Section 4
    add_h1("4. BƯỚC 3: TRIỂN KHAI FRONTEND LÊN VERCEL")
    add_h2("4.1. Cập nhật URL Backend vào Frontend")
    add_body("Trước khi deploy Frontend, mở tệp apti-frontend/js/config.js và cập nhật URL Backend Render của bạn:")
    add_code_block(doc, "// Thay bằng domain Render thực tế của bạn:\nexport const DEFAULT_PRODUCTION_API_URL = 'https://apti-backend-xxxx.onrender.com/api/v1';")
    
    add_h2("4.2. Triển khai trên Vercel Dashboard")
    add_bullet("Đăng nhập https://vercel.com bằng tài khoản GitHub.")
    add_bullet("Tại trang Overview, bấm \"Add New...\" ➔ \"Project\".")
    add_bullet("Tìm kiếm repository apt và bấm \"Import\".")
    add_bullet("Tại mục Root Directory: Nhấp \"Edit\" ➔ Chọn thư mục apti-frontend ➔ Nhấp \"Continue\".")
    add_bullet("Framework Preset: Chọn \"Other\".")
    add_bullet("Build and Output Settings: Giữ nguyên mặc định (Static HTML).")
    add_bullet("Nhấp \"Deploy\". Vercel sẽ tự động build và cấp domain có dạng: https://apti-frontend.vercel.app.")

    # Section 5
    add_h1("5. BƯỚC 4: KẾT NỐI VÀ CẤU HÌNH BẢO MẬT CORS GIỮA HAI BÊN")
    add_body("Hệ thống APTI Backend đã được tích hợp bộ lọc CORS thông minh trong app/main.py:")
    add_code_block(doc,
        "app.add_middleware(\n"
        "    CORSMiddleware,\n"
        "    allow_origins=settings.BACKEND_CORS_ORIGINS,\n"
        "    allow_origin_regex=r\"^https://.*\\.vercel\\.app$\",\n"
        "    allow_credentials=True,\n"
        "    allow_methods=[\"GET\", \"POST\", \"PUT\", \"DELETE\", \"OPTIONS\", \"PATCH\"],\n"
        "    allow_headers=[\"*\"],\n"
        "    expose_headers=[\"X-Process-Time-Ms\", \"Retry-After\"]\n"
        ")"
    )
    add_callout(
        doc,
        "Nhờ biểu thức allow_origin_regex, tất cả domain Preview và Production của Vercel (kể cả https://apt-branch-user.vercel.app) đều có thể kết nối mượt mà tới API Render mà không bao giờ gặp lỗi CORS Policy!",
        title="BẢO MẬT TỐI TÂN & LINH HOẠT"
    )

    # Section 6
    add_h1("6. BƯỚC 5: CHECKLIST KIỂM THỬ VÀ NGHIỆM THU HỆ THỐNG TRÊN MÔI TRƯỜNG THẬT")
    add_bullet("Kiểm tra Health Check API: Truy cập https://apti-backend.onrender.com/api/v1/health. Phản hồi: {\"status\": \"UP\", \"database\": {\"status\": \"HEALTHY\", \"target\": \"Neon PostgreSQL Serverless\"}}")
    add_bullet("Kiểm tra Tài liệu Swagger UI: Truy cập https://apti-backend.onrender.com/docs")
    add_bullet("Kiểm tra Giao diện Vercel: Truy cập https://apti-frontend.vercel.app, linh vật Em Tee 3D sắc nét, không bị răng cưa phông nền.")
    add_bullet("Kiểm tra Xác thực: Đăng nhập thử với học viên student@apti.vn hoặc quản trị viên admin@apti.vn.")
    add_bullet("Kiểm tra Luyện đề & Chấm điểm: Trả lời câu hỏi và bấm Nộp bài thi. Điểm số và phân tích phản hồi ngay lập tức từ Render.")
    add_bullet("Kiểm tra Thanh toán VietQR: Mở gói Pro 30 Ngày, quét mã Napas 24/7 và bấm 'Kích hoạt thử nghiệm (Dev Sim)'.")

    # Section 7
    add_h1("7. BẢNG XỬ LÝ SỰ CỐ THƯỜNG GẶP (TROUBLESHOOTING)")
    t3 = doc.add_table(rows=6, cols=3)
    t3.alignment = WD_TABLE_ALIGNMENT.CENTER
    t3.autofit = False
    col_w3 = [Inches(1.8), Inches(2.2), Inches(2.5)]
    for i, title in enumerate(["Hiện tượng / Triệu chứng", "Nguyên nhân kỹ thuật", "Cách xử lý nhanh"]):
        cell = t3.rows[0].cells[i]
        cell.width = col_w3[i]
        cell.paragraphs[0].text = title
    format_row(t3.rows[0], "5348CD", RGBColor(255, 255, 255), bold=True, font_size=10)

    troubles = [
        ("Lần đầu tải trang API trên Render mất 40-50s", "Gói Free Tier của Render tự động Spin down sau 15 phút không có request.", "Dùng dịch vụ UptimeRobot hoặc cron-job.org ping định kỳ endpoint /api/v1/health mỗi 10 phút để giữ ấm."),
        ("Lỗi offset-naive và offset-aware datetime", "Database trả về thời gian không múi giờ.", "Đã được fix triệt để trong code bằng hàm ensure_utc()."),
        ("Lỗi CORS Access-Control-Allow-Origin", "Domain Vercel chưa có trong cấu hình.", "Đã có sẵn regex *.vercel.app. Nếu dùng domain riêng, thêm vào biến BACKEND_CORS_ORIGINS trên Render."),
        ("Neon báo Connection limit exceeded", "Gói Free của Neon giới hạn max kết nối.", "Bắt buộc dùng Pooled Connection String (có chứa -pooler) và pool_recycle=300."),
        ("Frontend hiển thị Chế độ Ngoại tuyến (Offline)", "Backend Render đang thức giấc hoặc URL sai.", "Kiểm tra biến DEFAULT_PRODUCTION_API_URL trong config.js và đảm bảo backend Render báo trạng thái Live.")
    ]
    for row_idx, r_data in enumerate(troubles):
        row = t3.rows[row_idx + 1]
        for col_idx, text in enumerate(r_data):
            cell = row.cells[col_idx]
            cell.width = col_w3[col_idx]
            cell.paragraphs[0].text = text
        bg = "FFFFFF" if row_idx % 2 == 0 else "F8F6FA"
        format_row(row, bg, RGBColor(40, 40, 50), bold=(col_idx==0), font_size=9)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Signature Footer
    p_sig = doc.add_paragraph()
    p_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_sig = p_sig.add_run("Tài liệu bàn giao kiến trúc triển khai APTI • Google DeepMind Agentic Pair")
    r_sig.font.name = "Segoe UI"
    r_sig.font.size = Pt(9)
    r_sig.font.italic = True
    r_sig.font.color.rgb = RGBColor(120, 120, 140)

    output_path = "HUONG_DAN_DEPLOY_RENDER_VERCEL_NEON.docx"
    doc.save(output_path)
    print(f"Generated docx successfully: {output_path}")

if __name__ == "__main__":
    create_document()
