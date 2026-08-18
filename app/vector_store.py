import os
from typing import List, Dict, Any
import chromadb
from chromadb.utils import embedding_functions

CHROMA_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_data")

class ClinicalVectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DIR)
        
        # OpenAI API 호출 대신 ChromaDB 내장 기본 무료 임베딩 사용 (API 키/크레딧 불필요)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        self.collection = self.client.get_or_create_collection(
            name="functional_medicine_protocols",
            embedding_function=self.embedding_fn
        )
        self._seed_default_protocols_if_empty()

    def _seed_default_protocols_if_empty(self):
        """책 1~3권의 핵심 임상 프로토콜 초기 시드 데이터"""
        if self.collection.count() == 0:
            docs = [
                # SIBO
                "SIBO 및 장 점막 염증 치료 프로토콜: 1단계 Rifaximin(노르믹스) 200mg 2T tid 2~4주 투여. "
                "장점막 손상 및 Calprotectin 상승 시 L-Glutamine, 락토페린, 아르기닌 수액을 선행 또는 병용. "
                "소화효소제 병용 필수. IVNT는 마이어스 베이스에 글루타치온 600~1200mg Side 투여 권장.",
                # 부신피로
                "부신피로 2~3단계 및 HPA 축 소진 치료: 0.9% NS 250mL 베이스에 Megacorbin-C 10g + Bicarb 8mL + "
                "Magnesium Sulfate 10% 2g + Dexpan 2,000mg + Thiamine 50mg + Bidoxin 200mg + 감초주사 40mL 혼합. "
                "속도 150~200mL/hr. 부신 영양제로 Adaptogen 및 인지질 제제 추천.",
                # 히스타민
                "비알레르기성 히스타민 증후군(MUS) 치료: 5R 프로그램 적용. 노르믹스 제균 + 알레그라(Fexofenadine) 180mg qd 병용. "
                "IgG4 양성 음식 철저 제한. DAO 활성을 위한 Vit B6, 아연 보충.",
                # 면역
                "면역력 개선 및 롱코비드 프로토콜: NK 활성 330 미만 시 싸이모신 알파 1(Immun alpha) 1.6mg SC 주 1~2회(총 8회 이상). "
                "이스미젠 설하정 10일 복용/20일 휴약 3개월 요법. 비타민 D 20만 IU IM + 아연 경구 보충.",
                # 남성호르몬
                "남성 성선기능저하증(TRT): Total Testosterone 3.5 미만 시 1차성은 네비도(Nebido 1,000mg) 1차 투여 후 6주, "
                "이후 10~12주 간격 유지. 2차성/가임력 보존 필요 시 클로미펜 25~50mg qd 고려. Hct > 52% 모니터링.",
                # 관상동맥 석회화
                "관상동맥 석회화(CAC) 및 골다공증 칼슘 패러독스 치료: 비타민 K2(MK-7) 360mcg/day 투여(Matrix Gla Protein 활성화). "
                "비타민 D3 + K2 복합제 + 오메가3 2~4g 병용. 심근 산소효율 개선을 위해 바스티난(Trimetazidine) 20mg bid 고려."
            ]
            ids = [
                "SIBO_GUT_DYSBIOSIS",
                "ADRENAL_EXHAUSTION",
                "HISTAMINE_INTOLERANCE",
                "IMMUNE_NK_DEFICIENCY",
                "MALE_HYPOGONADISM",
                "CARDIO_VASCULAR_CAC"
            ]
            metadatas = [{"category": i} for i in ids]
            self.collection.add(documents=docs, ids=ids, metadatas=metadatas)

    def retrieve_context(self, category_codes: List[str]) -> str:
        results = self.collection.get(ids=category_codes)
        return "\n\n".join(results.get("documents", []))