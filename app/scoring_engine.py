from typing import Dict, List, Tuple, Any
from app.models import LabResults

class FunctionalScoringEngine:
    """
    《진료실에 두고 보는 실전 기능의학》 Part 1~3 임상 지표 기반 점수화
    """
    
    @staticmethod
    def evaluate(symptoms: List[str], labs: LabResults, gender: str) -> List[Dict[str, Any]]:
        scores = {
            "SIBO_GUT_DYSBIOSIS": {"score": 0, "evidence": [], "name": "소장내 세균 과증식(SIBO) 및 장 점막 염증"},
            "ADRENAL_EXHAUSTION": {"score": 0, "evidence": [], "name": "부신 피로 및 HPA 축 기능부전"},
            "HISTAMINE_INTOLERANCE": {"score": 0, "evidence": [], "name": "비알레르기성 히스타민 증후군 및 장투과성 이상"},
            "IMMUNE_NK_DEFICIENCY": {"score": 0, "evidence": [], "name": "NK 세포 활성 저하 및 면역 조절 부전 (롱코비드 포함)"},
            "MALE_HYPOGONADISM": {"score": 0, "evidence": [], "name": "남성 갱년기 및 성선 기능 저하증"},
            "CARDIO_VASCULAR_CAC": {"score": 0, "evidence": [], "name": "칼슘 패러독스 및 관상동맥 석회화(CAC) 위험"}
        }

        # 1. SIBO & 장 점막
        if any(s in ["식후 복부팽만", "만성 설사", "만성 변비", "복부 가스", "소화불량"] for s in symptoms):
            scores["SIBO_GUT_DYSBIOSIS"]["score"] += 35
            scores["SIBO_GUT_DYSBIOSIS"]["evidence"].append("주소증: 위장관 소화불량 및 팽만감 호소")
        if labs.fecal_calprotectin and labs.fecal_calprotectin > 11.5:
            scores["SIBO_GUT_DYSBIOSIS"]["score"] += 35
            scores["SIBO_GUT_DYSBIOSIS"]["evidence"].append(f"Calprotectin {labs.fecal_calprotectin} mg/kg (>11.5) 장점막 염증 확인")
        if (labs.sibo_hydrogen_peak and labs.sibo_hydrogen_peak >= 20) or (labs.sibo_methane_peak and labs.sibo_methane_peak >= 10):
            scores["SIBO_GUT_DYSBIOSIS"]["score"] += 40
            scores["SIBO_GUT_DYSBIOSIS"]["evidence"].append("호기검사상 수소/메탄 가스 이상 증폭")

        # 2. 부신 피로 & 미네랄 불균형
        if any(s in ["만성피로", "기립성 어지럼", "오후 방전", "수면장애"] for s in symptoms):
            scores["ADRENAL_EXHAUSTION"]["score"] += 30
            scores["ADRENAL_EXHAUSTION"]["evidence"].append("주소증: 만성 피로 및 기립성 증상")
        if labs.ca_mg_ratio and labs.ca_mg_ratio > 9.5:
            scores["ADRENAL_EXHAUSTION"]["score"] += 35
            scores["ADRENAL_EXHAUSTION"]["evidence"].append(f"모발 Ca/Mg 비 {labs.ca_mg_ratio} (Calcium Shell/만성 스트레스 패턴)")
        if labs.cortisol_8am and labs.cortisol_8am < 10.0:
            scores["ADRENAL_EXHAUSTION"]["score"] += 30
            scores["ADRENAL_EXHAUSTION"]["evidence"].append(f"혈청 아침 Cortisol {labs.cortisol_8am} mcg/dL (부신 3단계 소진 상태)")

        # 3. 비알레르기성 히스타민
        if any(s in ["원인불명 두드러기", "가려움", "홍조", "브레인포그"] for s in symptoms):
            scores["HISTAMINE_INTOLERANCE"]["score"] += 35
            scores["HISTAMINE_INTOLERANCE"]["evidence"].append("주소증: 두드러기, 가려움 및 신경 증상 동반")
        if labs.zinc and labs.zinc < 75:
            scores["HISTAMINE_INTOLERANCE"]["score"] += 20
            scores["HISTAMINE_INTOLERANCE"]["evidence"].append(f"혈청 아연 {labs.zinc} mcg/dL 저하 (점막/면역 방어선 약화)")

        # 4. 면역 & NK 활성
        if any(s in ["롱코비드", "잦은 감기", "구강 궤양", "대상포진"] for s in symptoms):
            scores["IMMUNE_NK_DEFICIENCY"]["score"] += 35
            scores["IMMUNE_NK_DEFICIENCY"]["evidence"].append("주소증: 잦은 감염 및 바이러스 후유증")
        if labs.nk_activity and labs.nk_activity < 330:
            scores["IMMUNE_NK_DEFICIENCY"]["score"] += 45
            scores["IMMUNE_NK_DEFICIENCY"]["evidence"].append(f"NK 세포 활성도 {labs.nk_activity} pg/mL (경계/저하 상태)")
        if labs.vitamin_d and labs.vitamin_d < 20:
            scores["IMMUNE_NK_DEFICIENCY"]["score"] += 20
            scores["IMMUNE_NK_DEFICIENCY"]["evidence"].append(f"비타민 D {labs.vitamin_d} ng/mL 결핍")

        # 5. 남성 갱년기 (남성 한정)
        if gender.upper() == "M":
            if any(s in ["의욕저하 및 성기능 저하", "복부비만", "근력저하"] for s in symptoms):
                scores["MALE_HYPOGONADISM"]["score"] += 30
                scores["MALE_HYPOGONADISM"]["evidence"].append("주소증: 남성 갱년기 증상군 호소")
            if labs.total_testosterone and labs.total_testosterone < 3.5:
                scores["MALE_HYPOGONADISM"]["score"] += 50
                subtype = "1차성(LH상승)" if (labs.lh and labs.lh > 8.0) else "2차성/스트레스성(LH정상/저하)"
                scores["MALE_HYPOGONADISM"]["evidence"].append(
                    f"총 테스토스테론 {labs.total_testosterone} ng/mL (<3.5) 확인 -> {subtype}"
                )

        # 6. CAC & 칼슘 침착
        if labs.cac_agaston_score and labs.cac_agaston_score > 50:
            scores["CARDIO_VASCULAR_CAC"]["score"] += 60
            scores["CARDIO_VASCULAR_CAC"]["evidence"].append(
                f"심장 CT Agaston Score {labs.cac_agaston_score} (관상동맥 석회화 진행 확인)"
            )

        # 점수 기준 내림차순 정렬
        sorted_results = []
        for key, data in sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True):
            if data["score"] > 25: # 유의미한 점수만 추출
                sorted_results.append({
                    "code": key,
                    "category_name": data["name"],
                    "score": data["score"],
                    "evidence": data["evidence"]
                })
        return sorted_results