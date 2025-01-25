#기본 라이브러리
from fastapi import Request
from typing import TypeVar, Generic, Type, Dict, Any, Union, List, Optional, Literal
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from ulid import ULID

#패키지 라이브러리
from .exceptions import ErrorCode, CustomException
from .base_repository import BaseRepository
from .database import (
    process_response,
    validate_unique_fields
)
from .security import hash_password, verify_jwt_token, verify_role_permission
ModelType = TypeVar("ModelType", bound=DeclarativeBase)

class BaseService(Generic[ModelType]):
    ##################
    # 초기화 영역 #
    ##################
    def __init__(
            self,
            model: Type[ModelType],
            repository: BaseRepository[ModelType],
            db_session: AsyncSession,
            additional_models: Dict[str, Type[DeclarativeBase]] = None,
    ):
        self.model = model
        self.repository = repository
        self.db_session = db_session
        self.additional_models = additional_models or {},
    
    #######################
    # 입력 및 수정, 삭제 #
    #######################
    async def create(
        self,
        request: Request,
        entity_data: Dict[str, Any],
        response_model: Any = None,
        exclude_entities: List[str] | None = None,
        unique_check: List[Dict[str, Any]] | None = None,
        fk_check: List[Dict[str, Any]] | None = None,
        org_ulid_position: str = "organization_ulid",
        role_permission: str = "create"
    ) -> ModelType:
        await verify_role_permission(request, role_permission)
        
        try:
            async with self.db_session.begin():
                # 고유 검사 수행
                if unique_check:
                    await validate_unique_fields(self.db_session, unique_check, find_value=True)
                # 외래 키 검사 수행
                if fk_check:
                    await validate_unique_fields(self.db_session, fk_check, find_value=False)
                
                if org_ulid_position:
                    
                result = await self.repository.create(
                    entity_data=entity_data,
                    exclude_entities=exclude_entities
                )

                # 결과 반환
                if response_model:
                    return process_response(result, response_model)
                else:
                    return result

        except CustomException as e:
            raise e
        except Exception as e:
            # 다른 예외 처리
            raise CustomException(
                ErrorCode.INTERNAL_ERROR,
                detail=str(e),
                source_function=f"{self.__class__.__name__}.create",
                original_error=e
            )
        
    async def update(
        self,
        request: Request,
        ulid: str | None = None,
        update_data: Dict[str, Any] | None = None,
        conditions: Dict[str, Any] | None = None,
        unique_check: List[Dict[str, Any]] | None = None,
        exclude_entities: List[str] | None = None,
        response_model: Any = None,
        org_ulid_position: str = "organization_ulid",
        role_permission: str = "update"
    ) -> ModelType:
        try:
            async with self.db_session.begin():
                # 고유 검사 수행
                if unique_check:
                    await validate_unique_fields(self.db_session, unique_check, find_value=True)

                if not ulid and not conditions:
                    raise CustomException(
                        ErrorCode.INVALID_INPUT,
                        detail="Either 'ulid' or 'conditions' must be provided.",
                        source_function="database.update_entity"
                    )

                # ulid로 조건 생성
                if ulid:
                    if not ULID.from_str(ulid):
                        raise CustomException(
                            ErrorCode.VALIDATION_ERROR,
                            detail=ulid,
                            source_function=f"{self.__class__.__name__}.update"
                        )
                    
                    conditions = {"ulid": ulid}

                result = await self.repository.update(
                    update_data=update_data,
                    conditions=conditions,
                    exclude_entities=exclude_entities
                )

                if response_model:
                    return process_response(result, response_model)
                else:
                    return result
        except CustomException as e:
            raise e
        except Exception as e:
            raise CustomException(
                ErrorCode.INTERNAL_ERROR,
                detail=str(e),
                source_function=f"{self.__class__.__name__}.update",
                original_error=e
            )

    async def delete(
        self,
        request: Request,
        ulid: str | None = None,
        conditions: Dict[str, Any] | None = None,
        org_ulid_position: str = "organization_ulid",
        role_permission: str = "delete"
    ) -> bool:
        try:
            if not ULID.from_str(ulid):
                raise CustomException(
                    ErrorCode.VALIDATION_ERROR,
                    detail=ulid,
                    source_function=f"{self.__class__.__name__}.delete"
                )
            
            if not ulid and not conditions:
                raise CustomException(
                    ErrorCode.INVALID_INPUT,
                    detail="Either 'ulid' or 'conditions' must be provided.",
                    source_function="database.update_entity"
                )

            # ulid로 조건 생성
            if ulid:
                conditions = {"ulid": ulid}

            conditions["is_deleted"] = False

            return await self.repository.delete(
                conditions=conditions
            )
        except CustomException as e:
            raise e
        except Exception as e:
            raise CustomException(
                ErrorCode.INTERNAL_ERROR,
                detail=str(e),
                source_function=f"{self.__class__.__name__}.delete",
                original_error=e
            )

    #########################
    # 조회 및 검색 메서드 #
    #########################
    async def list(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        filters: List[Dict[str, Any]] | None = None,
        org_ulid_position: str = "organization_ulid",
        response_model: Any = None,
        explicit_joins: Optional[List[Any]] = None,
        loading_joins: Optional[List[Any]] = None,
        order: Optional[str] = None,
        role_permission: str = "list"
    ) -> List[Dict[str, Any]]:
        try:
            if order is None:
                order = "created_at|desc"

                order_by = order.split("|")
                order = [{"field": order_by[0], "direction": order_by[1]}]

            entities = await self.repository.list(
                skip=skip,
                limit=limit,
                filters=filters,
                explicit_joins=explicit_joins,
                loading_joins=loading_joins,
                order=order
            )
            return [process_response(entity, response_model) for entity in entities]
        
        except CustomException as e:
            raise e
        except Exception as e:
            raise CustomException(
                ErrorCode.INTERNAL_ERROR,
                source_function=f"{self.__class__.__name__}.list",
                original_error=e
            )
        
    async def get(
        self,
        request: Request,
        ulid: str,
        model_name: str | None = None,
        response_model: Any = None,
        conditions: Dict[str, Any] | None = None,
        explicit_joins: Optional[List[Any]] = None,
        loading_joins: Optional[List[Any]] = None,
        org_ulid_position: str = "organization_ulid",
        role_permission: str = "get"
    ):
        try:
            if not ulid and not conditions:
                raise CustomException(
                    ErrorCode.INVALID_INPUT,
                    detail="Either 'ulid' or 'conditions' must be provided.",
                    source_function="database.update_entity"
                )

            # ulid로 조건 생성
            if ulid:
                if not ULID.from_str(ulid):
                    raise CustomException(
                        ErrorCode.VALIDATION_ERROR,
                        detail=ulid,
                        source_function=f"{self.__class__.__name__}.update"
                    )
                
                conditions = {"ulid": ulid}
            
            entity = await self.repository.get(
                conditions=conditions,
                explicit_joins=explicit_joins,
                loading_joins=loading_joins
            )
            return process_response(entity, response_model)

        except CustomException as e:
            raise e
        except Exception as e:
            raise CustomException(
                ErrorCode.INTERNAL_ERROR,
                detail=str(e),
                source_function=f"{self.__class__.__name__}.get",
                original_error=e
            )

