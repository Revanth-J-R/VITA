import os
import logging
import httpx
from app.models.schemas import TriageResponse

logger = logging.getLogger("vita.n8n")

class N8nService:
    """
    Sends VITA triage results to an n8n webhook for downstream automation.
    Silently skips if N8N_WEBHOOK_URL is not configured or n8n is unreachable.
    """

    def __init__(self):
        self.webhook_url = os.getenv("N8N_WEBHOOK_URL", "")

    async def send_triage_event(self, triage_data: TriageResponse, original_input: str):
        """
        Fire-and-forget: POST the triage result to n8n webhook as a background task.
        """
        if not self.webhook_url:
            logger.debug("N8N_WEBHOOK_URL not set — skipping n8n event.")
            return

        payload = {
            "source": "VITA",
            "original_input": original_input,
            "risk_level": triage_data.risk_level,
            "possible_cause": triage_data.possible_cause,
            "follow_up_questions": triage_data.follow_up_questions,
            "recommendations": triage_data.recommendations,
            "when_to_see_doctor": triage_data.when_to_see_doctor,
            "is_emergency": triage_data.is_emergency,
            "emergency_message": triage_data.emergency_message or "",
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()
                logger.info(f"n8n event sent successfully. Status: {response.status_code}")
        except httpx.ConnectError:
            logger.warning("n8n is not reachable. Triage event not sent.")
        except httpx.TimeoutException:
            logger.warning("n8n webhook timed out. Triage event not sent.")
        except Exception as e:
            logger.warning(f"Failed to send event to n8n: {e}")

n8n_service = N8nService()
