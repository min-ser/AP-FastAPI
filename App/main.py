import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# 절대경로 import로 수정 (app 폴더 기준)
from app.routers.theme import theme
from app.routers.azure import azure
from app.routers.azure.AzureCacheForRedis import AccessKey as redis_ak
from app.routers.azure.AzureCacheForRedis import Managed_Identity as redis_mi
from app.routers.azure.AzureCacheForRedis import Workload_Identity as redis_wi
from app.routers.azure.AzureStorageAccount import AccessKey as st_ak
from app.routers.azure.AzureStorageAccount import Managed_Identity as st_mi
from app.routers.azure.AzureStorageAccount import Workload_Identity as st_wi
from app.routers.azure.AzureAIFoundry import entra
from app.routers.azure.AzureApplicationInsights import ConnectionTest
from app.routers.azure.NetworkConnectionTest import connection

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(theme.router)
app.include_router(azure.router)
app.include_router(redis_ak.router)
app.include_router(redis_wi.router)
app.include_router(st_ak.router)
app.include_router(st_wi.router)
app.include_router(entra.router)
app.include_router(ConnectionTest.router)
app.include_router(connection.router)
