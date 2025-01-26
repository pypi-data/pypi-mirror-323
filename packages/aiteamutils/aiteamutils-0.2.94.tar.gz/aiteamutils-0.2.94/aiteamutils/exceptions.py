"""예외 처리 모듈."""
import logging
from enum import Enum, IntEnum
from typing import Dict, Any, Optional, Tuple, List
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, NoResultFound, MultipleResultsFound, ProgrammingError, OperationalError

logger = logging.getLogger(__name__)

class ErrorResponse:
    def __init__(self, code: int, value: str, status_code: int, detail_template: Optional[str] = None):
        self.code = code
        self.value = value
        self.status_code = status_code
        self.detail_template = detail_template

class ErrorCode(Enum):
    # Auth 관련 에러: 1000번대
    INVALID_CREDENTIALS = ErrorResponse(1001, "AUTH_INVALID_CREDENTIALS", 401, "잘못된 인증 정보입니다")
    TOKEN_EXPIRED = ErrorResponse(1002, "AUTH_TOKEN_EXPIRED", 401, "토큰이 만료되었습니다")
    INVALID_TOKEN = ErrorResponse(1003, "AUTH_INVALID_TOKEN", 401, "유효하지 않은 토큰입니다")
    UNAUTHORIZED = ErrorResponse(1004, "AUTH_UNAUTHORIZED", 401, "인증이 필요합니다")
    FORBIDDEN = ErrorResponse(1005, "AUTH_FORBIDDEN", 403, "접근 권한이 없습니다")
    RATE_LIMIT_EXCEEDED = ErrorResponse(1006, "AUTH_RATE_LIMIT_EXCEEDED", 429, "너무 많은 요청이 발생했습니다")
    INVALID_PASSWORD = ErrorResponse(1007, "AUTH_INVALID_PASSWORD", 401, "잘못된 비밀번호입니다")
    INVALID_ROLE_PERMISSION = ErrorResponse(1008, "AUTH_INVALID_ROLE_PERMISSION", 401, "접근 권한이 없습니다")
    
    # User 관련 에러: 2000번대
    USER_NOT_FOUND = ErrorResponse(2001, "USER_NOT_FOUND", 404, "사용자를 찾을 수 없습니다")
    USER_ALREADY_EXISTS = ErrorResponse(2002, "USER_ALREADY_EXISTS", 409, "이미 존재하는 사용자입니다")
    INVALID_USER_DATA = ErrorResponse(2003, "USER_INVALID_DATA", 400, "잘못된 사용자 데이터입니다")
    FIELD_INVALID_USERNAME = ErrorResponse(2005, "FIELD_INVALID_USERNAME", 400, "잘못된 사용자명입니다")
    FIELD_INVALID_EMAIL = ErrorResponse(2006, "FIELD_INVALID_EMAIL", 400, "잘못된 이메일 형식입니다")
    FIELD_INVALID_PHONE = ErrorResponse(2007, "FIELD_INVALID_PHONE", 400, "잘못된 전화번호 형식입니다")
    
    # Password 관련 에러: 2100번대
    FIELD_INVALID_PASSWORD_LENGTH = ErrorResponse(2101, "FIELD_INVALID_PASSWORD_LENGTH", 400, "비밀번호는 최소 8자 이상이어야 합니다")
    FIELD_INVALID_PASSWORD_UPPER = ErrorResponse(2102, "FIELD_INVALID_PASSWORD_UPPER", 400, "비밀번호는 최소 1개의 대문자를 포함해야 합니다")
    FIELD_INVALID_PASSWORD_NUMBER = ErrorResponse(2103, "FIELD_INVALID_PASSWORD_NUMBER", 400, "비밀번호는 최소 1개의 숫자를 포함해야 합니다")
    FIELD_INVALID_PASSWORD_SPECIAL = ErrorResponse(2104, "FIELD_INVALID_PASSWORD_SPECIAL", 400, "비밀번호는 최소 1개의 특수문자를 포함해야 합니다")
    FIELD_INVALID_PASSWORD_MISMATCH = ErrorResponse(2105, "FIELD_INVALID_PASSWORD_MISMATCH", 400, "새 비밀번호와 확인 비밀번호가 일치하지 않습니다")
    
    # ID 형식 관련 에러: 2200번대
    FIELD_INVALID_ID_LENGTH = ErrorResponse(2201, "FIELD_INVALID_ID_LENGTH", 400, "ID는 최소 3자 이상이어야 합니다")
    FIELD_INVALID_ID_CHARS = ErrorResponse(2202, "FIELD_INVALID_ID_CHARS", 400, "ID는 영문 소문자, 숫자, 언더스코어만 사용할 수 있습니다")
    
    # Database 관련 에러: 3000번대 세분화
    DB_CONNECTION_ERROR = ErrorResponse(3001, "DB_CONNECTION_ERROR", 500, "데이터베이스 연결 오류")
    DB_QUERY_ERROR = ErrorResponse(3002, "DB_QUERY_ERROR", 500, "데이터베이스 쿼리 오류")
    DUPLICATE_ERROR = ErrorResponse(3003, "DB_DUPLICATE_ERROR", 409, "중복된 데이터가 존재합니다")
    FOREIGN_KEY_VIOLATION = ErrorResponse(3004, "DB_FOREIGN_KEY_VIOLATION", 400, "참조하는 데이터가 존재하지 않습니다")
    TRANSACTION_ERROR = ErrorResponse(3005, "DB_TRANSACTION_ERROR", 500, "트랜잭션 처리 중 오류가 발생했습니다")
    DB_READ_ERROR = ErrorResponse(3006, "DB_READ_ERROR", 500, "데이터베이스 읽기 오류가 발생했습니다")
    DB_CREATE_ERROR = ErrorResponse(3007, "DB_CREATE_ERROR", 500, "데이터베이스 생성 오류가 발생했습니다")
    DB_UPDATE_ERROR = ErrorResponse(3008, "DB_UPDATE_ERROR", 500, "데이터베이스 업데이트 오류가 발생했습니다")
    DB_DELETE_ERROR = ErrorResponse(3009, "DB_DELETE_ERROR", 500, "데이터베이스 삭제 오류가 발생했습니다")
    DB_MULTIPLE_RESULTS = ErrorResponse(3010, "DB_MULTIPLE_RESULTS", 500, "중복된 데이터가 조회되었습니다")
    DB_NO_RESULT = ErrorResponse(3011, "DB_NO_RESULT", 404, "데이터를 찾을 수 없습니다")
    DB_INVALID_QUERY = ErrorResponse(3012, "DB_INVALID_QUERY", 500, "잘못된 쿼리 구문입니다")
    DB_OPERATIONAL_ERROR = ErrorResponse(3013, "DB_OPERATIONAL_ERROR", 500, "데이터베이스 작업 중 오류가 발생했습니다")
    
    # Validation 관련 에러: 4000번대
    VALIDATION_ERROR = ErrorResponse(4001, "VALIDATION_ERROR", 422, "유효성 검사 오류")
    FIELD_INVALID_FORMAT = ErrorResponse(4002, "FIELD_INVALID_FORMAT", 400, "잘못된 형식입니다")
    REQUIRED_FIELD_MISSING = ErrorResponse(4003, "VALIDATION_REQUIRED_FIELD_MISSING", 400, "필수 필드가 누락되었습니다")
    FIELD_INVALID_UNIQUE = ErrorResponse(4004, "VALIDATION_FIELD_INVALID_UNIQUE", 400, "중복된 값이 존재합니다")
    FIELD_INVALID_NOT_EXIST = ErrorResponse(4005, "VALIDATION_FIELD_INVALID_NOT_EXIST", 400, "존재하지 않는 값입니다")
    
    # General 에러: 5000번대
    NOT_FOUND = ErrorResponse(5001, "GENERAL_NOT_FOUND", 404, "리소스를 찾을 수 없습니다")
    INTERNAL_ERROR = ErrorResponse(5002, "GENERAL_INTERNAL_ERROR", 500, "내부 서버 오류")
    SERVICE_UNAVAILABLE = ErrorResponse(5003, "GENERAL_SERVICE_UNAVAILABLE", 503, "서비스를 사용할 수 없습니다")
    SERVICE_NOT_REGISTERED = ErrorResponse(5003, "GENERAL_SERVICE_UNAVAILABLE", 503, "서비스를 사용할 수 없습니다")
    LOGIN_ERROR = ErrorResponse(5004, "LOGIN_ERROR", 401, "로그인 오류")
    TOKEN_ERROR = ErrorResponse(5005, "TOKEN_ERROR", 401, "토큰 오류")
    DELETE_ERROR = ErrorResponse(5006, "DELETE_ERROR", 400, "삭제 오류")


class CustomException(Exception):
    """사용자 정의 예외 클래스"""
    
    def __init__(
        self,
        error_code: ErrorCode,
        detail: str,
        source_function: str,
        original_error: Optional[Exception] = None,
        parent_source_function: Optional[str] = None
    ):
        self.error_code = error_code
        self.detail = detail
        self.source_function = source_function
        self.original_error = original_error
        
        # 상위 함수 경로 연결
        if parent_source_function:
            self.source_function = f"{parent_source_function}/{self.source_function}"
        
        # 에러 체인 구성
        self.error_chain = []
        if isinstance(original_error, CustomException):
            self.error_chain = original_error.error_chain.copy()
        
        self.error_chain.append({
            "error_code": str(self.error_code),
            "detail": str(self.detail) if self.detail else None,
            "source_function": self.source_function,
            "original_error": str(self.original_error) if self.original_error else None
        })

    def get_error_chain(self) -> List[Dict[str, Any]]:
        """에러 발생 경로 상세 정보를 반환합니다."""
        return self.error_chain

    def get_original_error(self) -> Optional[Exception]:
        """원본 에러를 반환합니다."""
        return self.original_error

    def to_dict(self) -> Dict[str, Any]:
        """에러 정보를 딕셔너리로 반환합니다."""
        return {
            "error_code": self.error_code.name,
            "detail": self.detail if self.detail else None,
            "source_function": self.source_function,
            "error_chain": self.error_chain,
            "original_error": str(self.original_error) if self.original_error else None
        }

def get_error_details(request: Request, exc: CustomException) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """에러 상세 정보를 생성합니다.
    
    Args:
        request (Request): FastAPI 요청 객체
        exc (CustomException): 발생한 예외
        
    Returns:
        Tuple[Dict[str, Any], Dict[str, Any]]: (로그 데이터, 응답 데이터)
    """
    # 공통 데이터
    base_data = {
        "error_code": exc.error_code.value.code,
        "error_type": exc.error_code.name,
        "status_code": exc.error_code.value.status_code,
        "path": request.url.path,
        "method": request.method,
        "client_ip": request.client.host,
        "user_agent": request.headers.get("user-agent"),
        "detail": exc.detail,
    }
    
    # 로그 데이터에는 error_chain, source_function, detail 포함
    log_data = {
        **base_data,
        "source_function": exc.source_function,
        "error_chain": exc.error_chain,
        "original_error": str(exc.original_error) if exc.original_error else None
    }
    
    # 응답 데이터에는 error_chain, source_function, detail 제외
    response_data = base_data.copy()
    
    return log_data, response_data

def log_error(log_data: Dict[str, Any]):
    """로그 데이터 기록 (다중 줄 포맷)"""
    log_message = ["Request failed:"]
    
    # 기본 에러 정보
    basic_info = [
        "error_code", "error_type", "status_code", "path", 
        "method", "client_ip", "user_agent"
    ]
    for key in basic_info:
        if key in log_data:
            log_message.append(f"    {key}: {log_data[key]}")
    
    # 상세 에러 정보
    if "detail" in log_data:
        log_message.append("    detail:")
        for line in str(log_data["detail"]).split("\n"):
            log_message.append(f"        {line}")
    
    # 에러 체인 정보
    if "error_chain" in log_data:
        log_message.append("    error_chain:")
        for error in log_data["error_chain"]:
            log_message.append("        Error:")
            for key, value in error.items():
                if value:
                    if key == "detail":
                        log_message.append("            detail:")
                        for line in str(value).split("\n"):
                            log_message.append(f"                {line}")
                    else:
                        log_message.append(f"            {key}: {value}")
    
    # 원본 에러 정보
    if "original_error" in log_data and log_data["original_error"]:
        log_message.append("    original_error:")
        for line in str(log_data["original_error"]).split("\n"):
            log_message.append(f"        {line}")
    
    logger.error("\n".join(log_message), extra=log_data)

async def custom_exception_handler(request: Request, exc: CustomException):
    """CustomException에 대한 기본 핸들러"""
    # 로그 데이터와 응답 데이터 생성
    log_data, response_data = get_error_details(
        request=request,
        exc=exc,
    )

    # 로그 기록
    log_error(log_data)

    # 클라이언트 응답 반환
    return JSONResponse(
        status_code=exc.error_code.value.status_code,
        content=response_data,
    )

async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    """FastAPI의 RequestValidationError를 처리합니다."""
    missing_fields = []
    for error in exc.errors():
        if error["type"] == "missing":
            missing_fields.append(error["loc"][1])
    
    error = CustomException(
        ErrorCode.REQUIRED_FIELD_MISSING,
        detail="|".join(missing_fields),
        source_function="FastAPI.request_validation_handler",
        original_error=exc
    )
    return await custom_exception_handler(request, error)

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """SQLAlchemy 관련 예외 처리"""
    error_str = str(exc)
    error_class = exc.__class__.__name__
    error_module = exc.__class__.__module__
    
    # 상세 에러 정보 구성
    error_details = f"{error_module}.{error_class}: {error_str}"
    
    # 스택 트레이스가 있다면 포함
    if hasattr(exc, '__traceback__'):
        import traceback
        stack_trace = ''.join(traceback.format_tb(exc.__traceback__))
        error_details = f"{error_details}\nStack trace:\n{stack_trace}"
    
    # SQL 쿼리 정보 추가 (가능한 경우)
    if hasattr(exc, 'statement'):
        error_details = f"{error_details}\nFailed SQL Query: {exc.statement}"
    if hasattr(exc, 'params'):
        error_details = f"{error_details}\nQuery Parameters: {exc.params}"

    error = None
    
    # SQLAlchemy 예외 타입별 세분화된 처리
    if isinstance(exc, IntegrityError):
        if "violates foreign key constraint" in error_str:
            error = CustomException(
                ErrorCode.FOREIGN_KEY_VIOLATION,
                detail=error_details,
                source_function="DatabaseService.execute_operation",
                original_error=exc
            )
        elif "duplicate key" in error_str:
            error = CustomException(
                ErrorCode.DUPLICATE_ERROR,
                detail=error_details,
                source_function="DatabaseService.execute_operation",
                original_error=exc
            )
        else:
            error = CustomException(
                ErrorCode.DB_QUERY_ERROR,
                detail=error_details,
                source_function="DatabaseService.execute_operation",
                original_error=exc
            )
    elif isinstance(exc, NoResultFound):
        error = CustomException(
            ErrorCode.DB_NO_RESULT,
            detail=error_details,
            source_function="DatabaseService.execute_operation",
            original_error=exc
        )
    elif isinstance(exc, MultipleResultsFound):
        error = CustomException(
            ErrorCode.DB_MULTIPLE_RESULTS,
            detail=error_details,
            source_function="DatabaseService.execute_operation",
            original_error=exc
        )
    elif isinstance(exc, ProgrammingError):
        error = CustomException(
            ErrorCode.DB_INVALID_QUERY,
            detail=error_details,
            source_function="DatabaseService.execute_operation",
            original_error=exc
        )
    elif isinstance(exc, OperationalError):
        error = CustomException(
            ErrorCode.DB_OPERATIONAL_ERROR,
            detail=error_details,
            source_function="DatabaseService.execute_operation",
            original_error=exc
        )
    else:
        error = CustomException(
            ErrorCode.DB_QUERY_ERROR,
            detail=error_details,
            source_function="DatabaseService.execute_operation",
            original_error=exc
        )
    
    # 로그에 추가 정보 기록
    logger.error(
        "Database Error Details:\n"
        f"Error Type: {error_class}\n"
        f"Error Module: {error_module}\n"
        f"Error Message: {error_str}\n"
        f"Request Path: {request.url.path}\n"
        f"Request Method: {request.method}\n"
        f"Client IP: {request.client.host}"
    )
        
    return await custom_exception_handler(request, error)

async def generic_exception_handler(request: Request, exc: Exception):
    """처리되지 않은 예외를 위한 기본 핸들러"""
    error = CustomException(
        ErrorCode.INTERNAL_ERROR,
        detail=str(exc),
        source_function="GenericExceptionHandler.handle_exception"
    )
    return await custom_exception_handler(request, error)