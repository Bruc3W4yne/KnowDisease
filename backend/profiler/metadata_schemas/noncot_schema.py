from pydantic import BaseModel, Field

class SimpleAnswerSchema(BaseModel):
    """Simple schema for non-CoT single answer extraction."""
    answer: str = Field(
        min_length=8,
        max_length=150,
        description="1-3 most relevant medical terms (comma-separated) or 'Not specified'"
    )