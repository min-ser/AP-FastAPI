from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from azure.storage.blob import BlobClient
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
import mimetypes, base64

router = APIRouter()

class AzureStorageAccount_INFO(BaseModel):
    account_url: str        # 예: "https://<account>.blob.core.windows.net"
    container_name: str     # 예: "mycontainer"
    blob_dir: str           # 예: "images/test.png" (디렉토리 포함 전체 경로)

def get_blob_client(account_url: str, container_name: str, blob_path: str) -> BlobClient:
    credential = DefaultAzureCredential()
    return BlobClient(
        account_url=account_url,
        container_name=container_name,
        blob_name=blob_path,   # blob_dir을 그대로 blob_name으로 사용
        credential=credential
    )

@router.post("/StorageAccount/get-image")
async def get_image(data: AzureStorageAccount_INFO):
    try:
        blob_client = get_blob_client(
            data.account_url,
            data.container_name,
            data.blob_dir   # 여기서 blob_dir이 곧 blob의 전체 경로
        )
        blob_data = blob_client.download_blob().readall()

        mime_type = mimetypes.guess_type(data.blob_dir)[0] or "application/octet-stream"

        return Response(content=blob_data, media_type=mime_type)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blob 다운로드 실패: {str(e)}")


client = AzureOpenAI(
    api_version="",
    azure_endpoint="",
    api_key="",
)

def analyze_image_with_llm(blob_data: bytes, prompt: str):
    # blob_data → base64 변환
    image_base64 = base64.b64encode(blob_data).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4",  # 또는 gpt-4o
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that can analyze images."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=300
    )

    # result = client.images.generate(
    #     model="dall-e-3",
    #     prompt="이 사진을 만화 스타일로 바꿔줘",
    #     size="1024x1024"
    # )
    result_message = response.choices[0].message.content
    # image_url = result.data[0].url
    print(response.choices[0].message.content)
    # return {"result_message":result_message, "result_image":image_url}
    return {"result_message":result_message}


@router.post("/StorageAccount/get-image-and-analyze")
async def get_image_and_analyze(data: AzureStorageAccount_INFO, prompt: str = "이 이미지를 설명해줘"):
    try:
        # 1. Blob에서 바이너리 데이터 다운로드
        blob_client = get_blob_client(
            data.account_url,
            data.container_name,
            data.blob_dir
        )
        blob_data = blob_client.download_blob().readall()

        # 2. LLM 분석 수행 (GPT 답변)
        llm_result_text = analyze_image_with_llm(blob_data, prompt)
        # 3. 이미지 데이터를 Base64 문자열로 변환
        image_base64 = base64.b64encode(blob_data).decode("utf-8")
        
        # 4. MIME 타입 추정 (클라이언트에서 data URL을 생성하는 데 필요)
        mime_type = mimetypes.guess_type(data.blob_dir)[0] or "application/octet-stream"
        
        # 5. GPT 답변과 Base64 데이터를 포함한 JSON 반환
        return {
            "message": llm_result_text["result_message"], 
            "image_base64": image_base64,
            "mime_type":mime_type}
        # return {"message": result["result_message"]}

    except Exception as e:
        print("Exception : ",e)
        raise HTTPException(status_code=500, detail=f"분석 실패: {str(e)}")