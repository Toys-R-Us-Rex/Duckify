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
        import random
        dir = Path(__file__).parent.parent.parent / "assets" / "textures"
        files = list(filter(lambda p: p.is_file(), dir.iterdir()))
        return GenAIResult(random.choice(files).absolute())
