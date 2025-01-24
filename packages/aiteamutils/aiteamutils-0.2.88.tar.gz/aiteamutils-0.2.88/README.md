# AI Team Utils

AI Team의 공통 유틸리티 패키지입니다.

## 설치 방법

```bash
pip install aiteamutils
```

## 사용 예시

```python
from aiteamutils.database import DatabaseService

# DB 서비스 초기화
db_service = DatabaseService("postgresql+asyncpg://user:pass@localhost/db")

# DB 세션 사용
async with db_service.get_db() as session:
    # DB 작업 수행
    pass

# 트랜잭션 사용
async with db_service.transaction():
    # 트랜잭션 내 작업 수행
    result = await db_service.create_entity(UserModel, {"name": "test"})

# 예외 처리
from aiteamutils.exceptions import CustomException, ErrorCode

try:
    # 작업 수행
    pass
except CustomException as e:
    # 에러 처리
    print(e.to_dict())
```

## 주요 기능

- 데이터베이스 유틸리티
  - 세션 관리
  - 트랜잭션 관리
  - 기본 CRUD 작업
  - 외래키 검증
  - 유니크 필드 검증

- 인증/인가 유틸리티
  - JWT 토큰 관리
  - 비밀번호 해싱
  - Rate Limiting

- 예외 처리
  - 표준화된 에러 코드
  - 에러 체인 추적
  - 로깅 통합

- 공통 모델
  - 기본 모델 클래스
  - 타입 검증
  - 유효성 검사 