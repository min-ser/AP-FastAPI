from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from azure.identity import DefaultAzureCredential
from pydantic import BaseModel
from redis_entraid.cred_provider import (
    create_from_default_azure_credential,
    TokenManagerConfig,
    RetryPolicy,
)
import redis

# ========== 추가된 필수 모듈 임포트 ==========
import logging
import json
import time
from datetime import datetime
# ============================================

templates = Jinja2Templates(directory="templates")
router = APIRouter()

REDIS_DB = 0
SCOPE = "https://redis.azure.com/.default"
SOCKET_TIMEOUT = 10
SOCKET_CONNECT_TIMEOUT = 10
RETRY_ON_TIMEOUT = True

# Pydantic 모델로 요청 본문 데이터 정의
class RedisInfo(BaseModel):
    redis_host: str
    redis_port: str

# =======================================================
# 📌 기존 /Redis/workloadIdentity 함수를 상세 로깅 버전으로 완전히 대체
# =======================================================
@router.post("/Redis/TTL_Check")
def ttl_check(data: RedisInfo):
    
    result_message = ""
    redis_conn = None 
    
    # 상세 메시지를 콘솔 출력 및 result_message에 누적하는 내부 함수
    def log(message):
        nonlocal result_message
        print(message)
        result_message += message + "\n"
        
    try:
        # Redis 관련 로거들의 레벨을 DEBUG로 설정
        logging.getLogger('redis').setLevel(logging.DEBUG)
        logging.getLogger('redis.auth').setLevel(logging.DEBUG)
        logging.getLogger('redis_entraid').setLevel(logging.DEBUG)
        logging.getLogger('azure.identity').setLevel(logging.DEBUG)
        
        log("=" * 80)
        log("🚀 Starting Azure Entra ID Redis TTL Check")
        log("=" * 80)

        # 1. 환경 설정 확인
        log("📋 Step 1: Loading Redis host and port from request...")
        redis_host = data.redis_host
        redis_port = data.redis_port
        
        if not redis_host or not redis_port:
             log("❌ Error: Redis host and port must be configured")
             raise ValueError("Redis host and port must be configured") 
             
        log(f"   ✓ Redis Host: {redis_host}")
        log(f"   ✓ Redis Port: {redis_port}")

        # 2. Credential Provider 생성
        log("🔐 Step 2: Creating Azure EntraID credential provider...")
        credential_provider = create_from_default_azure_credential(
            scopes=[SCOPE],
            token_manager_config=TokenManagerConfig(
                expiration_refresh_ratio=0.8,
                lower_refresh_bound_millis=300000,
                token_request_execution_timeout_in_ms=10000,
                retry_policy=RetryPolicy(max_attempts=2, delay_in_ms=1000)
            )
        )
        log("   ✅ Credential provider created successfully")

        # 3. Redis 연결 생성
        log("🔌 Step 3: Creating Redis connection with EntraID...")
        redis_conn = redis.Redis(
            host=redis_host,
            port=int(redis_port),
            db=REDIS_DB,
            ssl=True,
            decode_responses=True,
            credential_provider=credential_provider,
            socket_timeout=SOCKET_TIMEOUT,
            socket_connect_timeout=SOCKET_CONNECT_TIMEOUT,
            retry_on_timeout=RETRY_ON_TIMEOUT
        )

        # 4. 키 조회 및 TTL 점검
        log("🔍 Step 4: Scanning for a random key and checking TTL...")
        target_key = redis_conn.randomkey()

        if target_key:
            ttl_seconds = redis_conn.ttl(target_key)
            
            log("-" * 40)
            log(f"🔎 점검 대상 키: [{target_key}]")
            
            if ttl_seconds == -1:
                log("결과: ⚠️  [TTL 미적용] 이 키는 만료 시간이 없는 '영구 키'입니다.")
            elif ttl_seconds == -2:
                log("결과: ❌ [키 없음] 조회 중 키가 만료되었거나 삭제되었습니다.")
            else:
                log(f"결과: ✅ [TTL 적용 중] 남은 수명: {ttl_seconds}초")
            log("-" * 40)
        else:
            log("📢 결과: Redis에 저장된 데이터가 없습니다.")

        log("=" * 80)
        log("✅✅✅ TTL Check Process Completed ✅✅✅")
        log("=" * 80)
        
        return {"message": result_message, "success": True}

    except redis.ConnectionError as e:
        log("=" * 80)
        log(f"❌❌❌ Redis Connection Error ❌❌❌")
        log(f"❌ Error: {str(e)}")
        log("=" * 80)
        return {"message": result_message, "success": False}
    except redis.AuthenticationError as e:
        log("=" * 80)
        log(f"❌❌❌ Redis Authentication Error ❌❌❌")
        log(f"❌ Error: {str(e)}")
        log("=" * 80)
        return {"message": result_message, "success": False}
    except Exception as e:
        log("=" * 80)
        log(f"❌❌❌ Unexpected Error ❌❌❌")
        log(f"❌ Error: {str(e)}")
        log("=" * 80)
        return {"message": result_message, "success": False}

    finally:
        if redis_conn:
            try:
                redis_conn.close()
                log("\n🔐 Connection closed.")
            except:
                pass