from fastapi import FastAPI, Request, APIRouter, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
import os
templates = Jinja2Templates(directory="templates")
router = APIRouter()

# Pydantic 모델로 요청 본문 데이터 정의
class AzureOpenAI_Info(BaseModel):
    openAI_Deployment_wi    : str
    openAI_ModelVersion_wi  : str
    openAI_Endpoint_wi      : str
    openAI_Message_wi       : str

def create_AzureOpenAI_Client(data):
    try:
        token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
        client = AzureOpenAI(
            api_version=data.openAI_ModelVersion_wi,
            azure_endpoint=data.openAI_Endpoint_wi,
            azure_ad_token_provider=token_provider,
        )
    except Exception as e:
        return "Exception : "+str(e)
    return client

def create_AzureOpenAIEmbeddings(data):
    try:
        token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
        client = AzureOpenAIEmbeddings(
            model=data.openAI_Deployment_wi,
            deployment=data.openAI_Deployment_wi,
            azure_endpoint=data.openAI_Endpoint_wi,
            # api_key=data.openAI_Key_ak,
            azure_ad_token_provider=token_provider,
            api_version=data.openAI_ModelVersion_wi,
            chunk_size=100  # 배치 크기
        )

    except Exception as e:
        return {"message": "Exception : "+str(e)}
    return client

# Ajax 요청을 받을 API 엔드포인트
@router.post("/OpenAI/workloadIdentity")
async def handle_access_key_request(data: AzureOpenAI_Info):
    print(data)
    result_message = ""
    client = create_AzureOpenAI_Client(data)

    try:    
        if data.openAI_Deployment_wi == "text-embedding-3-small":
            response = client.embeddings.create(
                input=["first phrase","second phrase","third phrase"],
                model=data.openAI_Deployment_wi
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
                    "content": data.openAI_Message_wi,
                }
            ],
            max_completion_tokens=13107,
            temperature=1.0,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            model=data.openAI_Deployment_wi
        )
    except Exception as e:
        # return {"message": "Exception : "+str(e)}
        print(f"Error logic triggered: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Azure OpenAI API 호출 실패: {str(e)}"
        )
    print(response.choices[0].message.content)
    result_message = response.choices[0].message.content
    return {"message": result_message}

@router.post("/OpenAI/workloadIdentity/embedding")
async def handle_access_key_request(data: AzureOpenAI_Info):
    print(data)
    result_message = ""
    embeddings = create_AzureOpenAIEmbeddings(data)
    result_message += "create AzureOpenAIEmbeddings instance \n"
    try:
        # Create a vector store with a sample text

        # text = "LangChain is the framework for building context-aware reasoning applications"
        text = data.openAI_Message_wi
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