import time
from typing import Dict, List, Any

class SessionService:
    def __init__(self, expiry_seconds: int = 1800):  # 30 mins
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.expiry_seconds = expiry_seconds

    def get_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "messages": [],       # Unified history: [{"role": "user/assistant", "content": "..."}]
                "extracted": set(),   # Accumulated symptoms
                "asked": set(),       # Questions already asked by doctor
                "last_active": time.time()
            }
        
        session = self.sessions[session_id]
        session["last_active"] = time.time()
        return session

    def update_session(self, session_id: str, new_input: str, symptoms: List[str]):
        session = self.get_session(session_id)
        session["messages"].append({"role": "user", "content": new_input})
        for s in symptoms:
            session["extracted"].add(s.lower())

    def record_assistant_message(self, session_id: str, message: str):
        session = self.get_session(session_id)
        session["messages"].append({"role": "assistant", "content": message})

    def mark_question_asked(self, session_id: str, question: str):
        session = self.get_session(session_id)
        session["asked"].add(question)
        self.record_assistant_message(session_id, question)

    def clear_session(self, session_id: str):
        self.sessions.pop(session_id, None)

    def cleanup(self):
        now = time.time()
        expired = [sid for sid, s in self.sessions.items() 
                  if now - s["last_active"] > self.expiry_seconds]
        for sid in expired:
            self.sessions.pop(sid, None)

session_service = SessionService()
