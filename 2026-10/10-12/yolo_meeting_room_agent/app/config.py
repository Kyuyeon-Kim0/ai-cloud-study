import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    model: str = os.getenv('OPENAI_MODEL', 'gpt-4.1-mini')
    yolo_model: str = os.getenv('YOLO_MODEL', 'yolov8n.pt')
    confidence: float = float(os.getenv('YOLO_CONF', '0.35'))
    small_max: int = int(os.getenv('SMALL_GROUP_MAX', '3'))
    crowded_min: int = int(os.getenv('CROWDED_MIN', '7'))
    enable_agent: bool = os.getenv('ENABLE_AGENT', 'true').lower() == 'true'

    def validate(self) -> None:
        if not 0 < self.confidence <= 1:
            raise ValueError('YOLO_CONF must be between 0 and 1')
        if not 0 < self.small_max < self.crowded_min:
            raise ValueError('Expected 0 < SMALL_GROUP_MAX < CROWDED_MIN')
