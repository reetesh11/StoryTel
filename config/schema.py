from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum

class VideoCategory(str, Enum):
    REAL_INCIDENT = "real_incident"
    CONSPIRACY = "conspiracy"

class VoiceTone(str, Enum):
    SERIOUS = "serious"
    HAPPY = "happy"
    NEUTRAL = "neutral"
    DRAMATIC = "dramatic"

class VideoConfig(BaseModel):
    topic: str
    category: Optional[VideoCategory] = None
    voice_tone: VoiceTone = VoiceTone.NEUTRAL
    voice_speed: float = Field(default=1.0, ge=0.5, le=2.0)
    background_music: Optional[str] = None
    theme: Optional[str] = None
    language: str = "en"
    include_references: bool = True
    playlist_id: Optional[str] = None
    custom_visuals: Optional[List[str]] = None

class VideoSection(BaseModel):
    title: str
    content: str
    duration: Optional[float] = None
    visuals: Optional[List[str]] = None
    references: Optional[List[str]] = None

class VideoScript(BaseModel):
    sections: List[VideoSection]
    total_duration: float
    category: VideoCategory 