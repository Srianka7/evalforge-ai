
from evalforge.schemas import EvaluationRequest, EvaluationResult


WEIGHTS = {
    "accuracy": 0.40,
    "relevance": 0.25,
    "completeness": 0.20,
    "clarity": 0.15,
}


def calculate_score(
    evaluation: EvaluationRequest,
) -> EvaluationResult:

    scores = {
        "accuracy": evaluation.accuracy,
        "relevance": evaluation.relevance,
        "completeness": evaluation.completeness,
        "clarity": evaluation.clarity,
    }

    weighted_score = sum(
        scores[criterion] * weight
        for criterion, weight in WEIGHTS.items()
    )

    final_score = round(weighted_score * 20, 2)

    if final_score >= 90:
        grade = "Excellent"
    elif final_score >= 75:
        grade = "Good"
    elif final_score >= 60:
        grade = "Fair"
    elif final_score >= 40:
        grade = "Poor"
    else:
        grade = "Very Poor"

    return EvaluationResult(
        score=final_score,
        grade=grade,
        criterion_scores=scores,
    )
