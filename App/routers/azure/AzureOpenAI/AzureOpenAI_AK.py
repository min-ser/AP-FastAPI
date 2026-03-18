from fastapi import FastAPI, Request, APIRouter, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from azure.storage.blob.aio import BlobServiceClient
from openai import AzureOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
import os
templates = Jinja2Templates(directory="templates")
router = APIRouter()

# Pydantic 모델로 요청 본문 데이터 정의
class AzureOpenAI_Info(BaseModel):
    # model_name :str
    openAI_Deployment_ak  : str
    openAI_ModelVersion_ak : str
    openAI_Endpoint_ak    : str
    openAI_Key_ak     : str
    openAI_Message_ak     : str

def create_AzureOpenAI_Client(data):
    try:
        client = AzureOpenAI(
            api_version=data.openAI_ModelVersion_ak,
            azure_endpoint=data.openAI_Endpoint_ak,
            api_key=data.openAI_Key_ak,
        )
    except Exception as e:
        return "Exception : "+str(e)
    return client

def create_AzureOpenAIEmbeddings(data):
    try:
        client = AzureOpenAIEmbeddings(
            model=data.openAI_Deployment_ak,
            deployment=data.openAI_Deployment_ak,
            azure_endpoint=data.openAI_Endpoint_ak,
            api_key=data.openAI_Key_ak,
            api_version=data.openAI_ModelVersion_ak,
            chunk_size=100  # 배치 크기
        )

    except Exception as e:
        return {"message": "Exception : "+str(e)}
    return client

# Ajax 요청을 받을 API 엔드포인트
@router.post("/OpenAI/accesskey")
async def handle_access_key_request(data: AzureOpenAI_Info):
    print(data)
    result_message = ""
    client = create_AzureOpenAI_Client(data)

    try:    
        if data.openAI_Deployment_ak == "text-embedding-3-small":
            response = client.embeddings.create(
                input=["first phrase","second phrase","third phrase"],
                model=data.openAI_Deployment_ak
            )
            for item in response.data:
                length = len(item.embedding)
                result_message += f"data[{item.index}]: length={length}, \n"
                result_message += f"[{item.embedding[0]}, {item.embedding[1]}, \n"
                result_message += f"..., {item.embedding[length-2]}, {item.embedding[length-1]}] \n"
            result_message += str(response.usage)
            return {"message": result_message}
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.",
                },
                {
                    "role": "user",
                    "content": data.openAI_Message_ak,
                }
            ],
            max_completion_tokens=13107,
            temperature=1.0,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            model=data.openAI_Deployment_ak
        )
    except Exception as e:
        # return {"message": "Exception : "+str(e)}
        # 에러 발생 시 400 또는 500 에러를 명시적으로 던짐
        print(f"Error logic triggered: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Azure OpenAI API 호출 실패: {str(e)}"
        )

    print(response.choices[0].message.content)
    result_message = response.choices[0].message.content
    return {"message": result_message}


@router.post("/OpenAI/accesskey/embedding")
async def handle_access_key_request(data: AzureOpenAI_Info):
    print(data)
    result_message = ""
    embeddings = create_AzureOpenAIEmbeddings(data)
    result_message += "create AzureOpenAIEmbeddings instance \n"
    try:
        # Create a vector store with a sample text

        # text = "LangChain is the framework for building context-aware reasoning applications"
        text = data.openAI_Message_ak
        vectorstore = InMemoryVectorStore.from_texts(
            [text],
            embedding=embeddings,
        )

        # Use the vectorstore as a retriever
        retriever = vectorstore.as_retriever()

        # Retrieve the most similar text
        retrieved_documents = retriever.invoke("What is LangChain?")

        # show the retrieved document's content
        retrieved_documents[0].page_content

        single_vector = embeddings.embed_query(text)
    except Exception as e:
        return {"message": "Exception : "+str(e)}
    return {"message": (str(single_vector)[:100])}  # Show the first 100 characters of the vector