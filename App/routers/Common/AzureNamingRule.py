import logging
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ResourceInfo(BaseModel):
    env: str
    resource_type: str
    service_name: Optional[str] = None
    target_resource_type: Optional[str] = None
    target_service_name: Optional[str] = None

@router.post("/common/CreateResourceName")
async def create_resource_name(data: ResourceInfo):
    try:
        env = data.env.lower()
        r_type = data.resource_type.lower()
        service = (data.service_name or "").strip()
        
        env_ai = f"ap{env}ai"    # apdevai
        env_hyphen = f"ap-{env}"  # ap-dev

        generated_name = ""
        pep_name = None
        rule_msg = ""

        # [추가] PEP 생성이 불필요한 리소스 타입 정의
        # vnet, snet, nsg, pip, waf, rg, subsc 등은 PEP를 생성하지 않음
        PEP_EXCLUDE_TYPES = {"vnet", "snet", "nsg", "pip", "waf", "rg", "subsc", "plan"}

        # A. PEP 단독 생성 (이미지 규정 4항)
        if r_type == "pep":
            t_type = (data.target_resource_type or "").upper()
            t_service = (data.target_service_name or "").upper()
            generated_name = f"{env_ai}-pep-{t_type}-{t_service}".upper()
            rule_msg = "이미지 규정 4항: Private Endpoint 전용 구조 (전체 대문자)"

        # B. AI Foundry (제3조 4항) - PEP 필요
        elif r_type in ["aif", "mlw"]:
            generated_name = f"{env_ai}-{service.lower()}"
            pep_name = f"{env_ai}-pep-{r_type.upper()}-{service.upper()}".upper()
            rule_msg = "제3조 4항: AI Foundry (유형 약어 생략 및 PEP 대문자 생성)"

        # C. Storage Account (제3조 3항) - PEP 필요
        elif r_type == "sa":
            clean_svc = service.lower().replace("-", "")
            generated_name = f"{env_ai}{r_type}{clean_svc}"
            pep_name = f"{env_ai}-pep-SA-{service.upper()}".upper()
            rule_msg = "제3조 3항: Storage (구분자 미사용 및 PEP 대문자 생성)"

        # D. 특수 구조 및 네트워크 인프라 (PEP 제외 대상)
        elif r_type in PEP_EXCLUDE_TYPES:
            if r_type in ["rg", "subsc"]:
                generated_name = f"{env_hyphen}-{service.lower()}-{r_type}"
            else:
                generated_name = f"{env_ai}-{r_type}-{service.lower()}"
            
            pep_name = None  # PEP 생성 안 함
            rule_msg = f"제3조: {r_type.upper()}는 PEP 생성 제외 리소스입니다."

        # E. 일반 리소스 (Redis, SQL, OpenAI 등 - PEP 필요)
        else:
            generated_name = f"{env_ai}-{r_type}-{service.lower()}"
            pep_name = f"{env_ai}-pep-{r_type.upper()}-{service.upper()}".upper()
            rule_msg = "제3조 1항: 일반 리소스 표준 구조 (PEP 대문자 생성)"

        return {
            "generated_name": generated_name,
            "pep_name": pep_name,
            "rule_info": rule_msg
        }

    except Exception as e:
        logging.error(f"Naming Error: {str(e)}")
        return {"message": f"서버 오류: {str(e)}"}, 500