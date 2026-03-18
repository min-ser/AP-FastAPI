import os, logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

# 절대경로 import로 수정 (app 폴더 기준)
from app.routers.theme import theme
from app.routers.azure import azure
from app.routers.azure.AzureCacheForRedis import AccessKey as redis_ak
from app.routers.azure.AzureCacheForRedis import Workload_Identity as redis_wi
from app.routers.azure.AzureCacheForRedis import TTL_Check
from app.routers.azure.AzureStorageAccount import AccessKey as st_ak
from app.routers.azure.AzureStorageAccount import Managed_Identity as st_mi
from app.routers.azure.AzureStorageAccount import Workload_Identity as st_wi
from app.routers.azure.AzureStorageAccount import image as st_image
from app.routers.azure.AzureAIFoundry import entra
from app.routers.azure.AzureAISearch import AIS_AK
from app.routers.azure.AzureAISearch import AIS_WI
from app.routers.azure.AzureOpenAI import AzureOpenAI_AK,AzureOpenAI_WI
from app.routers.azure.AzureApplicationInsights import ConnectionTest
from app.routers.azure.NetworkConnectionTest import connection
from app.routers.Common import AzureNamingRule

app = FastAPI()

# 1. BASE_DIR 정의 (현재 main.py의 위치:)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. templates 경로를 절대 경로로 설정
# app/templates 폴더를 가리키게 됩니다.
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
# templates = Jinja2Templates(directory="templates")

# 3. static 경로 설정 (기존 코드 유지 또는 확인)
static_dir = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(theme.router)
app.include_router(azure.router)
app.include_router(redis_ak.router)
app.include_router(redis_wi.router)
app.include_router(TTL_Check.router)
app.include_router(st_ak.router)
app.include_router(st_wi.router)
app.include_router(st_image.router)
app.include_router(entra.router)
app.include_router(ConnectionTest.router)
app.include_router(connection.router)
app.include_router(AzureOpenAI_AK.router)
app.include_router(AzureOpenAI_WI.router)
app.include_router(AIS_AK.router)
app.include_router(AIS_WI.router)
app.include_router(AzureNamingRule.router)

# 404 에러 핸들러 (기존)
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse("azure/common/404.html", {"request": request}, status_code=404)
    if exc.status_code >= 500:
        return templates.TemplateResponse("azure/common/500.html", {"request": request}, status_code=500)
    return await http_exception_handler(request, exc)

# 500 에러 핸들러 (코드 실행 중 발생하는 모든 예외 처리)
@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    # 콘솔에 에러 로그 출력 (디버깅용)
    logging.error(f"Internal Server Error: {exc}")
    
    return templates.TemplateResponse(
        "azure/common/500.html", 
        {"request": request, "error_details": str(exc)}, # 필요한 경우 에러 메시지 전달
        status_code=500
    )