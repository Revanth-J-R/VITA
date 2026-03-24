from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
from app.models.schemas import TriageRequest, TriageResponse, RiskLevel
from app.services.nlp_service import nlp_service
from app.services.triage_engine import triage_engine
from app.services.session_service import session_service
from app.services.n8n_service import n8n_service
import os
import uuid

router = APIRouter()

@router.post("/triage/text", response_model=TriageResponse)
async def triage_text(request: TriageRequest, background_tasks: BackgroundTasks):
    # Get or create session
    sid = request.session_id or str(uuid.uuid4())
    session = session_service.get_session(sid)
    
    # Process symptoms
    symptoms = nlp_service.extract_symptoms(request.user_input)
    session_service.update_session(sid, request.user_input, symptoms)
    
    # Intelligent LLM Triage (Async)
    # Pass full conversation messages for context
    response = await triage_engine.process_triage(
        session["extracted"], 
        session["messages"], 
        mode="text"
    )
    
    # Record the assistant's response in history if still triaging
    if not response.is_complete:
        session_service.record_assistant_message(sid, response.doctor_message)
    else:
        # Final summary also stored
        session_service.record_assistant_message(sid, response.doctor_message)
    
    # n8n background task
    background_tasks.add_task(
        n8n_service.send_triage_event,
        response, 
        request.user_input
    )
    
    return response

@router.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    session_service.clear_session(session_id)
    return {"status": "cleared", "session_id": session_id}

@router.get("/health")
def health_check():
    n8n_url = os.getenv("N8N_WEBHOOK_URL", "not configured")
    return {
        "status": "ok",
        "message": "VITA Intelligent Agent is running.",
        "n8n_webhook": n8n_url,
        "mode": "Groq LLM (Llama 3)"
    }
