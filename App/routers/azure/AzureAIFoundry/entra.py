from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter
from pydantic import BaseModel

import asyncio
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

templates = Jinja2Templates(directory="templates")
router = APIRouter()

# Pydantic 모델로 요청 본문 데이터 정의
class AIFoundryInfo(BaseModel):
    project_endpoint: str

async def create_client(data: AIFoundryInfo):
    project_client = None
    try:
        project_client = AIProjectClient(
                credential=DefaultAzureCredential(),
                endpoint=data.project_endpoint,
            )
    except Exception as e:
        print(f"An error occurred while listing agents: {e}")
        result_message += "An error occurred while listing agents:" + "\n"
        result_message += str(e) + "\n"
    return project_client, result_message

@router.post("/AIFoundry/agent_list")
async def agent_list(data: AIFoundryInfo):
    print(data)
    result_message = ""
    try:
        project_client = AIProjectClient(
                credential=DefaultAzureCredential(),
                endpoint=data.project_endpoint,
            )
        # project_client, result_message = create_client(data, result_message)
        # 생성된 에이전트 리스트 조회
        result_message += "생성된 Agent List 조회"+"\n"
        agent_list = project_client.agents.list_agents()
        if agent_list:
            async for agent in agent_list:
                print(f"- Agent Name: {agent.name}, Agent ID: {agent.id}")
                result_message += "- Agent Name:" + agent.name + ", Agent ID:"+ agent.id + "\n"
        else:
            print("No agents found.")
            result_message += "No agents found."+"\n"
    except Exception as e:
        print(e)
        result_message += str(e)
    return {"message": result_message}


@router.post("/AIFoundry/create_agent")
async def agent_list(data: AIFoundryInfo):
    result_message = ""
    return {"message": result_message}

@router.post("/AIFoundry/delete_agent")
async def agent_list(data: AIFoundryInfo):
    result_message = ""
    return {"message": result_message}