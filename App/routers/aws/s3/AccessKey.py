from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter
from pydantic import BaseModel
import boto3

templates = Jinja2Templates(directory="templates")
router = APIRouter()

# Pydantic 모델로 요청 본문 데이터 정의
class ConnectionStringData(BaseModel):
    connection_string: str

# Azure Storage 연결 테스트 함수 (비동기)
async def check_access_key(connection_string: str) -> str:
    message = ""
    try:
        # 비동기 BlobServiceClient 인스턴스 생성
        async with BlobServiceClient.from_connection_string(connection_string) as blob_service_client:
            # 컨테이너 목록을 가져와 연결 테스트
            # 비동기적으로 이터레이터 순회
            container_list = []
            async for container in blob_service_client.list_containers():
                container_list.append(container.name)
            
            message += "Azure Storage 계정에 성공적으로 연결되었습니다. 🎉\n"
            message += "현재 계정의 컨테이너 목록:\n"
            for container_name in container_list:
                message += f"- {container_name}\n"

    except ValueError as e:
        message += f"오류: 연결 문자열이 올바르지 않습니다. {e}\n"
    except Exception as e:
        message += f"Azure Storage 연결 중 오류가 발생했습니다: {e}\n"

    return message.strip()

# Ajax 요청을 받을 API 엔드포인트
@router.post("/StorageAccount/accesskey")
async def handle_access_key_request(data: ConnectionStringData):
    """
    클라이언트로부터 Connection String을 받아 Azure 연결을 테스트합니다.
    """
    connection_string = data.connection_string
    result_message = await check_access_key(connection_string)

    # 결과를 JSON 형식으로 반환
    if "오류:" in result_message or "오류가 발생했습니다" in result_message:
        return {"message": result_message}
    else:
        return {"message": result_message}