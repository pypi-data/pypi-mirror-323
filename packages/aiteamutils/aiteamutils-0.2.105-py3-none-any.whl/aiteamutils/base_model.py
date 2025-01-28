from datetime import datetime, timedelta, timezone
from typing import Any, Dict, TypeVar, Generic, Optional
from ulid import ULID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Column, String, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP
from pydantic import BaseModel, ConfigDict
from pydantic import Field

class Base(DeclarativeBase):
    """SQLAlchemy 기본 모델"""
    pass

class BaseColumn(Base):
    """공통 설정 및 메서드를 제공하는 BaseColumn"""
    __abstract__ = True

    ulid: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        unique=True,
        default=lambda: str(ULID()),
        doc="ULID",
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now(timezone.utc),
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        index=True
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=None,
        nullable=True
    )
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        index=True
    )

    def to_dict(self) -> Dict[str, Any]:
        """모델을 딕셔너리로 변환합니다.
        
        Returns:
            Dict[str, Any]: 모델의 속성을 포함하는 딕셔너리
        """
        result = {}
        
        # 테이블 컬럼 처리
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        
        # Relationship 처리 (이미 로드된 관계만 처리)
        for relationship in self.__mapper__.relationships:
            if relationship.key == "organizations":  # 순환 참조 방지
                continue
            try:
                value = getattr(self, relationship.key)
                if value is not None:
                    if isinstance(value, list):
                        result[relationship.key] = [item.to_dict() for item in value]
                    else:
                        result[relationship.key] = value.to_dict()
                else:
                    result[relationship.key] = None
            except Exception:
                result[relationship.key] = None
                
        return result

class BaseSchema(BaseModel):
    """공통 설정 및 메서드를 제공하는 BaseSchema"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        str_to_strip=True,
        coerce_numbers_to_str=True,
        null_to_none=True,
        validate_default=True,
        extra="allow",
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True
    )

    def to_dict(self) -> Dict[str, Any]:
        """모델을 딕셔너리로 변환"""
        return self.model_dump()