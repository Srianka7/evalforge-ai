"""from fastapi import FastAPI

app = FastAPI(
    title="EvalForge AI",
    description=(
        "AI Response Evaluation and "
        "Quality Assurance Platform"
    ),
    version="0.1.0",
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Welcome to EvalForge AI",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "evalforge-api",
    }"""

from fastapi import FastAPI

from evalforge.schemas import EvaluationRequest, EvaluationResult
from evalforge.scoring import calculate_score

app = FastAPI(
    title="EvalForge AI",
    description=(
        "AI Response Evaluation and "
        "Quality Assurance Platform"
    ),
    version="0.2.0",
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Welcome to EvalForge AI",
        "status": "running",
        "version": "0.2.0",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "evalforge-api",
    }


@app.post(
    "/evaluations/score",
    response_model=EvaluationResult,
)
def score_evaluation(
    evaluation: EvaluationRequest,
) -> EvaluationResult:
    return calculate_score(evaluation)
