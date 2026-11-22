import os
import time
from google import genai
from google.genai import types
from schemas import TaskPlanOutput
from prompts import CHECKLIST_SYSTEM_PROMPT


class ChecklistBotService:
    def __init__(self, api_key: str | None = None, model: str = "gemini-3.5-flash"):
        resolved_key = api_key or os.getenv("GEMINI_API_KEY")
        if not resolved_key:
            raise ValueError("Λείπει το GEMINI_API_KEY. Βάλ' το στο .env ή στην αριστερή μπάρα.")
        self.client = genai.Client(api_key=resolved_key)
        self.model = model

    def notes_to_tasks(self, notes_text: str, retries: int = 2) -> TaskPlanOutput:
        prompt = f"Μετέτρεψε τις παρακάτω σημειώσεις σε tasks με σύντομα βήματα checklist:\n\n{notes_text}"
        last_error: Exception | None = None

        for attempt in range(retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=CHECKLIST_SYSTEM_PROMPT,
                        response_mime_type="application/json",
                        response_schema=TaskPlanOutput,
                        temperature=0.3,
                    ),
                )
                return TaskPlanOutput.model_validate_json(response.text)
            except Exception as exc:
                last_error = exc
                message = str(exc)
                if ("503" in message or "UNAVAILABLE" in message or "429" in message) and attempt < retries - 1:
                    time.sleep(0.6)
                    continue
                raise

        raise last_error  # type: ignore[misc]