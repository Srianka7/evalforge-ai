
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from evalforge.database import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    response: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    accuracy: Mapped[int] = mapped_column(Integer, nullable=False)
    relevance: Mapped[int] = mapped_column(Integer, nullable=False)
    completeness: Mapped[int] = mapped_column(Integer, nullable=False)
    clarity: Mapped[int] = mapped_column(Integer, nullable=False)

    score: Mapped[float] = mapped_column(Float, nullable=False)
    max_score: Mapped[float] = mapped_column(Float, nullable=False)
    grade: Mapped[str] = mapped_column(String(50), nullable=False)

    explanations: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
