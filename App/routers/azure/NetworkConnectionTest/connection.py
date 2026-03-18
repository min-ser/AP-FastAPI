from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import platform, subprocess, socket

router = APIRouter()

# Pydantic 모델 개선: 모든 필드를 선택사항으로 변경하여 유연성 확보
class DnsInfo(BaseModel):
    dns: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None # 숫자로 처리

@router.post("/NetworkConnection/ping")
async def handle_ping(data: DnsInfo):
    if not data.dns:
        raise HTTPException(status_code=400, detail="DNS/IP is required")
    
    endpoint = data.dns
    try:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '4', endpoint]
        ping_process = subprocess.run(command, capture_output=True, text=True, timeout=10)
        
        if ping_process.returncode == 0:
            return {"message": f"✅ Ping test successful for {endpoint}.\n{ping_process.stdout}"}
        else:
            return {"message": f"❌ Ping test failed.\n{ping_process.stdout}\n{ping_process.stderr}"}
    except Exception as e:
        return {"message": f"❌ Error: {str(e)}"}

@router.post("/NetworkConnection/nslookup")
async def handle_nslookup(data: DnsInfo):
    if not data.dns:
        raise HTTPException(status_code=400, detail="Domain name is required")
    
    endpoint = data.dns
    try:
        ip_address = socket.gethostbyname(endpoint)
        return {"message": f"✅ DNS lookup successful:\n{endpoint} -> {ip_address}"}
    except socket.gaierror:
        return {"message": f"❌ DNS lookup failed: Could not resolve '{endpoint}'"}
    except Exception as e:
        return {"message": f"❌ Error: {str(e)}"}

@router.post("/NetworkConnection/port")
async def access_dns_port(data: DnsInfo):
    host = data.host
    port = data.port
    
    if not host or not port:
        raise HTTPException(status_code=400, detail="Host and Port are required")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3) # 타임아웃 단축
        result = sock.connect_ex((host, int(port)))
        
        if result == 0:
            message = f"✅ Port {port} is OPEN on {host}"
        else:
            message = f"❌ Port {port} is CLOSED/BLOCKED on {host} (Code: {result})"
        sock.close()
        return {"message": message}
    except Exception as e:
        return {"message": f"❌ Port check error: {str(e)}"}