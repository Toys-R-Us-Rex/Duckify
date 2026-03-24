from typing import Optional

from pydantic import BaseModel


class GenerationRequest(BaseModel):
    prompt: str
    negative_prompt: str = ""
    prompt_wrapper: str = ""
    steps: int
    guidance: float
    hf_token: Optional[str] = None
    num_generations: int = 1
