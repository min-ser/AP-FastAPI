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
@router.post("/Redis/workloadIdentity")
def workload_identity(data: RedisInfo):
    
    result_message = ""
    redis_conn = None 
    pattern = "test:entraid:*" 
    
    # 상세 메시지를 콘솔 출력 및 result_message에 누적하는 내부 함수
    def log(message):
        nonlocal result_message
        print(message)
        result_message += message + "\n"
        
    try:
        # Redis 관련 로거들의 레벨을 DEBUG로 설정
        logging.getLogger('redis').setLevel(logging.DEBUG)
        logging.getLogger('redis.auth').setLevel(logging.DEBUG)
        logging.getLogger('redis.auth.token_manager').setLevel(logging.DEBUG)
        logging.getLogger('redis_entraid').setLevel(logging.DEBUG)
        logging.getLogger('azure.identity').setLevel(logging.DEBUG)
        
        log("=" * 80)
        log("🚀 Starting Azure Entra ID Redis Connection Test (Detailed Version)")
        log("=" * 80)
        log("⚙️  DEBUG logging enabled for: redis, redis.auth, redis_entraid, azure.identity")
        log("=" * 80)

        # 1. 환경 설정 확인 (요청 본문 사용)
        log("📋 Step 1: Loading Redis host and port from request...")
        redis_host = data.redis_host
        redis_port = data.redis_port
        
        if not redis_host or not redis_port:
             log("❌ Error: Redis host and port must be configured")
             raise ValueError("Redis host and port must be configured") 
             
        log(f"  ✓ Redis Host: {redis_host}")
        log(f"  ✓ Redis Port: {redis_port}")

        # 2. Credential Provider 생성
        log("🔐 Step 2: Creating Azure EntraID credential provider...")
        log(f"  - Scopes: {SCOPE}")

        credential_provider = create_from_default_azure_credential(
            scopes=[SCOPE],
            token_manager_config=TokenManagerConfig(
                expiration_refresh_ratio=0.8,
                lower_refresh_bound_millis=300000,
                token_request_execution_timeout_in_ms=10000,
                retry_policy=RetryPolicy(max_attempts=2, delay_in_ms=1000)
            )
        )
        log("  ✅ Credential provider created successfully")

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
        log("  ✅ Redis connection object created (lazy initialization)")

        # 4. 연결 테스트 (첫 토큰 요청 발생)
        log("🔍 Step 4: Testing connection with PING command...")
        log("  ⚠️  This will trigger first token request from Token Manager...")
        log("  ⏳ Waiting for token acquisition (timeout: 10 seconds)...")
        # 

        start_time = time.time()

        try:
            ping_result = redis_conn.ping() 
            elapsed = time.time() - start_time
            log(f"  ✅ PING successful: {ping_result} (took {elapsed:.3f}s)")
            log("  ✅ Token acquired and Redis connection established!")
        except Exception as ping_error:
            elapsed = time.time() - start_time
            log(f"  ❌ PING failed after {elapsed:.3f}s")
            log(f"  ❌ Error type: {type(ping_error).__name__}")
            log(f"  ❌ Error message: {str(ping_error)}")
            raise # 연결 실패 시 상위 try-except 블록으로 전파

        # 5. INSERT 테스트
        log("📝 Step 5: Testing INSERT operation...")
        test_key = f"test:entraid:{datetime.now().strftime('%Y%m%d_%H%M%S')}" 
        test_value = {
            "type": "entraid_test",
            "timestamp": datetime.now().isoformat(),
            "pattern": pattern,
            "host": redis_host
        }
        test_value_json = json.dumps(test_value, ensure_ascii=False)

        log(f"  - Key: {test_key}")

        set_result = redis_conn.set(test_key, test_value_json)
        log(f"  ✅ INSERT successful: {set_result}")

        # 6. SELECT 테스트
        log("🔎 Step 6: Testing SELECT operation (verify inserted key)...")
        get_result = redis_conn.get(test_key)
        log(f"  ✅ SELECT successful: Retrieved data length: {len(get_result) if get_result else 0}")

        if get_result:
            try:
                retrieved_data = json.loads(get_result)
                log(f"  ✓ Retrieved data matches (Type check): {retrieved_data.get('type') == 'entraid_test'}")
            except json.JSONDecodeError:
                log("  ⚠️  Failed to decode retrieved data as JSON.")

        # 7. DELETE 테스트
        log("🗑️  Step 7: Testing DELETE operation...")
        delete_result = redis_conn.delete(test_key)
        log(f"  ✅ DELETE successful: {delete_result} key(s) deleted")

        # 8. 최종 결과
        log("=" * 80)
        log("✅✅✅ EntraID Redis Connection Test PASSED ✅✅✅")
        log("=" * 80)
        
        # 성공 시에도 최종 응답은 message 키를 사용하여 반환
        return {"message": result_message}


    except redis.ConnectionError as e:
        log("=" * 80)
        log(f"❌❌❌ Redis Connection Test FAILED: ConnectionError ❌❌❌")
        log(f"❌ Error: {type(e).__name__}: {str(e)}")
        log("💡 Check: Host/Port correctness, Firewall, Network connectivity.")
        log("=" * 80)
        return {"message": result_message, "success": False}
    except redis.AuthenticationError as e:
        log("=" * 80)
        log(f"❌❌❌ Redis Connection Test FAILED: AuthenticationError ❌❌❌")
        log(f"❌ Error: {type(e).__name__}: {str(e)}")
        log("💡 Check: Entra ID configuration, Role assignment to identity.")
        log("=" * 80)
        return {"message": result_message, "success": False}
    except Exception as e:
        # 기타 예상치 못한 오류
        log("=" * 80)
        log(f"❌❌❌ EntraID Redis Connection Test FAILED ❌❌❌")
        log(f"❌ Unexpected Error: {type(e).__name__}: {str(e)}")
        log("=" * 80)
        
        return {"message": result_message, "success": False}

    finally:
        if redis_conn:
            try:
                log("🔌 Closing Redis connection...")
                redis_conn.close()
                log("  ✅ Connection closed successfully")
            except Exception as e:
                log(f"  ⚠️  Error closing connection in finally block: {e}")


