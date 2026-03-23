from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class GenAIRequest:
    model_path: Path
    prompt: str
    negative_prompt: str
    prompt_wrapper: Optional[str]
    steps: int
    guidance: float
    output_dir: Path


@dataclass
class GenAIResult:
    files: list[Path]


class GenAIService:
    def __init__(self, host: str, port: int) -> None:
        self.host: str = host
        self.port: int = port

    def run(self, request: GenAIRequest) -> GenAIResult:
        # TODO: Call GenAI endpoint
        print("Generating texture")
        print(f" - host: {self.host}")
        print(f" - port: {self.port}")
        print(f" - model: {request.model_path}")
        print(f" - prompt: {request.prompt}")
        return GenAIResult(files=[])
