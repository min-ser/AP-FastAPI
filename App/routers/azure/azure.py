from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter
from app.config import templates

# templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/base", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(name="azure/base.html", context={"request": request, "title": "test"})

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("azure/index.html", context={"request": request, "title": "Dashboard", "subtitle" : "Control panel"})

@router.get("/index2", response_class=HTMLResponse)
def index2(request: Request):
    return templates.TemplateResponse(name="azure/index2.html", context={"request": request, "title": "Dashboard2", "subtitle" : "Control panel"})

# Azure
@router.get("/azure/StorageAccount", response_class=HTMLResponse)
def azure_st(request: Request):
    return templates.TemplateResponse(name="azure/pages/AzureStorageAccount.html", context={"request": request, "title": "Azure","subtitle" : "Storage Account"})

@router.get("/azure/Redis", response_class=HTMLResponse)
def azure_redis(request: Request):
    return templates.TemplateResponse(name="azure/pages/AzureCacheForRedis.html", context={"request": request, "title": "Azure","subtitle" : "Cache For Redis"})

@router.get("/azure/AIFoundry", response_class=HTMLResponse)
def azure_redis(request: Request):
    return templates.TemplateResponse(name="azure/pages/AzureAIFoundry.html", context={"request": request, "title": "Azure","subtitle" : "AI Foundry"})

@router.get("/azure/DataBase", response_class=HTMLResponse)
def azure_db(request: Request):
    return templates.TemplateResponse(name="azure/pages/AzureDataBase.html", context={"request": request, "title": "Azure","subtitle" : "DataBase"})

@router.get("/azure/ApplicationInsights", response_class=HTMLResponse)
def azure_db(request: Request):
    return templates.TemplateResponse(name="azure/pages/AzureApplicationInsights.html", context={"request": request, "title": "Azure","subtitle" : "ApplicationInsights"})

@router.get("/NetworkConnectionTest", response_class=HTMLResponse)
def azure_db(request: Request):
    return templates.TemplateResponse(name="azure/pages/NetworkConnectionTest.html", context={"request": request, "title": "ALL","subtitle" : "Network Connection Test"})

