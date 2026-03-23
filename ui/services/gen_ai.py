from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from genai.client import generate_texture


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
    texture_path: Optional[Path]


class GenAIService:
    def __init__(
        self,
        ssh_host: str,
        ssh_port: int,
        ssh_user: str,
        ssh_key_path: str,
        host: str,
        port: int,
        hf_token: str
    ) -> None:
        self.ssh_host: str = ssh_host
        self.ssh_port: int = ssh_port
        self.ssh_user: str = ssh_user
        self.ssh_key_path: str = ssh_key_path
        self.host: str = host
        self.port: int = port
        self.hf_token: str = hf_token

    def run(self, request: GenAIRequest) -> GenAIResult:
        outdir, _ = generate_texture(
            obj_path=request.model_path,
            prompt=request.prompt,
            output_dir=request.output_dir,
            negative_prompt=request.negative_prompt,
            prompt_wrapper=request.prompt_wrapper,
            steps=request.steps,
            guidance=request.guidance,
            SSH_HOST=self.ssh_host,
            SSH_USER=self.ssh_user,
            SSH_KEY_PATH=self.ssh_key_path,
            HF_TOKEN=self.hf_token,
        )

        if outdir is None:
            return GenAIResult(None)
        
        model_name: str = request.model_path.stem
        texture_filename: str = f"textured_{model_name}.png"
        return GenAIResult(outdir / texture_filename)
