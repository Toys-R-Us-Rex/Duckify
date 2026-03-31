import json
from dataclasses import dataclass, field

from PyQt6.QtCore import QObject, QSettings, pyqtSignal


@dataclass
class GenAISettings:
    ssh_host: str = ""
    ssh_port: int = 22
    ssh_user: str = ""
    ssh_key: str = ""
    host: str = "localhost"
    port: int = 5000
    hf_token: str = ""
    negative_prompt: str = ""
    prompt_wrapper: str = ""
    steps: int = 30
    guidance: float = 6.0


@dataclass
class TracingSettings:
    palette: list[tuple[int, int, int]] = field(default_factory=list)


@dataclass
class RobotSettings:
    ip_address: str = "127.0.0.1"


@dataclass
class Settings:
    genAI: GenAISettings = field(default_factory=GenAISettings)
    tracing: TracingSettings = field(default_factory=TracingSettings)
    robot: RobotSettings = field(default_factory=RobotSettings)


class SettingsManager(QObject):
    changed: pyqtSignal = pyqtSignal(Settings)

    def __init__(self) -> None:
        super().__init__()
        self._prefs = QSettings("Toys-R-Us-Rex", "Duckify")

    def load(self) -> Settings:
        colors: list[list[int]] = json.loads(self._prefs.value("tracing.palette", "[]"))
        return Settings(
            genAI=GenAISettings(
                ssh_host=self._prefs.value("genAI.ssh_host", GenAISettings.ssh_host),
                ssh_port=self._prefs.value(
                    "genAI.ssh_port", GenAISettings.ssh_port, type=int
                ),
                ssh_user=self._prefs.value("genAI.ssh_user", GenAISettings.ssh_user),
                ssh_key=self._prefs.value("genAI.ssh_key", GenAISettings.ssh_key),
                host=self._prefs.value("genAI.host", GenAISettings.host),
                port=self._prefs.value("genAI.port", GenAISettings.port, type=int),
                hf_token=self._prefs.value("genAI.hf_token", GenAISettings.hf_token),
                negative_prompt=self._prefs.value(
                    "genAI.negative_prompt", GenAISettings.negative_prompt
                ),
                prompt_wrapper=self._prefs.value(
                    "genAI.prompt_wrapper", GenAISettings.prompt_wrapper
                ),
                steps=self._prefs.value("genAI.steps", GenAISettings.steps, type=int),
                guidance=self._prefs.value(
                    "genAI.guidance", GenAISettings.guidance, type=float
                ),
            ),
            tracing=TracingSettings(palette=list(map(tuple, colors))),  # type: ignore
            robot=RobotSettings(
                ip_address=self._prefs.value("robot.ip", RobotSettings.ip_address)
            ),
        )

    def save(self, settings: Settings):
        self._prefs.setValue("genAI.ssh_host", settings.genAI.ssh_host)
        self._prefs.setValue("genAI.ssh_port", settings.genAI.ssh_port)
        self._prefs.setValue("genAI.ssh_user", settings.genAI.ssh_user)
        self._prefs.setValue("genAI.ssh_key", settings.genAI.ssh_key)
        self._prefs.setValue("genAI.host", settings.genAI.host)
        self._prefs.setValue("genAI.port", settings.genAI.port)
        self._prefs.setValue("genAI.hf_token", settings.genAI.hf_token)
        self._prefs.setValue("genAI.negative_prompt", settings.genAI.negative_prompt)
        self._prefs.setValue("genAI.prompt_wrapper", settings.genAI.prompt_wrapper)
        self._prefs.setValue("genAI.steps", settings.genAI.steps)
        self._prefs.setValue("genAI.guidance", settings.genAI.guidance)
        self._prefs.setValue("tracing.palette", json.dumps(settings.tracing.palette))
        self._prefs.setValue("robot.ip", settings.robot.ip_address)
        self.changed.emit(settings)
