"""보안 관련 유틸리티."""
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Literal, Callable, TYPE_CHECKING, TypeVar
from fastapi import Request, HTTPException, status
from functools import wraps
from jose import jwt, JWTError
from passlib.context import CryptContext
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from .exceptions import CustomException, ErrorCode
from .enums import ActivityType

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ModelType = TypeVar("ModelType")

# 전역 rate limit 상태 저장
_rate_limits: Dict[str, Dict[str, Any]] = {}

class RateLimitExceeded(CustomException):
    """Rate limit 초과 예외."""
    def __init__(self, detail: str, source_function: str):
        super().__init__(
            ErrorCode.RATE_LIMIT_EXCEEDED,
            detail=detail,
            source_function=source_function
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호를 검증합니다."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        raise CustomException(
            ErrorCode.INVALID_PASSWORD,
            detail=plain_password,
            source_function="security.verify_password",
            original_error=e
        )

def hash_password(password: str) -> str:
    """비밀번호를 해시화합니다."""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        raise CustomException(
            ErrorCode.INTERNAL_ERROR,
            detail=password,
            source_function="security.hash_password",
            original_error=e
        )

def rate_limit(
    max_requests: int,
    window_seconds: int,
    key_func: Optional[Callable] = None
):
    """Rate limiting 데코레이터."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Request 객체 찾기
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request:
                for arg in kwargs.values():
                    if isinstance(arg, Request):
                        request = arg
                        break
            if not request:
                raise CustomException(
                    ErrorCode.INTERNAL_ERROR,
                    detail="Request object not found",
                    source_function="rate_limit"
                )
            
            # 레이트 리밋 키 생성
            if key_func:
                rate_limit_key = f"rate_limit:{key_func(request)}"
            else:
                client_ip = request.client.host
                rate_limit_key = f"rate_limit:{client_ip}:{func.__name__}"
            
            try:
                now = datetime.now(timezone.utc)
                
                # 현재 rate limit 정보 가져오기
                rate_info = _rate_limits.get(rate_limit_key)
                
                if rate_info is None or (now - rate_info["start_time"]).total_seconds() >= window_seconds:
                    # 새로운 rate limit 설정
                    _rate_limits[rate_limit_key] = {
                        "count": 1,
                        "start_time": now
                    }
                else:
                    # 기존 rate limit 업데이트
                    if rate_info["count"] >= max_requests:
                        # rate limit 초과
                        remaining_seconds = window_seconds - (now - rate_info["start_time"]).total_seconds()
                        raise CustomException(
                            ErrorCode.RATE_LIMIT_EXCEEDED,
                            detail=f"{int(remaining_seconds)}",
                            source_function=func.__name__
                        )
                    rate_info["count"] += 1
                
                try:
                    # 원래 함수 실행
                    return await func(*args, **kwargs)
                except CustomException as e:
                    raise e
                except Exception as e:
                    raise CustomException(
                        ErrorCode.INTERNAL_ERROR,
                        source_function=func.__name__,
                        original_error=e
                    )
                    
            except CustomException as e:
                raise e
            except Exception as e:
                raise CustomException(
                    ErrorCode.INTERNAL_ERROR,
                    source_function="rate_limit",
                    original_error=e
                )
                
        return wrapper
    return decorator

async def create_jwt_token(
    user_data: Optional[ModelType],
    token_type: Literal["access", "refresh"],
    db_session: AsyncSession,
    token_settings: Dict[str, Any],
) -> str:
    """JWT 토큰을 생성하고 로그를 기록합니다."""
    try:
        # 토큰 데이터 구성
        if token_type == "access":
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=token_settings["ACCESS_TOKEN_EXPIRE_MINUTES"])
            
            token_data = {
                # 등록 클레임
                "iss": token_settings["TOKEN_ISSUER"],
                "sub": user_data.username,
                "aud": token_settings["TOKEN_AUDIENCE"],
                "exp": expires_at,
                
                # 공개 클레임
                "username": user_data.username,
                "name": user_data.name,
                
                # 비공개 클레임
                "user_ulid": user_data.ulid,
                "role_ulid": user_data.role_ulid,
                "team_ulid": user_data.team_ulid,
                "status": user_data.status,
                "last_login": datetime.now(timezone.utc).isoformat(),
                "token_type": token_type,
                
                # 조직 관련 클레임
                "organization_ulid": user_data.role.organization.ulid,
                "organization_id": user_data.role.organization.id,
                "organization_name": user_data.role.organization.name,
                "company_name": user_data.role.organization.company.name
            }
        else:  # refresh token
            expires_at = datetime.now(timezone.utc) + timedelta(days=14)
            token_data = {
                "iss": token_settings["TOKEN_ISSUER"],
                "sub": user_data.username,
                "exp": expires_at,
                "token_type": token_type,
                "user_ulid": user_data.ulid
            }

        # JWT 토큰 생성
        try:
            token = jwt.encode(
                token_data,
                token_settings["JWT_SECRET"],
                algorithm=token_settings["JWT_ALGORITHM"]
            )
        except Exception as e:
            raise CustomException(
                ErrorCode.TOKEN_ERROR,
                detail=f"token|{token_type}",
                source_function="security.create_jwt_token",
                original_error=e
            )
        return token
        
    except CustomException as e:
        raise e
    except Exception as e:
        raise CustomException(
            ErrorCode.INTERNAL_ERROR,
            detail=str(e),
            source_function="security.create_jwt_token",
            original_error=str(e)
        )

async def verify_jwt_token(
    token: str,
    expected_type: Optional[Literal["access", "refresh"]] = None,
    token_settings: Dict[str, Any] = None
) -> Dict[str, Any]:
    """JWT 토큰을 검증합니다."""
    try:
        # token_settings가 None인지 검증
        if not token_settings:
            raise CustomException(
                ErrorCode.CONFIGURATION_ERROR,
                detail="token_settings",
                source_function="security.verify_jwt_token"
            )

        required_settings = ["JWT_SECRET", "JWT_ALGORITHM", "TOKEN_AUDIENCE", "TOKEN_ISSUER"]
        missing_settings = [key for key in required_settings if key not in token_settings]
        if missing_settings:
            raise CustomException(
                ErrorCode.CONFIGURATION_ERROR,
                detail=f"token_settings|{'|'.join(missing_settings)}",
                source_function="security.verify_jwt_token"
            )

        # 토큰 디코딩
        try:
            payload = jwt.decode(
                token,
                token_settings["JWT_SECRET"],
                algorithms=[token_settings["JWT_ALGORITHM"]],
                audience=token_settings["TOKEN_AUDIENCE"],
                issuer=token_settings["TOKEN_ISSUER"]
            )
        except JWTError as e:
            raise CustomException(
                ErrorCode.INVALID_TOKEN,
                detail=token,
                source_function="security.verify_jwt_token",
                original_error=e
            )
        
        # payload가 None인지 확인
        if not payload:
            raise CustomException(
                ErrorCode.INVALID_TOKEN,
                detail=token,
                source_function="security.verify_jwt_token"
            )
        
        # 토큰 타입 검증
        token_type = payload.get("token_type")
        if not token_type:
            raise CustomException(
                ErrorCode.INVALID_TOKEN,
                detail=token,
                source_function="security.verify_jwt_token"
            )
            
        if expected_type and token_type != expected_type:
            raise CustomException(
                ErrorCode.INVALID_TOKEN,
                detail=f"token|{token_type}|{expected_type}",
                source_function="security.verify_jwt_token"
            )
            
        return payload
        
    except CustomException as e:
        # CustomException은 그대로 전달
        raise e
    except Exception as e:
        # 예상치 못한 에러만 INTERNAL_ERROR로 변환
        raise CustomException(
            ErrorCode.INTERNAL_ERROR,
            detail=str(e),
            source_function="security.verify_jwt_token",
            original_error=e
        )

async def verify_role_permission(
    request: Request,
    role_permission: str,
    token_settings: Dict[str, Any] = None,
    org_ulid_position: str = "organization_ulid"
) -> bool | Dict[str, Any]:
    token = request.headers.get("Authorization")

    if not token:
        raise CustomException(
            ErrorCode.UNAUTHORIZED,
            detail="Authorization header is missing",
            source_function="security.verify_role_permission"
        )
    
    token = token.split(" ")[1]

    payload = await verify_jwt_token(
        token=token,
        token_settings=token_settings
    )

    organization_ulid = payload.get("organization_ulid")

    if "list" in role_permission:
        return {
            "value": organization_ulid,
            "operator": "eq",
            "fields": [org_ulid_position]
        }
    elif "create" in role_permission:
        body = await request.json()
        body_org_ulid = body.get(org_ulid_position)
        
        if not body_org_ulid or body_org_ulid != organization_ulid:
            raise CustomException(
                ErrorCode.FORBIDDEN,
                detail=f"{org_ulid_position}|{body_org_ulid}",
                source_function="security.verify_role_permission"
            )
            
        return True
    else:
        return False