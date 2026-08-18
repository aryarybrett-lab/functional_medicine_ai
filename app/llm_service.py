# app/llm_service.py
import os
import json
from typing import Dict, List, Any
from openai import OpenAI
from app.models import PatientAnalysisRequest

OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

class ClinicalLLMService:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_KEY)

    def generate_clinical_report(
        self, 
        patient: PatientAnalysisRequest, 
        evaluated_impressions: list, 
        retrieved_protocols: str
    ) -> Dict:
        system_prompt = """
        당신은 《진료실에 두고 보는 실전 기능의학》에 기반한 전문 CDSS(임상 의사결정 지원 시스템) 엔진입니다.
        규칙 엔진에서 산출된 Impression 순위와 책의 프로토콜 텍스트를 바탕으로 정밀한 기능의학 진단 및 처방 JSON을 작성하세요.

        [반환 형식 요구사항 (JSON Schema)]
        {
          "impressions": [
            {
              "rank": 1,
              "category_name": "질환/불균형 카테고리명",
              "score": 90.0,
              "pathophysiology": "증상과 검사 수치가 왜 이 질환을 가리키는지 병태생리 설명",
              "matching_evidence": ["근거1", "근거2"]
            }
          ],
          "prescriptions": [
            {
              "category": "IVNT 또는 ORAL_RX 또는 SUPPLEMENT",
              "name": "약제/수액명",
              "dosage": "정확한 용량",
              "usage": "투여 속도 및 복용법",
              "duration": "치료 기간",
              "notes": "주의사항 및 모니터링 지표"
            }
          ],
          "doctor_chart_summary": "EMR에 바로 복사할 수 있는 의사용 SOAP 차팅 요약문",
          "patient_friendly_report": "환자가 100% 납득할 수 있는 대사 공장/배터리 비유 기반 설명문"
        }
        """

        user_content = f"""
        [환자 정보]
        - ID: {patient.patient_id} / 나이: {patient.age}세 / 성별: {patient.gender}
        - 주소증: {', '.join(patient.chief_complaints)}
        - 검사 수치: {patient.labs.model_dump(exclude_none=True) if patient.labs else {}}

        [1차 룰 엔진 평가 순위]
        {json.dumps(evaluated_impressions, ensure_ascii=False, indent=2)}

        [책에서 검색된 실전 처방 프로토콜 지식]
        {retrieved_protocols}
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            temperature=0.1,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]
        )

        raw_json = response.choices[0].message.content
        return json.loads(raw_json)
