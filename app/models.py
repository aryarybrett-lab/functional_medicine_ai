from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class LabResults(BaseModel):
    # 일반 혈액/생화학/염증
    ast: Optional[float] = None
    alt: Optional[float] = None
    ggt: Optional[float] = None
    ferritin: Optional[float] = None
    fibrinogen: Optional[float] = None
    homa_ir: Optional[float] = None
    vitamin_d: Optional[float] = None # ng/mL
    zinc: Optional[float] = None      # mcg/dL
    
    # 호르몬/부신
    cortisol_8am: Optional[float] = None
    dhea_s: Optional[float] = None
    total_testosterone: Optional[float] = None # ng/mL
    lh: Optional[float] = None
    
    # 모발 미네랄 및 중금속
    ca_mg_ratio: Optional[float] = None
    na_k_ratio: Optional[float] = None
    na_mg_ratio: Optional[float] = None
    mercury_hg: Optional[float] = None
    lead_pb: Optional[float] = None
    
    # 특수 기능의학 검사
    nk_activity: Optional[float] = None       # pg/mL
    fecal_calprotectin: Optional[float] = None # mg/kg
    sibo_hydrogen_peak: Optional[float] = None # ppm
    sibo_methane_peak: Optional[float] = None  # ppm
    cac_agaston_score: Optional[float] = None  # 심장 CT 관상동맥 석회화

class PatientAnalysisRequest(BaseModel):
    patient_id: str = Field(..., example="PT-2026-001")
    age: int = Field(..., example=48)
    gender: str = Field(..., example="M") # "M" or "F"
    chief_complaints: List[str] = Field(
        ..., 
        example=["만성피로", "식후 복부팽만", "기립성 어지럼", "원인불명 두드러기", "의욕저하 및 성기능 저하"]
    )
    labs: LabResults

class PrescriptionItem(BaseModel):
    category: str # "IVNT", "ORAL_RX", "SUPPLEMENT"
    name: str
    dosage: str
    usage: str
    duration: Optional[str] = None
    notes: Optional[str] = None

class ImpressionResult(BaseModel):
    rank: int
    category_name: str
    score: float
    pathophysiology: str
    matching_evidence: List[str]

class AnalysisResponse(BaseModel):
    patient_id: str
    impressions: List[ImpressionResult]
    prescriptions: List[PrescriptionItem]
    doctor_chart_summary: str
    patient_friendly_report: str