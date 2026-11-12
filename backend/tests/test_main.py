
from fastapi.testclient import TestClient

from evalforge.main import app

from evalforge.database import SessionLocal
from evalforge.models import Evaluation

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_score_evaluation_endpoint():
    payload = {
        "prompt": "Explain machine learning.",
        "response": "Machine learning learns patterns from data.",
        "accuracy": 4,
        "relevance": 3,
        "completeness": 5,
        "clarity": 2,
    }

    response = client.post(
        "/evaluations/score",
        json=payload,
    )

    assert response.status_code == 200

    result = response.json()

    assert result["score"] == 73.0
    assert result["grade"] == "Fair"
    assert result["max_score"] == 100.0


def test_evaluation_is_saved_to_database():
    payload = {
        "prompt": "Database persistence verification",
        "response": "This response should be saved.",
        "accuracy": 4,
        "relevance": 3,
        "completeness": 5,
        "clarity": 2,
    }

    response = client.post(
        "/evaluations/score",
        json=payload,
    )

    assert response.status_code == 200

    db = SessionLocal()
    try:
        saved = (
            db.query(Evaluation)
            .filter(
                Evaluation.prompt
                == "Database persistence verification"
            )
            .first()
        )

        assert saved is not None
        assert saved.score == 73.0
        assert saved.grade == "Fair"
    finally:
        if saved is not None:
            db.delete(saved)
            db.commit()
        db.close()


def test_get_evaluations_history():
    payload = {
        "prompt": "History API verification",
        "response": "This evaluation should appear in history.",
        "accuracy": 5,
        "relevance": 5,
        "completeness": 4,
        "clarity": 4,
    }

    create_response = client.post(
        "/evaluations/score",
        json=payload,
    )

    assert create_response.status_code == 200

    history_response = client.get("/evaluations")

    assert history_response.status_code == 200

    history = history_response.json()

    assert isinstance(history, dict)
    assert "total" in history
    assert "count" in history
    assert "limit" in history
    assert "offset" in history
    assert "results" in history

    assert history["count"] == len(history["results"])
    assert history["total"] >= history["count"]

    assert any(
        item["prompt"] == "History API verification"
        for item in history["results"]
    )


def test_get_evaluation_by_id():
    payload = {
        "prompt": "Individual evaluation lookup",
        "response": "Testing retrieval by ID.",
        "accuracy": 5,
        "relevance": 4,
        "completeness": 5,
        "clarity": 4,
    }

    create_response = client.post(
        "/evaluations/score",
        json=payload,
    )

    assert create_response.status_code == 200

    db = SessionLocal()
    saved = None

    try:
        saved = (
            db.query(Evaluation)
            .filter(
                Evaluation.prompt
                == "Individual evaluation lookup"
            )
            .first()
        )

        assert saved is not None
        evaluation_id = saved.id

        detail_response = client.get(
            f"/evaluations/{evaluation_id}"
        )

        assert detail_response.status_code == 200

        result = detail_response.json()

        assert result["id"] == evaluation_id
        assert result["prompt"] == "Individual evaluation lookup"
        assert result["grade"] == "Excellent"

    finally:
        if saved is not None:
            db.delete(saved)
            db.commit()
        db.close()
