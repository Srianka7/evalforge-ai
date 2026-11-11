
from pydantic import BaseModel, Field


class EvaluationRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=10000)
    response: str = Field(min_length=1, max_length=20000)
    reference_answer: str | None = Field(
        default=None,
        max_length=20000,
    )

    accuracy: int = Field(ge=0, le=5)
    relevance: int = Field(ge=0, le=5)
    completeness: int = Field(ge=0, le=5)
    clarity: int = Field(ge=0, le=5)


class EvaluationResult(BaseModel):
    score: float
    max_score: float = 100.0
    grade: str
    criterion_scores: dict[str, int]
