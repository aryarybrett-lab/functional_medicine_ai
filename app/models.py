# app/models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class LabResults(BaseModel):
    # 기존 지표
    fecal_calprotectin: Optional[float] = None
    ca_mg_ratio: Optional[float] = None
    total_testosterone: Optional[float] = None
    lh: Optional[float] = None
    vitamin_d: Optional[float] = None
    nk_activity: Optional[float] = None
    
    # ➕ 신규 추가: 심혈관/대사/메틸레이션 지표
    homocysteine: Optional[float] = Field(None, description="Serum Homocysteine (umol/L)")
    fasting_glucose: Optional[float] = Field(None, description="공복 혈당 (mg/dL)")
    fasting_insulin: Optional[float] = Field(None, description="공복 인슐린 (uIU/mL)")
    homa_ir: Optional[float] = Field(None, description="인슐린 저항성 지수 HOMA-IR")
    hs_crp: Optional[float] = Field(None, description="고감도 CRP (mg/L)")

class PatientAnalysisRequest(BaseModel):
    patient_id: str
    age: int
    gender: str
    chief_complaints: List[str]
    labs: Optional[LabResults] = None

class PrescriptionItem(BaseModel):
    category: str
    name: str
    dosage: str
    usage: str
    duration: Optional[str] = None
    notes: Optional[str] = None

class ImpressionResult(BaseModel):
    rank: int
    category_name: str
    score: float
    pathophysiology: Optional[str] = ""
    matching_evidence: List[str] = []

class AnalysisResponse(BaseModel):
    patient_id: str
    impressions: List[ImpressionResult]
    prescriptions: List[PrescriptionItem]
    doctor_chart_summary: str
    patient_friendly_report: str
