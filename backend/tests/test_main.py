
from fastapi.testclient import TestClient

from evalforge.main import app

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
