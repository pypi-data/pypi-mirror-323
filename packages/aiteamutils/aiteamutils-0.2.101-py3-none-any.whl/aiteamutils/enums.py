"""시스템 전체에서 사용되는 열거형 정의."""
from enum import Enum
from typing import Union, Dict
import importlib

from .exceptions import CustomException, ErrorCode

def get_enum_class(
        status_type: str,
        status_id: Union[str, None] = None,
        module_name: str = "app.utils.enums"
    ) -> Union[Dict[str, str], str]:
    """Enum 클래스에서 모든 값을 반환하거나 특정 ID에 해당하는 값을 반환."""
    words = status_type.split('-')
    camel_case_status_type = ''.join(word.capitalize() for word in words)

    try:
        enum_module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        raise CustomException(
            error_code=ErrorCode.NOT_FOUND,
            detail="Status module not found",
            source_function="get_enum_class.enum_module"
        )
    
    try:
        enum_class = getattr(enum_module, camel_case_status_type)
    except AttributeError:
        raise CustomException(
            error_code=ErrorCode.NOT_FOUND,
            detail=f"Status type '{status_type}' not found",
            source_function="get_enum_class.enum_class"
        )
    
    if status_id:
        item = next((item for item in enum_class if item.value == status_id), None)
        if item:
            return item.value
        else:
            raise CustomException(
                error_code=ErrorCode.NOT_FOUND,
                detail=f"'{status_id}' not found in '{status_type}'",
                source_function="get_enum_class"
            )
    else:
        return {status.value: status.value for status in enum_class}

class UserStatus(str, Enum):
    """사용자 상태."""
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BLOCKED = "BLOCKED"

class PermissionType(str, Enum):
    API = "API"
    UI = "UI"
    PAGE = "PAGE"

class PermissionAction(str, Enum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

class PermissionScope(str, Enum):
    OWN = "OWN"
    ALL = "ALL"
    TEAM = "TEAM"
    ORGANIZATION = "ORGANIZATION"

class ActivityType(str, Enum):
    """시스템 활동 유형."""
    # 인증 관련
    ACCESS_TOKEN_ISSUED = "ACCESS_TOKEN_ISSUED"
    REFRESH_TOKEN_ISSUED = "REFRESH_TOKEN_ISSUED"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    
    # 사용자 관련
    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"