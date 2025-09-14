from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# router 등록
from routers.theme import theme
from routers.azure import azure
from routers.azure.AzureCacheForRedis   import AccessKey          as redis_ak
from routers.azure.AzureCacheForRedis   import Managed_Identity   as redis_mi
from routers.azure.AzureCacheForRedis   import Workload_Identity  as redis_wi
from routers.azure.AzureStorageAccount  import AccessKey          as st_ak
from routers.azure.AzureStorageAccount   import Managed_Identity  as st_mi
from routers.azure.AzureStorageAccount  import Workload_Identity  as st_wi

app = FastAPI()
app.include_router(theme.router)
app.include_router(azure.router)
app.include_router(redis_ak.router)
app.include_router(redis_wi.router)
app.include_router(st_ak.router)
app.include_router(st_wi.router)

# 정적파일 등록
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")