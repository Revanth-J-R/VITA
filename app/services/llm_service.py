import os
import json
import logging
from typing import List, Dict, Any, Optional
from app.models.schemas import TriageResponse, RiskLevel
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import re

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.2
        )

    def call_llm(self, messages: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        try:
            lc_messages = []

            for m in messages:
                if m["role"] == "system":
                    lc_messages.append(SystemMessage(content=m["content"]))
                else:
                    lc_messages.append(HumanMessage(content=m["content"]))

            response = self.llm.invoke(lc_messages)
            content = response.content

            try:
                return json.loads(content)
            except:
                match = re.search(r"\{.*\}", content, re.DOTALL)
                if match:
                    return json.loads(match.group())
                return None

        except Exception as e:
            logger.error(f"Error calling Groq: {e}")
            return None

    def get_triage_system_prompt(self) -> str:
        return """
        You are VITA (Voice Integrated Triage Assistant), a professional clinical triage agent.
        Your goal is to conduct a safe, empathetic, and efficient medical triage via a chat/voice interface.

        PROTOCOLS:
        1. Follow standard clinical triage logic (like the Manchester Triage System).
        2. If emergency symptoms (chest pain, breathing difficulty, severe bleeding, etc.) are detected, IMMEDIATELY flag as HIGH risk and end the assessment.
        3. Collect enough information (usually 3-5 specific follow-up questions) before giving a final assessment.
        4. Maintain a supportive, professional, and non-alarmist tone.
        5. NEVER give a definitive medical diagnosis. Always use phrases like "This could be..." or "These symptoms may be associated with...".
        6. ALWAYS include a disclaimer that this is not medical advice.

        RESPONSE FORMAT (JSON ONLY):
        You MUST return a valid JSON object. Do not include any other text.
        JSON schema:
        {
            "risk_level": "LOW" | "MEDIUM" | "HIGH",
            "possible_cause": "Short summary of possible condition",
            "doctor_message": "Empathetic message for the user. If is_complete is false, include the next question here.",
            "is_complete": boolean (true if you have enough info for a final summary),
            "follow_up_questions": [string] (the bare next question to ask, if any),
            "recommendations": [string],
            "when_to_see_doctor": "Specific guidance on timing",
            "is_emergency": boolean
        }
        """

    async def process_triage(self, history: List[Dict[str, str]], symptoms: List[str]) -> TriageResponse:
        """
        Conduct triage reasoning using the LLM.
        """
        system_prompt = self.get_triage_system_prompt()
        
        # Build message history for context
        messages = [{"role": "system", "content": system_prompt}]
        
        # history is already a list of {"role": "...", "content": "..."}
        messages.extend(history)

        # Add current context as a summary nudge if symptoms found
        if symptoms:
            messages.append({
                "role": "system", 
                "content": f"Context: Symptoms detected in last input: {', '.join(symptoms)}. Ensure these are addressed."
            })

        # Final trigger message
        messages.append({"role": "user", "content": "Analyze the conversation and provide the next triage step in JSON format."})

        llm_data = self.call_llm(messages)

        if not llm_data:
            # Fallback in case of API failure
            return TriageResponse(
                risk_level=RiskLevel.LOW,
                possible_cause="Under Assessment (API Error)",
                doctor_message="I'm having a bit of trouble connecting right now. Can you tell me more about your symptoms?",
                is_complete=False,
                follow_up_questions=["Could you describe your symptoms again?"],
                recommendations=["Please check your internet connection."],
                when_to_see_doctor="N/A",
                is_emergency=False
            )

        # Map JSON to TriageResponse
        return TriageResponse(
            risk_level=RiskLevel(llm_data.get("risk_level", "LOW")),
            possible_cause=llm_data.get("possible_cause", "Under Assessment"),
            doctor_message=llm_data.get("doctor_message", ""),
            is_complete=llm_data.get("is_complete", False),
            follow_up_questions=llm_data.get("follow_up_questions", []),
            recommendations=llm_data.get("recommendations", []),
            when_to_see_doctor=llm_data.get("when_to_see_doctor", ""),
            is_emergency=llm_data.get("is_emergency", False),
            emergency_message=llm_data.get("emergency_message") if llm_data.get("is_emergency") else None
        )

llm_service = LLMService()
