from fastapi import FastAPI

from evalforge.database import Base, engine
from evalforge import models

from evalforge.schemas import EvaluationRequest, EvaluationResult
from evalforge.scoring import calculate_score

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy import func
from fastapi import Depends

from evalforge.database import get_db
from evalforge.models import Evaluation

from fastapi import FastAPI, Depends, HTTPException

from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware

import os
from dotenv import load_dotenv
from openai import OpenAI

from evalforge.ai_evaluator import evaluate_with_ai
from evalforge.schemas import AIEvaluationRequest

import json

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

app = FastAPI(
    title="EvalForge AI",
    description=(
        "AI Response Evaluation and "
        "Quality Assurance Platform"
    ),
    version="0.2.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

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
    db: Session = Depends(get_db),
) -> EvaluationResult:

    result = calculate_score(evaluation)

    db_evaluation = Evaluation(
        prompt=evaluation.prompt,
        response=evaluation.response,
        accuracy=evaluation.accuracy,
        relevance=evaluation.relevance,
        completeness=evaluation.completeness,
        clarity=evaluation.clarity,
        score=result.score,
        max_score=result.max_score,
        grade=result.grade,
    )

    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)

    return result

@app.post("/evaluations/auto")
def auto_evaluate(
    request: AIEvaluationRequest,
    db: Session = Depends(get_db),
):
    try:
        assessment = evaluate_with_ai(
            prompt=request.prompt,
            response=request.response,
        )

        print("AI ASSESSMENT:", assessment.model_dump())

        evaluation_request = EvaluationRequest(
            prompt=request.prompt,
            response=request.response,
            accuracy=assessment.accuracy,
            relevance=assessment.relevance,
            completeness=assessment.completeness,
            clarity=assessment.clarity,
        )

        result = calculate_score(evaluation_request)

        evaluation = Evaluation(
        prompt=request.prompt,
        response=request.response,
        accuracy=assessment.accuracy,
        relevance=assessment.relevance,
        completeness=assessment.completeness,
        clarity=assessment.clarity,
        score=result.score,
        max_score=result.max_score,
        grade=result.grade,
        explanations=json.dumps({
            "accuracy": assessment.accuracy_reason,
            "relevance": assessment.relevance_reason,
            "completeness": assessment.completeness_reason,
            "clarity": assessment.clarity_reason,
        }),
    )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)

        return {
            "id": evaluation.id,
            "score": result.score,
            "max_score": result.max_score,
            "grade": result.grade,
            "criterion_scores": result.criterion_scores,
            "explanations": {
                "accuracy": assessment.accuracy_reason,
                "relevance": assessment.relevance_reason,
                "completeness": assessment.completeness_reason,
                "clarity": assessment.clarity_reason,
            },
        }

    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=502,
            detail=f"Automatic evaluation failed: {str(error)}",
        ) from error

@app.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    total = db.scalar(
        select(func.count()).select_from(Evaluation)
    ) or 0

    average_score = db.scalar(
        select(func.avg(Evaluation.score))
    ) or 0

    grade_rows = db.execute(
        select(
            Evaluation.grade,
            func.count(Evaluation.id),
        ).group_by(Evaluation.grade)
    ).all()

    grade_counts = {
        "Excellent": 0,
        "Good": 0,
        "Fair": 0,
        "Poor": 0,
        "Very Poor": 0,
    }

    for grade, count in grade_rows:
        grade_counts[grade] = count

    return {
        "total_evaluations": total,
        "average_score": round(float(average_score), 2),
        "grade_counts": grade_counts,
    }

@app.get("/analytics/trends")
def get_evaluation_trends(db: Session = Depends(get_db)):
    rows = db.execute(
        select(
            func.date(Evaluation.created_at).label("date"),
            func.avg(Evaluation.score).label("average_score"),
            func.count(Evaluation.id).label("total"),
        )
        .group_by(func.date(Evaluation.created_at))
        .order_by(func.date(Evaluation.created_at))
    ).all()

    return {
        "dates": [
            row.date for row in rows
        ],
        "average_scores": [
            round(float(row.average_score), 2)
            for row in rows
        ],
        "evaluation_counts": [
            row.total for row in rows
        ],
    }

@app.get("/evaluations")
def get_evaluations(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    grade: str | None = None,
    db: Session = Depends(get_db),
):
    query = select(Evaluation)

    if grade is not None:
        query = query.where(Evaluation.grade == grade)

    total = db.scalar(
        select(func.count()).select_from(query.subquery())
    )

    evaluations = db.scalars(
        query
        .order_by(Evaluation.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    return {
        "total": total,
        "count": len(evaluations),
        "limit": limit,
        "offset": offset,
        "results": evaluations,
    }

@app.get("/evaluations/{evaluation_id}")
def get_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db),
):
    evaluation = db.get(Evaluation, evaluation_id)

    if evaluation is None:
        raise HTTPException(
            status_code=404,
            detail="Evaluation not found",
        )

    return {
        "id": evaluation.id,
        "prompt": evaluation.prompt,
        "response": evaluation.response,
        "accuracy": evaluation.accuracy,
        "relevance": evaluation.relevance,
        "completeness": evaluation.completeness,
        "clarity": evaluation.clarity,
        "score": evaluation.score,
        "max_score": evaluation.max_score,
        "grade": evaluation.grade,
        "created_at": evaluation.created_at,
        "explanations": (
            json.loads(evaluation.explanations)
            if evaluation.explanations
            else None
        ),
    }
