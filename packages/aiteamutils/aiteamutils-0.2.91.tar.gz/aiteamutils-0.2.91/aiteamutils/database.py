#기본 라이브러리
from typing import (
    TypeVar, 
    Generic, 
    Type, 
    Any, 
    Dict, 
    List, 
    Optional, 
    AsyncGenerator
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import DeclarativeBase, joinedload, selectinload
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from ulid import ULID
from sqlalchemy import MetaData, Table, insert

#패키지 라이브러리
from .exceptions import ErrorCode, CustomException

ModelType = TypeVar("ModelType", bound=DeclarativeBase)

##################
# 전처리 #
##################
def process_entity_data(
    model: Type[ModelType],
    entity_data: Dict[str, Any],
    existing_data: Dict[str, Any] = None,
    exclude_entities: List[str] | None = None
) -> Dict[str, Any]:
    from .security import hash_password

    """
    엔티티 데이터를 전처리하고 모델 속성과 extra_data를 분리합니다.

    이 함수는 다음과 같은 작업을 수행합니다:
    1. 모델의 기본 속성을 식별합니다.
    2. Swagger 자동 생성 속성을 제외합니다.
    3. 모델 속성에 해당하는 데이터는 model_data에 저장
    4. 모델 속성에 없는 데이터는 extra_data에 저장
    5. 기존 엔티티 데이터의 extra_data를 유지할 수 있습니다.

    Args:
        model (Type[ModelType]): 데이터 모델 클래스
        entity_data (Dict[str, Any]): 처리할 엔티티 데이터
        existing_entity_data (Dict[str, Any], optional): 기존 엔티티 데이터. Defaults to None.

    Returns:
        Dict[str, Any]: 전처리된 모델 데이터 (extra_data 포함)
    """
    # 모델의 속성을 가져와서 전처리합니다.
    model_attr = {
        attr for attr in dir(model)
        if not attr.startswith('_') and not callable(getattr(model, attr))
    }
    model_data = {}
    extra_data = {}

    # 기존 엔티티 데이터가 있으면 추가
    if existing_data and "extra_data" in existing_data:
        extra_data = existing_data["extra_data"].copy()

    # 제외할 엔티티가 있으면 제거
    if exclude_entities:
        entity_data = {k: v for k, v in entity_data.items() if k not in exclude_entities}

    # Swagger 자동 생성 속성 패턴
    swagger_patterns = {"additionalProp1", "additionalProp2", "additionalProp3"}

    for key, value in entity_data.items():
        # Swagger 자동 생성 속성 무시
        if key in swagger_patterns:
            continue

        # 패스워드 필드 처리
        if key == "password":
            value = hash_password(value)  # 비밀번호 암호화

        # 모델 속성에 있는 경우 model_data에 추가
        if key in model_attr:
            model_data[key] = value

        # 모델 속성에 없는 경우 extra_data에 추가
        else:
            extra_data[key] = value

    # extra_data가 있고 모델에 extra_data 속성이 있는 경우 추가
    if extra_data and "extra_data" in model_attr:
        model_data["extra_data"] = extra_data

    return model_data

##################
# 응답 처리 #
##################
def process_columns(
        entity: ModelType,
        exclude_extra_data: bool = True
) -> Dict[str, Any]:
    """엔티티의 컬럼들을 처리합니다.

    Args:
        entity (ModelType): 처리할 엔티티
        exclude_extra_data (bool, optional): extra_data 컬럼 제외 여부. Defaults to True.

    Returns:
        Dict[str, Any]: 처리된 컬럼 데이터
    """
    result = {}
    for column in entity.__table__.columns:
        if exclude_extra_data and column.name == 'extra_data':
            continue
            
        # 필드 값 처리
        if hasattr(entity, column.name):
            value = getattr(entity, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        elif hasattr(entity, 'extra_data') and isinstance(entity.extra_data, dict):
            result[column.name] = entity.extra_data.get(column.name)
        else:
            result[column.name] = None
    
    # extra_data의 내용을 최상위 레벨로 업데이트
    if hasattr(entity, 'extra_data') and isinstance(entity.extra_data, dict):
        result.update(entity.extra_data or {})
            
    return result

def process_response(
        entity: ModelType,
        response_model: Any = None
) -> Dict[str, Any]:
    """응답 데이터를 처리합니다.
    extra_data의 내용을 최상위 레벨로 변환하고, 라우터에서 선언한 응답 스키마에 맞게 데이터를 변환합니다.

    Args:
        entity (ModelType): 처리할 엔티티
        response_model (Any, optional): 응답 스키마. Defaults to None.

    Returns:
        Dict[str, Any]: 처리된 엔티티 데이터
    """
    if not entity:
        return None

    # 모든 필드 처리
    result = process_columns(entity)
    
    # Relationship 처리 (이미 로드된 관계만 처리)
    for relationship in entity.__mapper__.relationships:
        if not relationship.key in entity.__dict__:
            continue
            
        try:
            value = getattr(entity, relationship.key)
            # response_model이 있는 경우 해당 필드의 annotation type을 가져옴
            nested_response_model = None
            if response_model and relationship.key in response_model.model_fields:
                field_info = response_model.model_fields[relationship.key]
                nested_response_model = field_info.annotation
            
            if value is not None:
                if isinstance(value, list):
                    result[relationship.key] = [
                        process_response(item, nested_response_model)
                        for item in value
                    ]
                else:
                    result[relationship.key] = process_response(value, nested_response_model)
            else:
                result[relationship.key] = None
        except Exception:
            result[relationship.key] = None

    # response_model이 있는 경우 필터링
    if response_model:
        # 현재 키 목록을 저장
        current_keys = list(result.keys())
        # response_model에 없는 키 제거
        for key in current_keys:
            if key not in response_model.model_fields:
                result.pop(key)
        # 모델 검증 및 업데이트
        result.update(response_model(**result).model_dump())
            
    return result

##################
# 조건 처리 #
##################
def build_conditions(
    filters: List[Dict[str, Any]],
    model: Type[ModelType]
) -> List[Any]:
    """
    필터 조건을 기반으로 SQLAlchemy 조건 리스트를 생성합니다.

    Args:
        filters: 필터 조건 리스트.
        model: SQLAlchemy 모델 클래스.

    Returns:
        List[Any]: SQLAlchemy 조건 리스트.
    """
    conditions = []

    for filter_item in filters:
        value = filter_item.get("value")
        if not value:  # 값이 없으면 건너뜀
            continue

        operator = filter_item.get("operator", "eq")
        or_conditions = []

        for field_path in filter_item.get("fields", []):
            current_model = model

            # 관계를 따라 필드 가져오기
            for part in field_path.split(".")[:-1]:
                relationship_property = getattr(current_model, part)
                current_model = relationship_property.property.mapper.class_

            field = getattr(current_model, field_path.split(".")[-1])

            # 조건 생성
            if operator == "like":
                or_conditions.append(field.ilike(f"%{value}%"))
            elif operator == "eq":
                or_conditions.append(field == value)

        if or_conditions:  # OR 조건이 있을 때만 추가
            conditions.append(or_(*or_conditions))

    return conditions

##################
# 쿼리 실행 #
##################
async def create_entity(
    session: AsyncSession,
    model: Type[ModelType],
    entity_data: Dict[str, Any],
    exclude_entities: List[str] | None = None
) -> ModelType:
    """
    새로운 엔티티를 데이터베이스에 생성합니다.

    Args:
        session (AsyncSession): 데이터베이스 세션
        model (Type[ModelType]): 생성할 모델 클래스
        entity_data (Dict[str, Any]): 엔티티 생성에 필요한 데이터

    Returns:
        ModelType: 생성된 엔티티

    Raises:
        CustomException: 엔티티 생성 중 발생하는 데이터베이스 오류
    """
    try:
        # 엔티티 데이터 전처리
        processed_data = process_entity_data(
            model=model,
            entity_data=entity_data,
            exclude_entities=exclude_entities
        )
        
        # 새로운 엔티티 생성
        entity = model(**processed_data)
        
        # 세션에 엔티티 추가
        session.add(entity)
        
        # 데이터베이스에 커밋
        await session.flush()
        await session.refresh(entity)
        
        # 생성된 엔티티 반환
        return entity
    
    except SQLAlchemyError as e:
        # 데이터베이스 오류 발생 시 CustomException으로 변환
        raise CustomException(
            ErrorCode.DB_CREATE_ERROR,
            detail=f"{model.__name__}|{str(e)}",
            source_function="database.create_entity",
            original_error=e
        )

async def update_entity(
    session: AsyncSession,
    model: Type[ModelType],
    conditions: Dict[str, Any],
    update_data: Dict[str, Any],
    exclude_entities: List[str] | None = None
) -> ModelType:
    """
    조건을 기반으로 엔티티를 조회하고 업데이트합니다.

    Args:
        session (AsyncSession): 데이터베이스 세션
        model (Type[ModelType]): 업데이트할 모델 클래스
        conditions (Dict[str, Any]): 엔티티 조회 조건 
            conditions = {"user_id": 1, "status": "active"}
        update_data (Dict[str, Any]): 업데이트할 데이터
            update_data = {"status": "inactive"}
    Returns:
        ModelType: 업데이트된 엔티티

    Raises:
        CustomException: 엔티티 조회 또는 업데이트 중 발생하는 데이터베이스 오류
    """
    try:
        # 조건 기반 엔티티 조회
        stmt = select(model)
        for key, value in conditions.items():
            stmt = stmt.where(getattr(model, key) == value)

        result = await session.execute(stmt)
        entity = result.scalar_one_or_none()

        if not entity:
            raise CustomException(
                ErrorCode.NOT_FOUND,
                detail=f"{model.__name__}|{conditions}.",
                source_function="database.update_entity"
            )

        # 기존 데이터를 딕셔너리로 변환
        existing_data = {
            column.name: getattr(entity, column.name)
            for column in entity.__table__.columns
        }

        # 데이터 병합 및 전처리
        processed_data = process_entity_data(
            model=model,
            entity_data=update_data,
            existing_data=existing_data,
            exclude_entities=exclude_entities
        )

        # 엔티티 데이터 업데이트
        for key, value in processed_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        # 변경 사항 커밋
        await session.flush()
        await session.refresh(entity)

        return entity

    except SQLAlchemyError as e:
        raise CustomException(
            ErrorCode.DB_UPDATE_ERROR,
            detail=f"{model.__name__}|{conditions}",
            source_function="database.update_entity",
            original_error=e
        )

async def delete_entity(
    session: AsyncSession,
    model: Type[ModelType],
    conditions: Dict[str, Any]
) -> bool:
    try:
        stmt = select(model)
        for key, value in conditions.items():
            stmt = stmt.where(getattr(model, key) == value)

        result = await session.execute(stmt)
        entity = result.scalar_one_or_none()

        if not entity:
            raise CustomException(
                ErrorCode.NOT_FOUND,
                detail=f"{model.__name__}|{conditions}.",
                source_function="database.delete_entity"
            )

        entity.is_deleted = True
        entity.deleted_at = datetime.now()

        await session.flush()
        await session.refresh(entity)

        return True
    except SQLAlchemyError as e:
        raise CustomException(
            ErrorCode.DB_DELETE_ERROR,
            detail=f"{model.__name__}|{conditions}",
            source_function="database.delete_entity",
            original_error=e
        )

async def purge_entity(
    session: AsyncSession,
    model: Type[ModelType],
    entity: ModelType
) -> bool:
    # 엔티티를 영구 삭제합니다.
    await session.delete(entity)

    return True

async def list_entities(
    session: AsyncSession,
    model: Type[ModelType],
    skip: int = 0,
    limit: int = 100,
    filters: Optional[List[Dict[str, Any]]] = None,
    explicit_joins: Optional[List[Any]] = None,
    loading_joins: Optional[List[Any]] = None,
    order: Optional[List[Dict[str, str]]] = None
) -> List[Dict[str, Any]]:
    """
    엔터티 리스트를 필터 및 조건에 따라 가져오는 함수.

    Args:
        session: SQLAlchemy AsyncSession.
        model: SQLAlchemy 모델.
        skip: 페이지네이션 시작 위치.
        limit: 페이지네이션 크기.
        filters: 필터 조건 딕셔너리.
            예시:
            filters = {
                "search": {"field": "username", "operator": "like", "value": "%admin%"},
                "name": {"field": "name", "operator": "like", "value": "%John%"},
                "role_ulid": {"field": "role_ulid", "operator": "eq", "value": "1234"}
            }

        joins: 조인 옵션.
            예시:
            joins = [
                selectinload(YourModel.related_field),  # 관련된 필드를 함께 로드
                joinedload(YourModel.another_related_field)  # 다른 관계된 필드를 조인
            ]

    Returns:
        List[Dict[str, Any]]: 쿼리 결과 리스트.
    """
    try:
        query = select(model)

        # 명시적 조인 적용
        if explicit_joins:
            for join_target in explicit_joins:
                query = query.join(join_target)  # 명시적으로 정의된 조인 추가

        # 조인 로딩 적용
        if loading_joins:
            for join_option in loading_joins:
                query = query.options(join_option)

        # 필터 조건 적용
        if filters:
            conditions = build_conditions(filters, model)
            query = query.where(and_(*conditions))

        # 정렬 조건 적용
        if order:
            for order_item in order:
                query = query.order_by(getattr(model, order_item["field"]).desc() if order_item["direction"] == "desc" else getattr(model, order_item["field"]).asc())

        # 페이지네이션 적용
        query = query.limit(limit).offset(skip)

        result = await session.execute(query)
        
        return result.scalars().unique().all()
    except SQLAlchemyError as e:
        raise CustomException(
            ErrorCode.DB_READ_ERROR,
            detail=f"{model.__name__}|{str(e)}",
            source_function="database.list_entities",
            original_error=e
        )

async def get_entity(
    session: AsyncSession,
    model: Type[ModelType],
    conditions: Dict[str, Any],
    explicit_joins: Optional[List[Any]] = None,
    loading_joins: Optional[List[Any]] = None
) -> ModelType:
    try:
        query = select(model)

        if explicit_joins:
            for join_target in explicit_joins:
                query = query.join(join_target)

        if loading_joins:
            for join_option in loading_joins:
                query = query.options(join_option)

        if conditions:
            for key, value in conditions.items():
                query = query.where(getattr(model, key) == value)

        result = await session.execute(query)
        return result.scalars().unique().one_or_none()

    except SQLAlchemyError as e:
        raise CustomException(
            ErrorCode.DB_READ_ERROR,
            detail=str(e),
            source_function="database.get_entity",
            original_error=str(e)
        )
    
##################
# 로그 등 #
##################
async def log_create(
    session: AsyncSession,
    model: Type[ModelType],
    log_data: Dict[str, Any],
    request: Optional[Request] = None
) -> None:
    try:
        # 사용자 에이전트 및 IP 주소 추가
        if request:
            log_data["user_agent"] = request.headers.get("user-agent")
            log_data["ip_address"] = request.headers.get("x-forwarded-for") or request.client.host

        await create_entity(
            session=session,
            model=model,
            entity_data=log_data
        )
    except Exception as e:
        raise CustomException(
            ErrorCode.INTERNAL_ERROR,
            detail=f"{model}|{str(e)}",
            source_function="database.log_create",
            original_error=e
        )

######################
# 검증 #
######################
async def validate_unique_fields(
    session: AsyncSession,
    unique_check: List[Dict[str, Any]] | None = None,
    find_value: bool = True  # True: 값이 있는지, False: 값이 없는지 확인
) -> None:
    try:
        for check in unique_check:
            value = check["value"]
            model = check["model"]
            fields = check["fields"]

            # 여러 개의 컬럼이 있을 경우 모든 조건을 만족해야 한다
            conditions = [getattr(model, column) == value for column in fields]

            # 쿼리 실행
            query = select(model).where(or_(*conditions))
            result = await session.execute(query)
            existing = result.scalar_one_or_none()

            # 값이 있는지 확인 (find_value=True) 또는 값이 없는지 확인 (find_value=False)
            if find_value and existing:  # 값이 존재하는 경우
                raise CustomException(
                    ErrorCode.FIELD_INVALID_UNIQUE,
                    detail=f"{model.name}|{value}",
                    source_function="database.validate_unique_fields.existing"
                )
            elif not find_value and not existing:  # 값이 존재하지 않는 경우
                raise CustomException(
                    ErrorCode.FIELD_INVALID_NOT_EXIST,
                    detail=f"{model.name}|{value}",
                    source_function="database.validate_unique_fields.not_existing"
                )

    except CustomException as e:
        # 특정 CustomException 처리
        raise CustomException(
            e.error_code,
            detail=str(e),
            source_function="database.validate_unique_fields.Exception",
            original_error=e
        )
    except Exception as e:
        # 알 수 없는 예외 처리
        raise CustomException(
            ErrorCode.INTERNAL_ERROR,
            detail=f"Unexpected error: {str(e)}",
            source_function="database.validate_unique_fields.Exception",
            original_error=e
        )