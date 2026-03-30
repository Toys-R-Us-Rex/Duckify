import datetime
import logging
import zipfile
from logging import Logger
from pathlib import Path
from typing import Optional

import requests
from sshtunnel import SSHTunnelForwarder

from genai.data import GenerationRequest


class GenAIClient:
    def __init__(
        self,
        ssh_host: str = "",
        ssh_port: int = 22,
        ssh_user: str = "user",
        ssh_key_path: Path = Path(),
        remote_host: str = "127.0.0.1",
        remote_port: int = 5000,
        hf_token: str = "",
    ) -> None:
        self.logger: Logger = logging.getLogger("GenAIClient")

        self.ssh_host: str = ssh_host
        self.ssh_port: int = ssh_port
        self.ssh_user: str = ssh_user
        self.ssh_key_path: Path = ssh_key_path
        self.remote_host: str = remote_host
        self.remote_port: int = remote_port
        self.hf_token: str = hf_token

    def open_tunnel(self) -> SSHTunnelForwarder:
        return SSHTunnelForwarder(
            (self.ssh_host, self.ssh_port),
            ssh_username=self.ssh_user,
            ssh_pkey=self.ssh_key_path,
            remote_bind_address=(self.remote_host, self.remote_port),
        )

    def test_ssh_connection(self) -> bool:
        with self.open_tunnel() as tunnel:
            return tunnel is not None
        return False

    def test_api_connection(self) -> bool:
        with self.open_tunnel() as tunnel:
            if tunnel is None:
                return False

            res = requests.get(
                f"http://{self.remote_host}:{tunnel.local_bind_port}/ping"
            )
            return res.status_code == 200
        return False

    def generate(
        self,
        obj_path: Path,
        prompt: str,
        output_dir: Path,
        negative_prompt: str = "",
        prompt_wrapper: str = "",
        steps: int = 30,
        guidance: float = 6.0,
    ) -> tuple[Optional[Path], Optional[str]]:
        output_dir = output_dir.resolve()
        with self.open_tunnel() as tunnel:
            if tunnel is None:
                err = "Error while opening SSH tunnel"
                self.logger.error(err)
                return None, err

            self.logger.info("SSH tunnel opened")
            api_url = f"http://{self.remote_host}:{tunnel.local_bind_port}/generate"

            with open(obj_path, "rb") as f:
                files = {"file": f}
                data = GenerationRequest(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    prompt_wrapper=prompt_wrapper,
                    steps=steps,
                    guidance=guidance,
                    hf_token=self.hf_token,
                )
                response = requests.post(api_url, files=files, data=data.model_dump())

            if response.status_code != 200:
                err = f"API Error: {response.text}"
                self.logger.error(err)
                return None, err

            zip_path: Path = output_dir / "texture_result.zip"
            with open(zip_path, "wb") as f:
                f.write(response.content)
            self.logger.info("Zip received")

            result_dir: Path = self._extract_result(zip_path, output_dir)

            if not output_dir.exists():
                err = f"Extracted directory doesn't exist: {output_dir}"
                self.logger.error(err)
                return None, err

            return result_dir / "texture.png", None

    def _extract_result(self, zip_path: Path, output_dir: Path) -> Path:
        timestamp: str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        extract_dirname: str = f"extracted_{timestamp}"
        output_path: Path = output_dir / extract_dirname
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(output_path)
        return output_path
