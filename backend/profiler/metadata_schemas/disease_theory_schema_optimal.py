from pydantic import BaseModel, Field, constr
from typing import List

class DiseaseTheorySchema(BaseModel):
    disease_name: str = Field(
        description="What is the full name of the disease or condition discussed in this paper? Include the full name only, no abbreviations."
    )

    etiology_factor: str = Field(
        description="What directly causes this disease? Include genetic factors, pathogens, precursor conditions, environmental exposures, and transmission routes. For genetic causes, list specific genes."
    )
    
    diagnostic_method: str = Field(
        description="What specific tests confirm diagnosis of this disease? Include exact test names, imaging methods, and clinical assessments. List the specific diagnostic procedure, not general categories."
    )
    
    biomarker: str = Field(
        description="What measurable indicators reflect this disease's presence or progression? Include both molecular entities (genes, proteins, antibodies) AND clinical findings."
    )
    
    treatment_intervention: str = Field(
        description="What treatments are used for this disease? List ALL medications, surgical procedures, and therapeutic approaches."
    )
    
    prognostic_indicator: str = Field(
        description="What factors predict patient outcomes or disease progression? Include genetic markers, molecular features, patient characteristics, and clinical findings that correlate with prognosis."
    )