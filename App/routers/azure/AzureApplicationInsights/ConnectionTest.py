import logging
import re
import socket
import subprocess
import platform
from fastapi import APIRouter
from pydantic import BaseModel
from opencensus.ext.azure.log_exporter import AzureLogHandler

# FastAPI 라우터 및 Pydantic 모델 정의 (코드의 일부라고 가정)
router = APIRouter()

class ApplicationInsightInfo(BaseModel):
    connection_string: str

@router.post("/ApplicationInsights/connectionTest")
async def handle_access_key_request(data: ApplicationInsightInfo):
    result_message = ""
    endpoint = ""
    
    try:
        logger = logging.getLogger(__name__)

        # 1. 연결 문자열에서 IngestionEndpoint 호스트 이름 추출
        match = re.search(r'IngestionEndpoint=https?://([^/]+)/', data.connection_string)
        if match:
            endpoint = match.group(1)
            result_message += f"Ingestion Endpoint: {endpoint}\n"
        else:
            raise ValueError("Invalid connection string format: IngestionEndpoint not found.")

        # 2. DNS(nslookup) 테스트
        try:
            ip_address = socket.gethostbyname(endpoint)
            result_message += f"✅ DNS lookup successful: {endpoint} -> {ip_address}\n"
        except socket.gaierror as e:
            result_message += f"❌ DNS lookup failed: Could not resolve '{endpoint}'. Error: {e}\n"
            return {"message": result_message}

        # 3. Ping 테스트
        # OS에 따라 Ping 명령 옵션 조정
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '4', endpoint]
        
        try:
            ping_process = subprocess.run(command, capture_output=True, text=True, timeout=10)
            if ping_process.returncode == 0:
                result_message += "✅ Ping test successful.\n"
            else:
                result_message += f"❌ Ping test failed: {ping_process.stderr.strip() or ping_process.stdout.strip()}\n"
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            result_message += f"❌ Ping test failed: An error occurred. Error: {e}\n"

        # 4. Azure Application Insights로 로그를 보낼 핸들러 추가
        logger.addHandler(AzureLogHandler(connection_string=data.connection_string))
        
        # 5. 콘솔에 로그를 출력할 핸들러 추가
        console_handler = logging.StreamHandler()
        logger.addHandler(console_handler)

        # 6. 로거의 로그 레벨 설정 (예: INFO 레벨 이상)
        logger.setLevel(logging.INFO)

        # 7. 로그 메시지 전송
        logger.warning('✅ Hello, World!')
        result_message += "✅ Application Insights log sent successfully."
        
    except Exception as e:
        print("❌ 연결 실패:", e)
        result_message += "❌ Connection failed: " + str(e)
        
    return {"message": result_message}