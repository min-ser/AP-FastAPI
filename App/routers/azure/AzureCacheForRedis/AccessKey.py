from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter
from pydantic import BaseModel
import redis

templates = Jinja2Templates(directory="templates")
router = APIRouter()

# Pydantic 모델로 요청 본문 데이터 정의
class RedisInfo(BaseModel):
    redis_host: str
    redis_port: str
    redis_username: str
    redis_password: str

# Azure Storage 연결 테스트 함수 (비동기)
@router.post("/Redis/accesskey")
async def handle_access_key_request(data: RedisInfo):

    print(data)

    r = redis.Redis(
        host=data.redis_host,
        port=data.redis_port,
        username=data.redis_username,
        password=data.redis_password,
        ssl=True,
        ssl_cert_reqs=None,
        decode_responses=True
    )
    result_message = ""
    try:
        print("Ping:", r.ping())  # True 나오면 연결 성공
        result_message += "Ping: " + str(r.ping()) +"\n"
        r.set("test_key", "hello_redis")
        result_message += "r.set(test_key, hello_redis)" +"\n"
        print("test_key 값:", r.get("test_key"))
        result_message += "test_key 값:"+ r.get("test_key") +"\n"
    except redis.exceptions.AuthenticationError as e:
        print("❌ 인증 실패:", e)
        result_message += "❌ 인증 실패:" + str(e) + "\n"
    except Exception as e:
        print("❌ 연결 실패:", e)
        result_message += "❌ 연결 실패:" + str(e) + "\n"

    # 결과를 JSON 형식으로 반환
    return {"message": result_message}