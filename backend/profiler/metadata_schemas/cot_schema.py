from pydantic import BaseModel, Field
from typing import Dict, List

class CoTModelSchema(BaseModel):
    reasoning: str = Field(description="Explain WHY you selected these specific terms over others. Include: (1) What you searched for, (2) What candidates you found, (3) Why you chose these particular terms.")
    final_answer: List[str] = Field(
        description="Array of up to three distinct terms that directly and specifically answer the field's question, and are also the keys of 'evidence', in the same order.",
        min_items=0,
        max_items=3
    )
    evidence: Dict[str, str] = Field(description="Mapping from each extracted term to the verbatim quote(s) from the context supporting it.")
    