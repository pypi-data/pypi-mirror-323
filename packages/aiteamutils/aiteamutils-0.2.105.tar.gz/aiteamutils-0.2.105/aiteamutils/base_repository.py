#기본 라이브러리
from typing import TypeVar, Generic, Type, Any, Dict, List, Optional
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

#패키지 라이브러리
from .exceptions import ErrorCode, CustomException
from .database import (
    list_entities,
    get_entity,
    create_entity,
    update_entity,
    delete_entity
)

ModelType = TypeVar("ModelType", bound=DeclarativeBase)

class BaseRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self._session = session
        self.model = model
    
    @property
    def session(self) -> AsyncSession:
        return self._session
    
    @session.setter
    def session(self, value: AsyncSession):
        if value is None:
            raise CustomException(
                ErrorCode.DB_CONNECTION_ERROR,
                detail="Session cannot be None",
                source_function=f"{self.__class__.__name__}.session"
            )
        self._session = value
   
    #######################
    # 입력 및 수정, 삭제 #
    ####################### 
    async def create(
        self,
        entity_data: Dict[str, Any],
        exclude_entities: List[str] | None = None
    ) -> ModelType:
        try:
            return await create_entity(
                session=self.session,
                model=self.model,
                entity_data=entity_data,
                exclude_entities=exclude_entities
            )
        except CustomException as e:
            raise e
        except Exception as e:
            raise CustomException(
                ErrorCode.INTERNAL_ERROR,
                detail=str(e),
                source_function=f"{self.__class__.__name__}.create",
                original_error=e
            )
        
    async def update(
        self,
        entity_data: Dict[str, Any],
        conditions: Dict[str, Any],
        exclude_entities: List[str] | None = None
    ) -> ModelType:
        try:
            return await update_entity(
                session=self.session,
                model=self.model,
                entity_data=entity_data,
                conditions=conditions,
                exclude_entities=exclude_entities
            )
        except CustomException as e:
            raise e
        
    async def delete(
        self,
        conditions: Dict[str, Any]
    ) -> bool:
        await delete_entity(
            session=self.session,
            model=self.model,
            conditions=conditions
        )
        return True
    #########################
    # 조회 및 검색 메서드 #
    #########################
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[List[Dict[str, Any]]] = None,
        explicit_joins: Optional[List[Any]] = None,
        loading_joins: Optional[List[Any]] = None,
        order: Optional[List[Dict[str, str]]] = None
    ) -> List[ModelType]:
        """
        엔티티 목록 조회.
        """
        try:
            # 기본 CRUD 작업 호출
            return await list_entities(
                session=self.session,
                model=self.model,
                skip=skip,
                limit=limit,
                filters=filters,
                explicit_joins=explicit_joins,
                loading_joins=loading_joins,
                order=order
            )
        except CustomException as e:
            raise e
        except Exception as e:
            raise CustomException(
                ErrorCode.INTERNAL_ERROR,
                detail=str(e),
                source_function=f"{self.__class__.__name__}.list",
                original_error=e
            )
        
    async def get(
        self,
        conditions: Dict[str, Any] | None = None,
        explicit_joins: Optional[List[Any]] = None,
        loading_joins: Optional[List[Any]] = None
    ) -> ModelType:
        try:
            return await get_entity(
                session=self.session,
                model=self.model,
                conditions=conditions,
                explicit_joins=explicit_joins,
                loading_joins=loading_joins
            )
        except CustomException as e:
            raise e
        except Exception as e:
            raise CustomException(
                ErrorCode.INTERNAL_ERROR,
                detail=str(e),
                source_function=f"{self.__class__.__name__}.get",
                original_error=e
            )