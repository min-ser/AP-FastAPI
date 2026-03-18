from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
# from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential, AzureAuthorityHosts
from azure.search.documents.indexes import SearchIndexClient
from app.routers.azure.AzureAISearch import index_crud

import os
templates = Jinja2Templates(directory="templates")
router = APIRouter()
audience = "https://search.azure.com"
authority = AzureAuthorityHosts.AZURE_PUBLIC_CLOUD

# Pydantic 모델로 요청 본문 데이터 정의
class AzureAISearch_Info(BaseModel):
    aisearch_endpoint : str
    # aisearch_key_wi : str = None
    # aisearch_index_name_wi 필드는 이 모델에서 제거하거나 선택적으로 만듭니다.
    # 만약 혹시라도 프론트에서 Index Name을 보낼 수도 있다면 Optional로 처리합니다.
    aisearch_index_name : Optional[str] = None
    aisearch_index_config : Optional[str] = None

def create_AzureAISearch_Client(data):
    try:
        # DefaultAzureCredential을 사용하여 인증
        # credential = DefaultAzureCredential()
        credential = DefaultAzureCredential(authority=authority)
        client = SearchIndexClient(
            # AISearch 엔드포인트를 URL 형식으로 제공
            data.aisearch_endpoint, 
            credential = credential,
            audience=audience
        )
        print("Create Azure AI Search Client with Azure AD...")
    except Exception as e:
        return "Exception : "+str(e)
    return client

# Ajax 요청을 받을 API 엔드포인트
@router.post("/AISearch/WI/index/list")
async def ais_wi_index_list(data: AzureAISearch_Info):
    print(data)
    result_message = ""
    try:    
        client = create_AzureAISearch_Client(data)
        result_message += index_crud.get_index_list(data,client)
    except Exception as e:
        return {"message": "Exception : "+str(e)}
    return {"message": result_message}

@router.post("/AISearch/WI/index/read")
async def ais_wi_index_read(data: AzureAISearch_Info):
    print(data)
    result_message = "[/AISearch/WI/index/read]\n"
    try:    
        client = create_AzureAISearch_Client(data)
        result_message += index_crud.get_index(data,client)
    except Exception as e:
        return {"message": "Exception : "+str(e)}
    return {"message": result_message}

@router.post("/AISearch/WI/index/create")
async def ais_wi_index_create(data: AzureAISearch_Info):
    print(data)
    result_message = "[/AISearch/WI/index/create]\n"
    try:    
        client = create_AzureAISearch_Client(data)
        result_message += index_crud.create_index(data,client)
    except Exception as e:
        return {"message": "Exception : "+str(e)}
    return {"message": result_message}

@router.post("/AISearch/WI/index/update")
async def ais_wi_index_update(data: AzureAISearch_Info):
    print(data)
    result_message = "[/AISearch/WI/index/update]\n"
    try:    
        client = create_AzureAISearch_Client(data)
        result_message += "UPDATE 기능 보류"
        # result_message += index_crud.update_index(data,client)
    except Exception as e:
        return {"message": "Exception : "+str(e)}
    return {"message": result_message}

@router.post("/AISearch/WI/index/delete")
async def ais_wi_index_delete(data: AzureAISearch_Info):
    print(data)
    result_message = "[/AISearch/WI/index/delete]\n"
    try:    
        client = create_AzureAISearch_Client(data)
        result_message += index_crud.delete_index(data,client)
    except Exception as e:
        return {"message": "Exception : "+str(e)}
    return {"message": result_message}