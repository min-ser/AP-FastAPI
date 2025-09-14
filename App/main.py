from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# router 등록
from routers.theme import theme
from routers.azure import azure

app = FastAPI()
app.include_router(theme.router)
app.include_router(azure.router)

# 정적파일 등록
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")