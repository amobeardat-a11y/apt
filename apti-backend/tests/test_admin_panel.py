import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_rbac_protection_comprehensive(client: AsyncClient, student_token: str, admin_token: str):
    """
    KIỂM THỬ BẢO MẬT PHÂN QUYỀN RBAC:
    Học viên thông thường (role: USER) TUYỆT ĐỐI không thể gọi bất kỳ API quản trị nào:
    - Thêm / sửa / xóa câu hỏi
    - Thêm / sửa / xóa đề thi
    - Thêm / sửa / xóa lộ trình
    - Thêm / sửa / xóa banner
    Toàn bộ phải trả về HTTP 403 Forbidden.
    """
    student_headers = {"Authorization": f"Bearer {student_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Questions
    r1 = await client.get("/api/v1/admin/questions", headers=student_headers)
    assert r1.status_code == 403

    r2 = await client.post("/api/v1/admin/questions", json={
        "category_id": "numerical",
        "level": "Cơ bản",
        "question_text": "Hack test question",
        "options": ["A", "B", "C", "D"],
        "correct_index": 0,
        "explanation": "Hack expl"
    }, headers=student_headers)
    assert r2.status_code == 403

    # 2. Exams
    r3 = await client.post("/api/v1/admin/exams", json={
        "title": "Hack exam",
        "description": "Hack desc"
    }, headers=student_headers)
    assert r3.status_code == 403

    # 3. Roadmaps
    r4 = await client.post("/api/v1/admin/roadmaps", json={
        "id": "hack-roadmap",
        "title": "Hack roadmap",
        "subtitle": "Hack sub"
    }, headers=student_headers)
    assert r4.status_code == 403

    # 4. Banners
    r5 = await client.post("/api/v1/admin/banners", json={
        "title": "Hack banner",
        "badge_text": "HACK",
        "description": "Hack desc"
    }, headers=student_headers)
    assert r5.status_code == 403

    # 5. Admin can access stats
    r_admin_stats = await client.get("/api/v1/admin/stats", headers=admin_headers)
    assert r_admin_stats.status_code == 200
    assert r_admin_stats.json()["data"]["total_questions_bank"] >= 1000


@pytest.mark.asyncio
async def test_admin_question_crud(client: AsyncClient, admin_token: str):
    """Kiểm thử thêm, sửa, xóa câu hỏi bởi Admin và kiểm tra ràng buộc dữ liệu."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Test invalid correct_index
    r_bad = await client.post("/api/v1/admin/questions", json={
        "category_id": "numerical",
        "level": "Cơ bản",
        "question_text": "Lỗi đáp án",
        "options": ["A", "B", "C", "D"],
        "correct_index": 99,  # Invalid
        "explanation": "Expl"
    }, headers=headers)
    assert r_bad.status_code == 400

    # Test valid create
    r_create = await client.post("/api/v1/admin/questions", json={
        "category_id": "numerical",
        "level": "Thực tế",
        "question_text": "Một công ty FMCG có doanh thu 100 tỷ VNĐ, giá vốn chiếm 60%. Lợi nhuận gộp là bao nhiêu?",
        "options": ["30 tỷ VNĐ", "40 tỷ VNĐ", "50 tỷ VNĐ", "60 tỷ VNĐ"],
        "correct_index": 1,
        "explanation": "Lợi nhuận gộp = 100 - 60 = 40 tỷ VNĐ.",
        "tip": "Mẹo MT: Doanh thu - Giá vốn = Lợi nhuận gộp.",
        "is_premium": False,
        "time_limit_seconds": 60
    }, headers=headers)
    assert r_create.status_code == 201
    created_q = r_create.json()["data"]
    q_id = created_q["id"]
    assert created_q["correct_index"] == 1

    # Test update
    r_update = await client.put(f"/api/v1/admin/questions/{q_id}", json={
        "level": "Nâng cao",
        "tip": "Mẹo cập nhật"
    }, headers=headers)
    assert r_update.status_code == 200
    assert r_update.json()["data"]["level"] == "Nâng cao"

    # Test delete
    r_del = await client.delete(f"/api/v1/admin/questions/{q_id}", headers=headers)
    assert r_del.status_code == 200


@pytest.mark.asyncio
async def test_exam_flow_and_anti_cheat(client: AsyncClient, admin_token: str):
    """Kiểm thử tạo đề thi, bảo mật chống lộ đáp án (Anti-Cheat) và nộp bài chấm điểm."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Admin tạo đề thi mới với 2 câu ngẫu nhiên
    r_create_exam = await client.post("/api/v1/admin/exams", json={
        "title": "Đề Thi Thử Tự Động 2026",
        "description": "Đề thi thử phục vụ kiểm thử hệ thống",
        "category_id": "numerical",
        "time_limit_minutes": 15,
        "passing_score": 50.0,
        "is_premium": False,
        "random_count": 3
    }, headers=headers)
    assert r_create_exam.status_code == 201
    exam_data = r_create_exam.json()["data"]
    exam_id = exam_data["id"]

    # 2. Học viên lấy đề thi để làm
    r_get_exam = await client.get(f"/api/v1/exams/{exam_id}")
    assert r_get_exam.status_code == 200
    exam_detail = r_get_exam.json()["data"]
    assert len(exam_detail["questions"]) > 0

    # BẢO MẬT ANTI-CHEAT: Đảm bảo không có correct_index hoặc explanation trong câu hỏi gửi về client
    for q in exam_detail["questions"]:
        assert "correct_index" not in q
        assert "explanation" not in q

    # 3. Học viên nộp bài thi
    first_q = exam_detail["questions"][0]
    r_submit = await client.post(f"/api/v1/exams/{exam_id}/submit", json={
        "time_spent_seconds": 120,
        "answers": [
            {"question_id": first_q["id"], "selected_index": 0}
        ]
    })
    assert r_submit.status_code == 200
    submit_res = r_submit.json()["data"]
    assert "score_percentage" in submit_res
    assert "mascot_message" in submit_res
    assert len(submit_res["reviews"]) == 1
    # Sau khi nộp bài, đáp án và lời giải chi tiết mới được trả về
    assert "explanation" in submit_res["reviews"][0]


@pytest.mark.asyncio
async def test_roadmap_and_banner_flow(client: AsyncClient, admin_token: str):
    """Kiểm thử luồng lộ trình (Roadmap) và Banner quảng bá."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Public endpoints
    r_roadmaps = await client.get("/api/v1/roadmaps")
    assert r_roadmaps.status_code == 200
    assert len(r_roadmaps.json()["data"]) >= 1

    r_banners = await client.get("/api/v1/banners")
    assert r_banners.status_code == 200
    assert len(r_banners.json()["data"]) >= 1

    # 2. Admin banner creation
    r_new_banner = await client.post("/api/v1/admin/banners", json={
        "title": "Banner Flash Sale 2026",
        "badge_text": "FLASH SALE",
        "description": "Giảm 50% trọn gói ôn thi",
        "cta_text": "Đăng ký",
        "link_url": "#pricing",
        "bg_gradient": "linear-gradient(135deg, #1FA97A, #5348CD)"
    }, headers=headers)
    assert r_new_banner.status_code == 201
    b_id = r_new_banner.json()["data"]["id"]

    # Delete banner
    r_del = await client.delete(f"/api/v1/admin/banners/{b_id}", headers=headers)
    assert r_del.status_code == 200
