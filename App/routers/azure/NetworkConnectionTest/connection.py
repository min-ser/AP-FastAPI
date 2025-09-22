from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import platform, subprocess, socket
templates = Jinja2Templates(directory="templates")
router = APIRouter()

# Pydantic 모델로 요청 본문 데이터 정의
class DnsInfo(BaseModel):
    dns: str

# Ajax 요청을 받을 API 엔드포인트
@router.post("/NetworkConnection/ping")
async def handle_access_key_request(data: DnsInfo):
    result_message = ""
    endpoint = data.dns
    try:
        # 3. Ping 테스트
        # OS에 따라 Ping 명령 옵션 조정
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '4', endpoint]
        ping_process = subprocess.run(command, capture_output=True, text=True, timeout=10)
        if ping_process.returncode == 0:
            result_message += "✅ Ping test successful.\n"
        else:
            result_message += f"❌ Ping test failed: {ping_process.stderr.strip() or ping_process.stdout.strip()}\n"
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        result_message += f"❌ Ping test failed: An error occurred. Error: {e}\n"
    except Exception as e:
        result_message = "Exception : "+str(e)
    return {"message": result_message}

@router.post("/NetworkConnection/nslookup")
async def handle_access_key_request(data: DnsInfo):
    result_message = ""
    endpoint = data.dns
    try:
        result_message += "DNS : "+data.dns + "\n"
        ip_address = socket.gethostbyname(endpoint)
        result_message += f"✅ DNS lookup successful: {endpoint} -> {ip_address}\n"
    except socket.gaierror as e:
            result_message += f"❌ DNS lookup failed: Could not resolve '{endpoint}'. Error: {e}\n"
    except Exception as e:
        result_message = "Exception : "+str(e)
    return {"message": result_message}