from dataclasses import dataclass, field
import json

from PyQt6.QtCore import QSettings

@dataclass
class GenAISettings:
    host: str = "localhost"
    port: int = 8000


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


class SettingsManager:
    def __init__(self) -> None:
        self._prefs = QSettings("Toys-R-Us-Rex", "Duckify")
    
    def load(self) -> Settings:
        colors: list[list[int]] = json.loads(self._prefs.value("tracing.palette", "[]"))
        return Settings(
            genAI=GenAISettings(
                host=self._prefs.value("genAI.host", GenAISettings.host),
                port=self._prefs.value("genAI.port", GenAISettings.port, type=int),
            ),
            tracing=TracingSettings(
                palette=list(map(tuple, colors)) # type: ignore
            ),
            robot=RobotSettings(
                ip_address=self._prefs.value("robot.ip", RobotSettings.ip_address)
            )
        )
    
    def save(self, settings: Settings):
        self._prefs.setValue("genAI.host", settings.genAI.host)
        self._prefs.setValue("genAI.port", settings.genAI.port)
        self._prefs.setValue("tracing.palette", json.dumps(settings.tracing.palette))
        self._prefs.setValue("robot.ip", settings.robot.ip_address)
