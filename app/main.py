from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

load_dotenv()

from app.models import PatientAnalysisRequest, AnalysisResponse
from app.scoring_engine import FunctionalScoringEngine
from app.vector_store import ClinicalVectorStore
from app.llm_service import ClinicalLLMService

app = FastAPI(
    title="Functional Medicine AI CDSS Server",
    description="《진료실에 두고 보는 실전 기능의학》 1~3권 기반 임상 추론 백엔드",
    version="1.0.0"
)

# 인메모리/DB 서비스 인스턴스 초기화
vector_store = ClinicalVectorStore()
llm_service = ClinicalLLMService()

@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_patient_case(request: PatientAnalysisRequest):
    try:
        # 1. 파이썬 룰 엔진을 통한 결정론적 점수 계산 및 랭킹 도출
        evaluated_impressions = FunctionalScoringEngine.evaluate(
            symptoms=request.chief_complaints,
            labs=request.labs,
            gender=request.gender
        )

        if not evaluated_impressions:
            raise HTTPException(status_code=400, detail="유의미한 기능의학적 이상 소견을 도출할 수 없습니다.")

        # 2. 상위 랭킹 질환 코드들에 대한 Vector DB 프로토콜 검색 (RAG)
        top_category_codes = [item["code"] for item in evaluated_impressions[:3]]
        retrieved_protocols = vector_store.retrieve_context(top_category_codes)

        # 3. LLM API 호출 (지식 + 환자 데이터 기반 최종 리포트 합성)
        result_json = llm_service.generate_clinical_report(
            patient=request,
            evaluated_impressions=evaluated_impressions,
            retrieved_protocols=retrieved_protocols
        )

        # 4. 응답 모델 반환
        return AnalysisResponse(
            patient_id=request.patient_id,
            impressions=result_json["impressions"],
            prescriptions=result_json["prescriptions"],
            doctor_chart_summary=result_json["doctor_chart_summary"],
            patient_friendly_report=result_json["patient_friendly_report"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Functional Medicine CDSS Engine"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)