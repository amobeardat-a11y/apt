import os
import json
import logging
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import get_password_hash
from app.models.user import User, UserRole, SubscriptionTier
from app.models.quiz import Category, Question
from app.models.plan import PricingPlan
from app.models.document import DocumentPack
from app.models.exam import Exam
from app.models.roadmap import Roadmap
from app.models.banner import Banner

logger = logging.getLogger("apti.seed")


async def seed_database(db: AsyncSession):
    """
    Tự động khởi tạo và đồng bộ hóa toàn bộ dữ liệu mẫu khi hệ thống khởi động:
    - Tài khoản Admin & Học viên thử nghiệm
    - Danh mục đề thi (Số học, Logic, Ngôn ngữ, Hình ảnh)
    - Ngân hàng hơn 1000+ câu hỏi trắc nghiệm tiếng Việt & chuẩn quốc tế SHL/Aon
    - Các bộ đề thi thử mô phỏng (Mock Exams)
    - Các lộ trình học tập theo tuần (Roadmaps)
    - Các Banner sự kiện & quảng bá (Banners)
    - Gói bản quyền (7 ngày, 30 ngày)
    - Bộ tài liệu Ebook & Đề thi PDF
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
                "Luyện tập online hơn 200+ câu hỏi cơ bản",
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
                "Mở khóa toàn bộ ngân hàng 1000+ câu hỏi phân tầng",
                "10 đề thi thử Mock Test chuẩn định dạng SHL/Aon/Korn Ferry",
                "Toàn bộ tài liệu PDF Ebook đề thi tuyển dụng thực tế",
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

    # 4. Document Packs (Bao gồm các file PDF vừa trích xuất từ bộ dữ liệu)
    docs_data = [
        {
            "id": "pack-foundation",
            "title": "Tài liệu Nhập môn Aptitude Test Tiếng Việt",
            "desc": "Giải thích chi tiết các dạng bài Numerical, Logical, Verbal bằng ngôn ngữ thuần Việt, dễ hiểu, không hàn lâm.",
            "tag": "Nhập môn",
            "level": "Dành cho người mới",
            "pages": "45 trang PDF",
            "download_url": "/assets/docs/aon-online-assessment-de-thi-va-dap-an.pdf",
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
            "download_url": "/assets/docs/shl-direct-practice-tests-de-thi-va-dap-an.pdf",
            "is_premium": True,
            "is_active": True
        },
        {
            "id": "pack-aon-assessment",
            "title": "Aon Online Assessment - Đề Thi & Đáp Án Phân Tích",
            "desc": "Trọn bộ đề thi thực chiến chuẩn định dạng Aon Scales (Số học, Diễn dịch Logic, Ma trận chuyển vị) có đáp án.",
            "tag": "Chuẩn Aon",
            "level": "Ứng tuyển MT",
            "pages": "115 trang PDF",
            "download_url": "/assets/docs/aon-online-assessment-de-thi-va-dap-an.pdf",
            "is_premium": True,
            "is_active": True
        },
        {
            "id": "pack-shl-direct",
            "title": "SHL Direct Practice Tests & Tuyển Tập Đề Thi Có Lời Giải",
            "desc": "Tài liệu ôn luyện chính thức SHL: Numerical Reasoning, Verbal Reasoning, Inductive Reasoning và Data Checking.",
            "tag": "Chuẩn SHL",
            "level": "Unilever / Big 4",
            "pages": "140 trang PDF",
            "download_url": "/assets/docs/shl-direct-practice-tests-de-thi-va-dap-an.pdf",
            "is_premium": True,
            "is_active": True
        },
        {
            "id": "pack-mock-test",
            "title": "Tuyển Tập Đề Thi Năng Lực Chuyên Biệt Theo Ngành",
            "desc": "Bộ đề thi tổng hợp áp lực thời gian thực tế kèm phân tích chiến thuật làm bài dưới 60 giây/câu.",
            "tag": "Chuyên biệt",
            "level": "Chinh phục kỳ thi",
            "pages": "160 trang PDF",
            "download_url": "/assets/docs/tong-hop-de-thi-chuyen-biet.pdf",
            "is_premium": True,
            "is_active": True
        }
    ]

    for d_data in docs_data:
        d = await db.get(DocumentPack, d_data["id"])
        if not d:
            db.add(DocumentPack(**d_data))

    # Commit categories, plans, docs first
    await db.commit()

    # 5. Question Bank (Kiểm tra và nạp hơn 1000 câu hỏi)
    q_count_stmt = select(func.count(Question.id))
    current_q_count = (await db.execute(q_count_stmt)).scalar_one() or 0

    if current_q_count < 1000:
        logger.info(f"Hiện có {current_q_count} câu hỏi trong ngân hàng. Đang nạp bộ 1000+ câu hỏi chuẩn hóa...")
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seed_data", "questions_1000.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                questions_data = json.load(f)

            # Insert in chunks of 100 to ensure compatibility with SQLite and Neon PG
            chunk_size = 100
            for i in range(0, len(questions_data), chunk_size):
                chunk = questions_data[i:i + chunk_size]
                for q_dict in chunk:
                    # check if id exists
                    q_id = q_dict.get("id")
                    if q_id:
                        existing = await db.get(Question, q_id)
                        if not existing:
                            db.add(Question(
                                id=q_id,
                                category_id=q_dict["category_id"],
                                level=q_dict.get("level", "Cơ bản"),
                                question_text=q_dict["question_text"],
                                options=q_dict["options"],
                                correct_index=q_dict["correct_index"],
                                explanation=q_dict["explanation"],
                                tip=q_dict.get("tip"),
                                is_premium=q_dict.get("is_premium", False),
                                time_limit_seconds=q_dict.get("time_limit_seconds", 90),
                                is_active=q_dict.get("is_active", True)
                            ))
                await db.commit()
            logger.info(f"-> Đã nạp thành công {len(questions_data)} câu hỏi vào ngân hàng câu hỏi!")
        else:
            logger.warning(f"Không tìm thấy file câu hỏi tại {json_path}")

    # 6. Default Mock Exams
    exam_count = (await db.execute(select(func.count(Exam.id)))).scalar_one() or 0
    if exam_count == 0:
        logger.info("Đang khởi tạo các đề thi thử chuẩn hóa...")
        exams_data = [
            {
                "id": 1,
                "title": "Đề Thi Thử Toàn Diện MT Unilever & Nestlé 2026 (Full Mock Test)",
                "description": "Bài thi mô phỏng 100% vòng test tuyển dụng Management Trainee: Số học, Logic suy luận, Đọc hiểu và Ma trận hình học.",
                "category_id": None,
                "time_limit_minutes": 30,
                "passing_score": 70.0,
                "is_premium": False,
                "is_active": True,
                "question_ids": list(range(1, 31))
            },
            {
                "id": 2,
                "title": "Đề Thi SHL Numerical Reasoning - Phân Tích Dữ Liệu Kinh Doanh",
                "description": "20 câu hỏi bám sát format bài thi SHL Verify Numerical: Tính toán tỷ lệ tăng trưởng, đọc biểu đồ và biên lợi nhuận.",
                "category_id": "numerical",
                "time_limit_minutes": 25,
                "passing_score": 75.0,
                "is_premium": False,
                "is_active": True,
                "question_ids": list(range(31, 51))
            },
            {
                "id": 3,
                "title": "Đề Thi SHL Verbal Reasoning - Tư Duy Đọc Hiểu & Logic Ngôn Ngữ",
                "description": "20 câu hỏi đánh giá khả năng thẩm định thông tin: Đúng (True), Sai (False), Không thể xác định (Cannot Say).",
                "category_id": "verbal",
                "time_limit_minutes": 20,
                "passing_score": 70.0,
                "is_premium": True,
                "is_active": True,
                "question_ids": list(range(566, 586))
            },
            {
                "id": 4,
                "title": "Đề Thi Aon Scales - Tư Duy Quy Nạp & Suy Diễn Nâng Cao",
                "description": "Đề thi thử định dạng Aon/Cut-e: Quy luật ma trận, toán tử chuyển vị và tư duy trừu tượng giải quyết vấn đề.",
                "category_id": "logical",
                "time_limit_minutes": 20,
                "passing_score": 70.0,
                "is_premium": True,
                "is_active": True,
                "question_ids": list(range(281, 301))
            },
            {
                "id": 5,
                "title": "Đề Thi Tuyển Dụng Big 4 (PwC, KPMG, EY, Deloitte) & FMCG",
                "description": "Tổng hợp các bài toán tài chính, tỷ suất sinh lời, hoàn vốn đầu tư và bài toán sắp xếp logic nhân sự.",
                "category_id": None,
                "time_limit_minutes": 30,
                "passing_score": 80.0,
                "is_premium": True,
                "is_active": True,
                "question_ids": list(range(100, 126))
            }
        ]
        for e_dict in exams_data:
            db.add(Exam(**e_dict))
        await db.commit()
        logger.info(f"-> Đã tạo {len(exams_data)} đề thi thử chuẩn hóa.")

    # 7. Default Roadmaps
    roadmap_count = (await db.execute(select(func.count(Roadmap.id)))).scalar_one() or 0
    if roadmap_count == 0:
        logger.info("Đang khởi tạo các lộ trình học tập...")
        roadmaps_data = [
            {
                "id": "mt-fasttrack-4w",
                "title": "Lộ Trình 4 Tuần Bứt Tốc Management Trainee (Fast-Track 2026)",
                "subtitle": "Kế hoạch ôn tập tập trung cao độ 30 ngày dành cho ứng viên chuẩn bị bước vào vòng thi năng lực",
                "target_role": "Management Trainee / Graduate Trainee",
                "duration_weeks": 4,
                "display_order": 1,
                "is_active": True,
                "phases": [
                    {
                        "week": 1,
                        "title": "Tuần 1: Xây nền Số học & Tỷ lệ % kinh doanh",
                        "description": "Làm quen với các công thức tính nhanh: Tăng trưởng doanh thu, Tỷ suất lợi nhuận gộp, Ước lượng không dùng máy tính.",
                        "targets": ["Làm 50 câu Numerical cơ bản", "Đạt độ chính xác > 75%", "Tốc độ < 75s/câu"],
                        "recommended_topics": ["Tỷ lệ phần trăm và biến thiên", "Đọc biểu đồ cột và đồ thị đường FMCG"]
                    },
                    {
                        "week": 2,
                        "title": "Tuần 2: Tư duy Logic Suy diễn & Nhận diện quy luật",
                        "description": "Luyện tập tam đoạn luận (Syllogisms), ma trận logic, nhận diện mệnh đề đảo và điều kiện cần/đủ.",
                        "targets": ["Làm 60 câu Logical", "Nắm vững biểu đồ Venn", "Xử lý bẫy phủ định kép"],
                        "recommended_topics": ["Tam đoạn luận Modus Ponens/Tollens", "Chuỗi số cấp số cộng và nhân lồng"]
                    },
                    {
                        "week": 3,
                        "title": "Tuần 3: Chiến thuật Đọc hiểu True/False/Cannot Say & Trừu tượng",
                        "description": "Rèn luyện kỹ năng định vị từ khóa trong đoạn văn kinh tế và bẫy tuyệt đối hóa. Giải mã ma trận hình học.",
                        "targets": ["Làm 50 câu Verbal", "Làm 40 câu Abstract", "Đạt điểm chuẩn SHL Verbal"],
                        "recommended_topics": ["Chiến thuật định vị Keywords", "Quy luật xoay hình và đối xứng XOR"]
                    },
                    {
                        "week": 4,
                        "title": "Tuần 4: Thi thử áp lực thời gian & Đề chuẩn SHL/Aon",
                        "description": "Làm trọn vẹn 3 Full Mock Tests có bấm giờ đếm ngược, phân tích lỗi sai và củng cố tâm lý phòng thi.",
                        "targets": ["Hoàn thành 3 đề Mock Test", "Điểm số đạt > 80%", "Sẵn sàng 100% cho vòng Test thật"],
                        "recommended_topics": ["Full Mock Test Unilever/Nestlé", "Phân bổ thời gian 60s/câu"]
                    }
                ]
            },
            {
                "id": "mt-mastery-8w",
                "title": "Lộ Trình 8 Tuần Nền Tảng Vững Chắc Cho Người Mới Bắt Đầu",
                "subtitle": "Hành trình bài bản từ con số 0 đến làm chủ toàn diện tất cả các bài thi năng lực của tập đoàn đa quốc gia",
                "target_role": "Sinh viên năm 3, năm 4 & Người mới ứng tuyển",
                "duration_weeks": 8,
                "display_order": 2,
                "is_active": True,
                "phases": [
                    {"week": 1, "title": "Tuần 1: Khái niệm nền tảng Aptitude Test", "description": "Tìm hiểu cấu trúc bài thi của SHL, Aon, Korn Ferry và cách tính điểm percentile.", "targets": ["Làm bài đánh giá năng lực đầu vào", "Xác định điểm mạnh/yếu"], "recommended_topics": ["Tổng quan các nhà cung cấp đề thi"]},
                    {"week": 2, "title": "Tuần 2: Toán kinh doanh & Báo cáo tài chính cơ bản", "description": "Làm chủ các chỉ số tài chính, doanh thu, chi phí, lợi nhuận ròng.", "targets": ["50 câu bài toán tài chính"], "recommended_topics": ["Gross Margin vs Markup"]},
                    {"week": 3, "title": "Tuần 3: Toán đố logic & Dãy số ma trận", "description": "Quy luật dãy số Fibonacci, cấp số nhân, chuỗi logic đan xen.", "targets": ["60 câu chuỗi số"], "recommended_topics": ["Hiệu số bậc 2"]},
                    {"week": 4, "title": "Tuần 4: Tam đoạn luận & Sắp xếp vị trí", "description": "Giải quyết các bài toán xếp chỗ ngồi phòng họp, lịch trình phân bổ.", "targets": ["50 câu bài toán sắp xếp"], "recommended_topics": ["Bảng ma trận logic"]},
                    {"week": 5, "title": "Tuần 5: Tư duy Ngôn ngữ & Văn bản chiến lược", "description": "Thẩm định tính logic của các thông điệp truyền thông và khảo sát.", "targets": ["50 câu Verbal"], "recommended_topics": ["Phát hiện ngụy biện lập luận"]},
                    {"week": 6, "title": "Tuần 6: Tư duy Không gian & Biểu tượng trừu tượng", "description": "Ma trận 3x3 và hình học không gian 3 chiều.", "targets": ["50 câu Abstract"], "recommended_topics": ["Cộng trừ nét ma trận"]},
                    {"week": 7, "title": "Tuần 7: Bài thi phán đoán tình huống (SJT)", "description": "Xử lý xung đột nhóm, ưu tiên công việc trong môi trường làm việc tập đoàn.", "targets": ["30 câu Situational Judgement"], "recommended_topics": ["Các năng lực cốt lõi MT"]},
                    {"week": 8, "title": "Tuần 8: Thi thử toàn diện & Tối ưu tốc độ", "description": "Luyện đề cấp tốc mô phỏng phòng thi thật với áp lực thời gian cao.", "targets": ["Hoàn thành 5 đề Mock Test", "Điểm trung bình > 85%"], "recommended_topics": ["Chiến thuật thi đạt Top 5%"]}
                ]
            }
        ]
        for r_dict in roadmaps_data:
            db.add(Roadmap(**r_dict))
        await db.commit()
        logger.info(f"-> Đã tạo {len(roadmaps_data)} lộ trình học tập chuẩn hóa.")

    # 8. Default Banners
    banner_count = (await db.execute(select(func.count(Banner.id)))).scalar_one() or 0
    if banner_count == 0:
        logger.info("Đang khởi tạo các banner thông báo...")
        banners_data = [
            {
                "id": 1,
                "title": "Mùa Tuyển Dụng Management Trainee 2026 Đã Mở Cổng!",
                "badge_text": "MÙA TUYỂN DỤNG",
                "description": "Luyện tập ngay bộ đề hơn 1,000+ câu hỏi bám sát các kỳ thi tuyển dụng của Unilever, Nestlé, Vinamilk và Big 4.",
                "cta_text": "Luyện đề ngay",
                "link_url": "#quiz-arena",
                "bg_gradient": "linear-gradient(135deg, #5348CD 0%, #7B68EE 50%, #F54899 100%)",
                "is_active": True,
                "display_order": 1
            },
            {
                "id": 2,
                "title": "Ngân Hàng Câu Hỏi Chuẩn Quốc Tế SHL & Aon 2026",
                "badge_text": "MỚI CẬP NHẬT",
                "description": "Đầy đủ 4 phân hệ: Số học (Numerical), Logic (Deductive/Inductive), Ngôn ngữ (Verbal) và Hình ảnh (Abstract) có giải thích chi tiết.",
                "cta_text": "Xem danh mục",
                "link_url": "#categories-section",
                "bg_gradient": "linear-gradient(135deg, #1FA97A 0%, #5348CD 100%)",
                "is_active": True,
                "display_order": 2
            },
            {
                "id": 3,
                "title": "Ưu Đãi Đặc Biệt: Nâng Cấp Hội Viên MT Master 30 Ngày",
                "badge_text": "ƯU ĐÃI 40%",
                "description": "Mở khóa trọn bộ 1,000+ câu hỏi cao cấp và tặng kèm 4 bộ tài liệu Ebook độc quyền kèm lời giải.",
                "cta_text": "Nhận ưu đãi ngay",
                "link_url": "#pricing",
                "bg_gradient": "linear-gradient(135deg, #F54899 0%, #F5A524 100%)",
                "is_active": True,
                "display_order": 3
            }
        ]
        for b_dict in banners_data:
            db.add(Banner(**b_dict))
        await db.commit()
        logger.info(f"-> Đã tạo {len(banners_data)} banner quảng bá.")

    logger.info("Hoàn tất khởi tạo dữ liệu mặc định thành công.")
