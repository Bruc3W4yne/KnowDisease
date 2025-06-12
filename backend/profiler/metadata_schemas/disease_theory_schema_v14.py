from pydantic import BaseModel, Field, constr

class DiseaseTheorySchema(BaseModel):
    disease_name: str = Field(
        description="What is the primary disease, medical condition, or distinct pathological process that is the main subject of this paper, including any common synonyms or specific subtypes explicitly discussed?"
    )
    etiology_factor: constr(max_length=1500) = Field(
        description="What are the primary infectious agents, underlying pathogenic mechanisms (e.g., specific protein actions, inflammation, metabolic dysregulation), genetic mutations, oncogenic drivers, or significant environmental/lifestyle risk factors identified as causing or directly contributing to the development or manifestation of the main disease/condition discussed?"
    )
    diagnostic_method: constr(max_length=1500) = Field(
        description="What are the key diagnostic procedures, specific laboratory tests (including cut-off values if mentioned), imaging findings, clinical assessment criteria, or histopathological features highlighted in the paper for confirming the presence of the disease/condition, or proposed as important novel diagnostic approaches?"
    )
    biomarker: constr(max_length=1500) = Field(
        description="What specific molecular entities (e.g., genes, proteins, miRNAs), cellular characteristics, imaging signatures, or other quantifiable physiological indicators are described in the paper as being valuable for detecting the disease, monitoring its progression, stratifying patient risk, or predicting response to therapy?"
    )
    treatment_intervention: constr(max_length=1500) = Field(
        description="What are the principal therapeutic interventions, including specific drug names (and mechanisms if central to the discussion), surgical techniques, radiation modalities, cell-based therapies, or distinct management strategies, detailed in the paper for treating or managing the main disease/condition or its complications?"
    )
    prognostic_indicator: constr(max_length=1500) = Field(
        description="What specific clinical signs, laboratory values, imaging findings, genetic or molecular markers, histopathological features, or established scoring systems are identified in the paper as significant predictors of the disease's future course, patient survival, likelihood of relapse, or risk of developing severe complications?"
    )