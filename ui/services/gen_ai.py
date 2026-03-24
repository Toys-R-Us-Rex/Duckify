from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from genai.client import GenAIClient


@dataclass
class GenAIRequest:
    model_path: Path
    prompt: str
    steps: int
    guidance: float
    output_dir: Path
    negative_prompt: str = ""
    prompt_wrapper: str = ""


@dataclass
class GenAIResult:
    texture_path: Optional[Path]


class GenAIService:
    def __init__(
        self,
        ssh_host: str,
        ssh_port: int,
        ssh_user: str,
        ssh_key_path: Path,
        host: str,
        port: int,
        hf_token: str
    ) -> None:
        self.ssh_host: str = ssh_host
        self.ssh_port: int = ssh_port
        self.ssh_user: str = ssh_user
        self.ssh_key_path: Path = ssh_key_path
        self.host: str = host
        self.port: int = port
        self.hf_token: str = hf_token

        self.client: GenAIClient = GenAIClient(
            ssh_host=ssh_host,
            ssh_port=ssh_port,
            ssh_user=ssh_user,
            ssh_key_path=ssh_key_path,
            remote_host=host,
            remote_port=port,
            hf_token=hf_token
        )

    def run(self, request: GenAIRequest) -> GenAIResult:
        texture_path: Optional[Path] = self.client.generate(
            obj_path=request.model_path,
            prompt=request.prompt,
            output_dir=request.output_dir,
            negative_prompt=request.negative_prompt,
            prompt_wrapper=request.prompt_wrapper,
            steps=request.steps,
            guidance=request.guidance,
        )

        return GenAIResult(texture_path)
