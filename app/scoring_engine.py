# app/scoring_engine.py
from typing import Dict, List, Tuple, Any
from app.models import LabResults

class FunctionalMedicineScoringEngine:
    def __init__(self):
        # 기능의학적 최적 밴드 기준
        self.OPTIMAL_RANGES = {
            "homocysteine_optimal": 8.0,      # > 9.0부터 메틸레이션 결손/혈관독성 경고
            "homocysteine_high": 12.0,        # > 12.0 고위험
            "homa_ir_optimal": 1.5,           # > 2.0 인슐린 저항성 시작
            "homa_ir_high": 2.5,              # > 2.5 뚜렷한 대사증후군/당뇨 전단계
            "hs_crp_optimal": 0.5,            # > 1.0 전신 미세염증
            "calprotectin_optimal": 11.5,
            "ca_mg_optimal_high": 10.0,
            "total_testosterone_low": 3.5,
            "vitamin_d_optimal": 40.0,
            "nk_activity_optimal": 500.0,
            "nk_activity_borderline": 330.0
        }

    def evaluate(self, complaints: List[str], labs: LabResults) -> List[Dict[str, Any]]:
        categories = {
            # ➕ 신규 카테고리: 대사증후군 및 인슐린 저항성
            "INSULIN_RESISTANCE_METABOLIC": {
                "name": "인슐린 저항성 및 대사 증후군 (HOMA-IR 상승)",
                "score": 0.0,
                "evidence": []
            },
            # ➕ 신규 카테고리: 고호모시스테인혈증 및 메틸레이션 장애
            "METHYLATION_DEFECT_VASCULAR": {
                "name": "고호모시스테인혈증 및 혈관 내피세포 독성 (메틸레이션 결손)",
                "score": 0.0,
                "evidence": []
            },
            # 기존 카테고리들
            "SIBO_GUT_DYSBIOSIS": {
                "name": "소장내 세균 과증식(SIBO) 및 장 점막 염증",
                "score": 0.0,
                "evidence": []
            },
            "ADRENAL_EXHAUSTION": {
                "name": "부신 피로 및 HPA 축 기능부전",
                "score": 0.0,
                "evidence": []
            },
            "MALE_HYPOGONADISM": {
                "name": "남성 갱년기 및 성선 기능 저하증",
                "score": 0.0,
                "evidence": []
            },
            "IMMUNE_NK_DEFICIENCY": {
                "name": "NK 세포 활성 저하 및 면역 조절 부전",
                "score": 0.0,
                "evidence": []
            }
        }

        # ----------------------------------------------------
        # 1. HOMA-IR 인슐린 저항성 평가
        # ----------------------------------------------------
        calc_homa_ir = None
        if labs and labs.homa_ir is not None:
            calc_homa_ir = labs.homa_ir
        elif labs and labs.fasting_glucose and labs.fasting_insulin:
            # HOMA-IR 자동 계산 공식: (Glucose * Insulin) / 405
            calc_homa_ir = round((labs.fasting_glucose * labs.fasting_insulin) / 405.0, 2)

        if calc_homa_ir:
            if calc_homa_ir >= self.OPTIMAL_RANGES["homa_ir_high"]:
                categories["INSULIN_RESISTANCE_METABOLIC"]["score"] += 60.0
                categories["INSULIN_RESISTANCE_METABOLIC"]["evidence"].append(
                    f"HOMA-IR {calc_homa_ir} (>=2.5 고위험 인슐린 저항성 확인)"
                )
            elif calc_homa_ir >= self.OPTIMAL_RANGES["homa_ir_optimal"]:
                categories["INSULIN_RESISTANCE_METABOLIC"]["score"] += 40.0
                categories["INSULIN_RESISTANCE_METABOLIC"]["evidence"].append(
                    f"HOMA-IR {calc_homa_ir} (기능의학 최적 기준 1.5 초과)"
                )

        # ----------------------------------------------------
        # 2. 호모시스테인 및 메틸레이션 평가
        # ----------------------------------------------------
        if labs and labs.homocysteine:
            if labs.homocysteine >= self.OPTIMAL_RANGES["homocysteine_high"]:
                categories["METHYLATION_DEFECT_VASCULAR"]["score"] += 65.0
                categories["METHYLATION_DEFECT_VASCULAR"]["evidence"].append(
                    f"Serum Homocysteine {labs.homocysteine} umol/L (>=12.0 심혈관/뇌혈관 고위험 밴드)"
                )
            elif labs.homocysteine >= self.OPTIMAL_RANGES["homocysteine_optimal"]:
                categories["METHYLATION_DEFECT_VASCULAR"]["score"] += 40.0
                categories["METHYLATION_DEFECT_VASCULAR"]["evidence"].append(
                    f"Serum Homocysteine {labs.homocysteine} umol/L (기능의학 최적치 8.0 초과, 메틸레이션 저하)"
                )

        # ----------------------------------------------------
        # 3. hs-CRP 미세염증 복합 가산
        # ----------------------------------------------------
        if labs and labs.hs_crp and labs.hs_crp >= self.OPTIMAL_RANGES["hs_crp_optimal"]:
            categories["INSULIN_RESISTANCE_METABOLIC"]["score"] += 15.0
            categories["METHYLATION_DEFECT_VASCULAR"]["score"] += 15.0
            categories["INSULIN_RESISTANCE_METABOLIC"]["evidence"].append(
                f"hs-CRP {labs.hs_crp} mg/L (혈관 전신 미세염증 동반)"
            )

        # ----------------------------------------------------
        # 4. 주소증 가산
        # ----------------------------------------------------
        for symptom in complaints:
            if any(k in symptom for k in ["체중증가", "복부비만", "식곤증", "당뇨", "지방간"]):
                categories["INSULIN_RESISTANCE_METABOLIC"]["score"] += 25.0
                categories["INSULIN_RESISTANCE_METABOLIC"]["evidence"].append(f"주소증: {symptom} (대사 이상 시그널)")
            
            if any(k in symptom for k in ["가슴답답", "두통", "브레인포그", "기억력저하", "혈액순환"]):
                categories["METHYLATION_DEFECT_VASCULAR"]["score"] += 20.0
                categories["METHYLATION_DEFECT_VASCULAR"]["evidence"].append(f"주소증: {symptom} (혈관/신경 염증 소견)")

            # 기존 주소증 로직
            if any(k in symptom for k in ["복부팽만", "가스", "소화불량", "설사"]):
                categories["SIBO_GUT_DYSBIOSIS"]["score"] += 20.0
            if any(k in symptom for k in ["피로", "어지럼", "기립성"]):
                categories["ADRENAL_EXHAUSTION"]["score"] += 20.0
            if any(k in symptom for k in ["성기능", "의욕저하", "근력감소"]):
                categories["MALE_HYPOGONADISM"]["score"] += 25.0

        # 기존 검사 지표 평가 (Calprotectin, Ca/Mg, Testosterone 등)
        if labs:
            if labs.fecal_calprotectin and labs.fecal_calprotectin > self.OPTIMAL_RANGES["calprotectin_optimal"]:
                categories["SIBO_GUT_DYSBIOSIS"]["score"] += 50.0
                categories["SIBO_GUT_DYSBIOSIS"]["evidence"].append(f"Calprotectin {labs.fecal_calprotectin} mg/kg 장점막 염증")
            if labs.ca_mg_ratio and labs.ca_mg_ratio > self.OPTIMAL_RANGES["ca_mg_optimal_high"]:
                categories["ADRENAL_EXHAUSTION"]["score"] += 45.0
                categories["ADRENAL_EXHAUSTION"]["evidence"].append(f"Ca/Mg 비 {labs.ca_mg_ratio} (Calcium Shell/만성 스트레스)")
            if labs.total_testosterone and labs.total_testosterone < self.OPTIMAL_RANGES["total_testosterone_low"]:
                categories["MALE_HYPOGONADISM"]["score"] += 55.0
                categories["MALE_HYPOGONADISM"]["evidence"].append(f"Total Testosterone {labs.total_testosterone} ng/mL 저하")

        # 점수 기준 정렬 및 상위 항목 추출
        results = []
        for code, data in categories.items():
            if data["score"] > 0:
                results.append({
                    "code": code,
                    "category_name": data["name"],
                    "score": min(data["score"], 100.0),
                    "evidence": data["evidence"]
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results
