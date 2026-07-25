from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from database.base import Base


class IndicatorDefinition(Base):
    __tablename__ = "indicator_definition"

    indicator_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    indicator_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    indicator_name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )