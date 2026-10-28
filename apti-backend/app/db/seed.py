import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import get_password_hash
from app.models.user import User, UserRole, SubscriptionTier
from app.models.quiz import Category, Question
from app.models.plan import PricingPlan
from app.models.document import DocumentPack

logger = logging.getLogger("apti.seed")


async def seed_database(db: AsyncSession):
    """
    Tự động khởi tạo dữ liệu mẫu khi hệ thống khởi động:
    - Tài khoản Admin & Học viên thử nghiệm
    - Danh mục đề thi (Số học, Logic, Ngôn ngữ, Hình ảnh)
    - Ngân hàng câu hỏi trắc nghiệm tiếng Việt
    - Gói bản quyền (7 ngày, 30 ngày)
    - Bộ tài liệu Ebook
    """
    logger.info("Bắt đầu kiểm tra và khởi tạo dữ liệu mặc định...")

    # 1. Super Admin User
    admin_stmt = select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL.lower())
    admin_user = (await db.execute(admin_stmt)).scalar_one_or_none()
    if not admin_user:
        admin_user = User(
            email=settings.FIRST_SUPERUSER_EMAIL.lower(),
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            full_name=settings.FIRST_SUPERUSER_NAME,
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
            subscription_tier=SubscriptionTier.MASTER_30D
        )
        db.add(admin_user)
        logger.info(f"Đã tạo tài khoản Quản trị viên: {settings.FIRST_SUPERUSER_EMAIL}")

    # Demo Student User
    demo_stmt = select(User).where(User.email == "student@apti.vn")
    demo_user = (await db.execute(demo_stmt)).scalar_one_or_none()
    if not demo_user:
        demo_user = User(
            email="student@apti.vn",
            hashed_password=get_password_hash("Student@2026!"),
            full_name="Nguyễn Văn Học Viên",
            phone="0912345678",
            role=UserRole.USER,
            is_active=True,
            is_verified=True,
            subscription_tier=SubscriptionTier.FREE
        )
        db.add(demo_user)
        logger.info("Đã tạo tài khoản học viên mẫu: student@apti.vn (Mật khẩu: Student@2026!)")

    # 2. Categories
    categories_data = [
        {
            "id": "numerical",
            "name": "Số học",
            "description": "Bài toán phân tích kinh doanh, tỷ lệ tăng trưởng, đọc đồ thị và xử lý số liệu nhanh.",
            "icon": "bi-calculator",
            "display_order": 1
        },
        {
            "id": "logical",
            "name": "Logic",
            "description": "Suy luận tam đoạn luận, nhận diện quy luật suy diễn, điều kiện cần và đủ.",
            "icon": "bi-puzzle",
            "display_order": 2
        },
        {
            "id": "verbal",
            "name": "Ngôn ngữ",
            "description": "Đọc hiểu văn bản học thuật & kinh tế, đánh giá Đúng/Sai/Không đủ dữ liệu (True/False/Cannot Say).",
            "icon": "bi-file-text",
            "display_order": 3
        },
        {
            "id": "abstract",
            "name": "Hình ảnh",
            "description": "Quy luật xoay hình, đối xứng, chuỗi ma trận hình học không gian.",
            "icon": "bi-grid-3x3",
            "display_order": 4
        }
    ]

    for cat_data in categories_data:
        cat = await db.get(Category, cat_data["id"])
        if not cat:
            db.add(Category(**cat_data))

    # 3. Pricing Plans
    plans_data = [
        {
            "id": "starter-7d",
            "name": "Gói 7 Ngày",
            "tagline": "Làm quen và khởi động",
            "price_vnd": 99000,
            "original_price_vnd": 149000,
            "duration_days": 7,
            "badge": "Khởi động",
            "popular": False,
            "is_active": True,
            "features": [
                "Trọn bộ tài liệu tiếng Việt giải mã các dạng bài",
                "Luyện tập online hơn 150+ câu hỏi cơ bản",
                "Đáp án & Lời giải chi tiết từng bước",
                "Đồng hồ đếm ngược mô phỏng áp lực thi thực tế",
                "Báo cáo phân tích điểm mạnh yếu sơ bộ",
                "Hỗ trợ giải đáp thắc mắc cùng cộng đồng"
            ]
        },
        {
            "id": "master-30d",
            "name": "Gói 30 Ngày",
            "tagline": "Luyện tập có kế hoạch & Chinh phục MT",
            "price_vnd": 249000,
            "original_price_vnd": 399000,
            "duration_days": 30,
            "badge": "Được chọn nhiều nhất",
            "popular": True,
            "is_active": True,
            "features": [
                "Tất cả quyền lợi của Gói 7 ngày",
                "Hơn 600+ câu hỏi phân tầng từ cơ bản đến nâng cao",
                "5 đề thi thử Mock Test chuẩn định dạng SHL/Korn Ferry",
                "Video hướng dẫn mẹo tư duy & bẫy đề thi từ cựu MT",
                "Theo dõi tiến độ học tập chi tiết trên Dashboard",
                "Cập nhật đề thi mới liên tục theo mùa tuyển dụng",
                "Cam kết tự tin làm chủ đề thi sau 30 ngày"
            ]
        }
    ]

    for p_data in plans_data:
        p = await db.get(PricingPlan, p_data["id"])
        if not p:
            db.add(PricingPlan(**p_data))

    # 4. Document Packs
    docs_data = [
        {
            "id": "pack-foundation",
            "title": "Tài liệu Nhập môn Aptitude Test Tiếng Việt",
            "desc": "Giải thích chi tiết các dạng bài Numerical, Logical, Verbal bằng ngôn ngữ thuần Việt, dễ hiểu, không hàn lâm.",
            "tag": "Nhập môn",
            "level": "Dành cho người mới",
            "pages": "45 trang PDF",
            "download_url": "/static/docs/nhap-mon-aptitude-test-tieng-viet.pdf",
            "is_premium": False,
            "is_active": True
        },
        {
            "id": "pack-numerical-mastery",
            "title": "Bộ đề Chuyên sâu Numerical Reasoning & Business Math",
            "desc": "Tuyển tập 200 câu hỏi số học thực chiến bám sát các kỳ thi Unilever Ufresh, Vinamilk MT, Big 4.",
            "tag": "Chuyên sâu",
            "level": "Ứng tuyển MT",
            "pages": "120 trang PDF",
            "download_url": "/static/docs/chuyen-sau-numerical-reasoning.pdf",
            "is_premium": True,
            "is_active": True
        },
        {
            "id": "pack-logical-verbal",
            "title": "Giải mã Bẫy đề Logical & Verbal Reasoning",
            "desc": "Phân tích 50 bẫy tư duy thường gặp khiến thí sinh mất điểm oan trong bài test True/False/Cannot Say.",
            "tag": "Mẹo & Bẫy đề",
            "level": "Mọi trình độ",
            "pages": "80 trang PDF",
            "download_url": "/static/docs/giai-ma-bay-de-logical-verbal.pdf",
            "is_premium": True,
            "is_active": True
        },
        {
            "id": "pack-mock-test",
            "title": "Tuyển tập 10 Đề Mock Test chuẩn SHL & Korn Ferry",
            "desc": "Bộ đề hoàn chỉnh có bấm giờ chuẩn áp lực thi thực tế cùng đáp án phân tích chi tiết từng phương án.",
            "tag": "Luyện đề",
            "level": "Chinh phục kỳ thi",
            "pages": "160 trang PDF",
            "download_url": "/static/docs/10-de-mock-test-chuan-shl.pdf",
            "is_premium": True,
            "is_active": True
        }
    ]

    for d_data in docs_data:
        d = await db.get(DocumentPack, d_data["id"])
        if not d:
            db.add(DocumentPack(**d_data))

    # 5. Question Bank
    questions_count = (await db.execute(select(Question))).scalars().all()
    if not questions_count:
        sample_questions = [
            {
                "category_id": "numerical",
                "level": "Cơ bản",
                "question_text": "Năm 2025, doanh thu của công ty APTI đạt 50 tỷ VNĐ. Mục tiêu năm 2026 là tăng trưởng 20%. Doanh thu mục tiêu năm 2026 là bao nhiêu?",
                "options": ["55 tỷ VNĐ", "60 tỷ VNĐ", "62.5 tỷ VNĐ", "70 tỷ VNĐ"],
                "correct_index": 1,
                "explanation": "Mức tăng thêm là: 50 × 20% = 10 tỷ VNĐ. Doanh thu mới = 50 + 10 = 60 tỷ VNĐ (hoặc tính nhanh: 50 × 1.2 = 60).",
                "tip": "Mẹo MT: Khi nhân với 20%, hãy chia cho 5 rồi cộng vào số gốc để ra kết quả trong 3 giây!",
                "is_premium": False,
                "time_limit_seconds": 60
            },
            {
                "category_id": "numerical",
                "level": "Thực tế",
                "question_text": "Một sản phẩm có giá vốn 120.000 VNĐ. Công ty muốn đạt tỷ suất lợi nhuận trên giá bán (Gross Margin) là 25%. Giá bán niêm yết của sản phẩm phải là bao nhiêu?",
                "options": ["150.000 VNĐ", "160.000 VNĐ", "145.000 VNĐ", "175.000 VNĐ"],
                "correct_index": 1,
                "explanation": "Chú ý bẫy tỷ suất lợi nhuận trên GIÁ BÁN: Lợi nhuận = 25% Giá bán ⇒ Giá vốn = 75% Giá bán. Vậy Giá bán = 120.000 / 0.75 = 160.000 VNĐ.",
                "tip": "Bẫy thường gặp: Nhiều bạn lấy 120.000 × 1.25 = 150.000 VNĐ (đây là Markup trên giá vốn, không phải Gross Margin trên doanh số!).",
                "is_premium": False,
                "time_limit_seconds": 90
            },
            {
                "category_id": "logical",
                "level": "Suy luận",
                "question_text": "Tất cả các thành viên đội ngũ Trainee đều giỏi giải quyết vấn đề. Một số thành viên Trainee biết lập trình Python. Kết luận nào sau đây CHẮC CHẮN ĐÚNG?",
                "options": [
                    "Tất cả người giỏi giải quyết vấn đề đều biết Python.",
                    "Một số người biết Python giỏi giải quyết vấn đề.",
                    "Tất cả người biết Python đều là Trainee.",
                    "Không có Trainee nào không biết Python."
                ],
                "correct_index": 1,
                "explanation": "Vì có một số thành viên Trainee biết Python, và tất cả Trainee đều giỏi giải quyết vấn đề, nên những Trainee biết Python đó chắc chắn giỏi giải quyết vấn đề. Do đó 'Một số người biết Python giỏi giải quyết vấn đề' là khẳng định đúng tuyệt đối.",
                "tip": "Vẽ biểu đồ Venn: Vòng tròn Trainee nằm trọn trong Vòng tròn Giỏi giải quyết vấn đề. Vòng Python giao với Trainee, tức là cũng giao với Giỏi giải quyết vấn đề.",
                "is_premium": False,
                "time_limit_seconds": 90
            },
            {
                "category_id": "verbal",
                "level": "Đọc hiểu",
                "question_text": "Đoạn văn: 'Trong năm 2025, ứng dụng trí tuệ nhân tạo (AI) trong quy trình lọc CV đã giúp các tập đoàn đa quốc gia rút ngắn thời gian tuyển dụng ban đầu đến 40%. Tuy nhiên, quyết định tuyển chọn cuối cùng ở vòng phỏng vấn chuyên sâu vẫn do ban giám đốc nhân sự trực tiếp đánh giá.'\n\nNhận định: 'AI là yếu tố duy nhất quyết định ứng viên có trúng tuyển chương trình Management Trainee hay không.'\nNhận định trên là:",
                "options": ["Đúng (True)", "Sai (False)", "Không thể xác định (Cannot Say)"],
                "correct_index": 1,
                "explanation": "Đoạn văn nêu rõ: AI chỉ giúp rút ngắn thời gian lọc CV ban đầu, còn quyết định tuyển chọn cuối cùng vẫn do ban giám đốc nhân sự trực tiếp đánh giá. Vì vậy nhận định 'AI là yếu tố duy nhất quyết định' là SAI hoàn toàn.",
                "tip": "Quy tắc thi Verbal: Cảnh giác cao độ với các từ chỉ tính tuyệt đối như 'duy nhất', 'tất cả', 'luôn luôn'. Nếu đề không khẳng định tính tuyệt đối, câu đó thường là Sai.",
                "is_premium": False,
                "time_limit_seconds": 75
            },
            {
                "category_id": "abstract",
                "level": "Hình ảnh",
                "question_text": "Quy luật ma trận: Một hình vuông xoay 45 độ theo chiều kim đồng hồ ở mỗi bước, đồng thời chấm tròn đen bên trong di chuyển từ góc trên bên trái sang góc dưới bên phải theo đường chéo. Ở bước thứ 4, vị trí của chấm đen sẽ ở đâu?",
                "options": [
                    "Góc trên bên phải",
                    "Góc dưới bên phải",
                    "Chính giữa tâm hình",
                    "Góc dưới bên trái"
                ],
                "correct_index": 1,
                "explanation": "Quy luật di chuyển của chấm đen là tịnh tiến tuyến tính theo đường chéo chính từ trên-trái xuống dưới-phải và cố định tại góc đích.",
                "tip": "Mẹo trừu tượng: Tách biệt riêng rẽ 2 yếu tố (sự xoay của hình lớn và sự dịch chuyển của chấm tròn con) để phân tích độc lập.",
                "is_premium": False,
                "time_limit_seconds": 60
            },
            {
                "category_id": "numerical",
                "level": "Nâng cao",
                "question_text": "Chi phí marketing quý 1 là 80 triệu. Quý 2 tăng 25% so với quý 1. Quý 3 giảm 20% so với quý 2. Chi phí marketing quý 3 là bao nhiêu?",
                "options": ["75 triệu VNĐ", "80 triệu VNĐ", "85 triệu VNĐ", "100 triệu VNĐ"],
                "correct_index": 1,
                "explanation": "Quý 2: 80 × 1.25 = 100 triệu. Quý 3: 100 × (1 - 0.20) = 80 triệu VNĐ. Kết quả không đổi so với Quý 1!",
                "tip": "Quy tắc nghịch đảo phần trăm: Tăng 25% (+1/4) sau đó giảm 20% (-1/5) sẽ đưa giá trị trở về đúng số gốc ban đầu!",
                "is_premium": True,
                "time_limit_seconds": 60
            },
            {
                "category_id": "logical",
                "level": "Thực tế",
                "question_text": "Điều kiện để vào vòng Phỏng vấn nhóm: Ứng viên phải đạt ít nhất 80% điểm bài test năng lực VÀ có chứng chỉ IELTS từ 6.5 trở lên. Hoàng có IELTS 7.5 và không được vào vòng phỏng vấn nhóm. Kết luận nào sau đây chắc chắn đúng?",
                "options": [
                    "Hoàng đạt dưới 80% điểm bài test năng lực.",
                    "Hoàng không tham gia làm bài test năng lực.",
                    "Ban tuyển dụng đã chấm nhầm điểm cho Hoàng.",
                    "Hoàng đạt đúng 80% điểm bài test."
                ],
                "correct_index": 0,
                "explanation": "Vì điều kiện là kết hợp 'VÀ' (cần cả hai), Hoàng đã thỏa mãn IELTS 7.5 mà vẫn bị loại, suy ra Hoàng chắc chắn không thỏa mãn điều kiện còn lại: điểm test dưới 80%.",
                "tip": "Phép toán logic De Morgan: Không (A và B) = (Không A) hoặc (Không B). Khi B đúng thì chắc chắn A phải sai.",
                "is_premium": True,
                "time_limit_seconds": 60
            }
        ]

        for q_item in sample_questions:
            db.add(Question(**q_item, is_active=True))
        logger.info(f"Đã khởi tạo {len(sample_questions)} câu hỏi mẫu chất lượng cao vào ngân hàng đề APTI.")

    await db.commit()
    logger.info("Hoàn tất khởi tạo dữ liệu mặc định thành công.")

