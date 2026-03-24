from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class TriageRequest(BaseModel):
    user_input: str
    session_id: Optional[str] = None

class TriageResponse(BaseModel):
    risk_level: RiskLevel
    possible_cause: str
    doctor_message: str  # What the doctor says next
    is_complete: bool    # Whether triage is finished
    follow_up_questions: List[str]
    recommendations: List[str]
    when_to_see_doctor: str
    is_emergency: bool
    emergency_message: Optional[str] = None

class VoiceTriageResponse(TriageResponse):
    transcribed_text: str
    audio_response_url: Optional[str] = None # Base64 encoded audio string
