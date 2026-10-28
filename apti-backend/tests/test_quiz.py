import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_quiz_integrity_no_answer_leak(client: AsyncClient):
    """
    CRITICAL SECURITY CHECK:
    Ensure questions endpoint NEVER leaks correct_index or explanation before submission!
    """
    res = await client.get("/api/v1/quiz/questions?limit=5")
    assert res.status_code == 200
    questions = res.json()["data"]
    assert len(questions) > 0

    for q in questions:
        assert "id" in q
        assert "question_text" in q
        assert "options" in q
        # Ensure answers and explanations are NOT leaked
        assert "correct_index" not in q
        assert "explanation" not in q


@pytest.mark.asyncio
async def test_quiz_submission_and_grading(client: AsyncClient):
    # Fetch questions
    res = await client.get("/api/v1/quiz/questions?limit=2")
    questions = res.json()["data"]
    q1 = questions[0]

    # Submit quiz
    sub_res = await client.post(
        "/api/v1/quiz/submit",
        json={
            "mode": "PRACTICE",
            "time_spent_seconds": 45,
            "answers": [
                {"question_id": q1["id"], "selected_index": 1}
            ]
        }
    )
    assert sub_res.status_code == 200
    result = sub_res.json()["data"]
    assert "score_percentage" in result
    assert "reviews" in result
    assert "mascot_message" in result
    assert len(result["reviews"]) == 1
    # After submission, correct index and explanation are revealed
    assert "correct_index" in result["reviews"][0]
    assert "explanation" in result["reviews"][0]

