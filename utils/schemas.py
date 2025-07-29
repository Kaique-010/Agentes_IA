# utils/schemas.py
from pydantic import BaseModel, Field

class FormPrompt(BaseModel):
    mensagem: str = Field(..., min_length=3, description="Mensagem enviada pelo usuário")
