import re

# In the new Intelligent Agent architecture, the LLM is the primary extractor.
# This service is now a lightweight helper to identify common medical keywords 
# to provide additional structural context to the LLM if needed.

COMMON_SYMPTOMS = [
    "stomach pain", "fever", "headache", "cough", "chest pain",
    "breathing difficulty", "shortness of breath", "vomiting", 
    "nausea", "body pain", "chills", "dizziness", "blood in vomit",
    "severe injury", "irregular periods", "missed period", 
    "heavy bleeding", "menstrual changes", "menstrual cramps", "late period"
]

class NLPService:
    def __init__(self):
        pass

    def extract_symptoms(self, text: str) -> list[str]:
        """
        Extract symptoms from user text for additional context.
        """
        text_lower = text.lower()
        extracted = []
        for symptom in COMMON_SYMPTOMS:
            if symptom in text_lower:
                extracted.append(symptom)
        
        # If no strict match, it's fine - the LLM will analyze the full text.
        return extracted

nlp_service = NLPService()
