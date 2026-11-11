
import pytest

from evalforge.schemas import EvaluationRequest
from evalforge.scoring import calculate_score


def make_evaluation(
    accuracy=5,
    relevance=5,
    completeness=5,
    clarity=5,
):
    return EvaluationRequest(
        prompt="Explain machine learning.",
        response="Machine learning learns patterns from data.",
        accuracy=accuracy,
        relevance=relevance,
        completeness=completeness,
        clarity=clarity,
    )


def test_perfect_score():
    evaluation = make_evaluation()

    result = calculate_score(evaluation)

    assert result.score == 100.0
    assert result.grade == "Excellent"


def test_zero_score():
    evaluation = make_evaluation(0, 0, 0, 0)

    result = calculate_score(evaluation)

    assert result.score == 0.0
    assert result.grade == "Very Poor"


def test_weighted_score():
    evaluation = make_evaluation(
        accuracy=4,
        relevance=3,
        completeness=5,
        clarity=2,
    )

    result = calculate_score(evaluation)

    assert result.score == 73.0
    assert result.grade == "Fair"


def test_invalid_score_is_rejected():
    with pytest.raises(ValueError):
        make_evaluation(accuracy=6)
