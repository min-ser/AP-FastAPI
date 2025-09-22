from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter
from pydantic import BaseModel
import os, uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContainerClient

templates = Jinja2Templates(directory="templates")
router = APIRouter()

# Pydantic 모델로 요청 본문 데이터 정의
class AzureStorageAccount_INFO(BaseModel):
    account_url: str

# Ajax 요청을 받을 API 엔드포인트
@router.post("/StorageAccount/workloadIdentity")
def workload_identity(data: AzureStorageAccount_INFO):
    result_message = ""
    try:
        print("Azure Blob Storage Python quickstart sample")
        result_message += "Azure Blob Storage Python quickstart sample" + "\n"
        # account_url = "https://apdevaistaibiz.blob.core.windows.net"
        account_url = data.account_url
        default_credential = DefaultAzureCredential()

        # BlobServiceClient 생성
        blob_service_client = BlobServiceClient(account_url, credential=default_credential)

        # 기존 컨테이너 리스트 출력
        print("\nListing existing containers and their blobs:")
        result_message += "Listing existing containers and their blobs:" + "\n"
        containers = blob_service_client.list_containers()
        for c in containers:
            container_name = c['name']
            print(f"\nContainer: {container_name}")
            result_message += "Container: "+container_name + "\n"
            # ContainerClient 생성
            container_client = blob_service_client.get_container_client(container_name)
            
            # 블롭 리스트 출력
            blob_list = container_client.list_blobs()
            for blob in blob_list:
                print("\t" + blob.name)
                result_message += "\t: "+blob.name + "\n"
    except Exception as ex:
        print('Exception:')
        print(ex)
        result_message += "Exception:" + "\n"
        result_message += ex + "\n"

    return {"message": result_message}