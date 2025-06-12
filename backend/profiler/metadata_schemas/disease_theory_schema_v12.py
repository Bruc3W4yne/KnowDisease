from pydantic import BaseModel, Field, constr

class DiseaseTheorySchema(BaseModel):
    disease_name: constr(min_length=3) = Field(
        description="What disease or condition is the paper about?"
    )

    etiology_factor: constr(min_length=3) = Field(
        description="What direct cause, mutation, infection or exposure triggers the disease?"
    )
    diagnostic_method: constr(min_length=3) = Field(
        description="Which diagnostic procedure, imaging result, lab test, biopsy finding, or criteria establishes the disease diagnosis?"
    )
    biomarker: constr(min_length=3) = Field(
        description="What measurable indicator (e.g., gene, protein, imaging finding) reflects disease state, progression, or treatment response?"
    )
    treatment_intervention: constr(min_length=3) = Field(
        description="Which therapy, drug, surgery or other intervention targets the disease?"
    )
    prognostic_indicator: constr(min_length=3) = Field(
        description="Which factor or metric predicts patient outcome or survival?"
    )