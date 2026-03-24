from app.models.schemas import RiskLevel, TriageResponse
from typing import List, Optional, Set
from app.services.llm_service import llm_service

# TriageEngine now acts as a coordinator for the LLM-powered logic.
# It maintains the same interface to avoid breaking the rest of the app.

class TriageEngine:
    def __init__(self):
        # Base intros for fallback or consistency
        self.empathetic_intros = [
            "I understand.",
            "That sounds uncomfortable.",
            "I'm sorry you're feeling this way.",
            "I hear you, let's look into this.",
            "Thank you for sharing that with me."
        ]

    async def process_triage(self, symptoms: Set[str], messages: List[dict], mode: str = "text") -> TriageResponse:
        """
        Delegate the triage process to the LLM.
        - symptoms: set of symptoms already extracted (for context)
        - messages: full conversation history from session_service
        """
        # Convert set to list for LLM context
        symptom_list = list(symptoms)
        
        # Use LLM Service to process the logic
        response = await llm_service.process_triage(messages, symptom_list)
        
        return response

triage_engine = TriageEngine()
