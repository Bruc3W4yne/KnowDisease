from pydantic import BaseModel, Field, constr

class DiseaseTheorySchema(BaseModel):
    disease_name: str = Field(
        description="What is the primary disease or medical condition focused on in this paper?"
    )
    etiology_factor: constr(max_length=1500) = Field(
        description="What are the main causes, identified genetic mutations, or key risk factors for the disease discussed?"
    )
    diagnostic_method: constr(max_length=1500) = Field(
        description="Which primary methods, tests, or criteria are used to diagnose the disease according to the paper?"
    )
    biomarker: constr(max_length=1500) = Field(
        description="What measurable biological markers (e.g., genes, proteins, imaging features) indicate disease presence, progression, or risk?"
    )
    treatment_intervention: constr(max_length=1500) = Field(
        description="What are the main treatments, therapies, or specific drugs mentioned for the disease?"
    )
    prognostic_indicator: constr(max_length=1500) = Field(
        description="Which factors, markers, or scores are identified to predict the disease's outcome or patient survival?"
    )