import os
import json
from datetime import datetime

# Prefer the new `google-genai` package (import path: `google.genai` via `from google import genai`).
# Fall back to legacy `google.generativeai` if needed for compatibility.
try:
    # New package (preferred)
    from google import genai
    _NEW_GENAI = True
except Exception:
    try:
        # Legacy package
        import google.generativeai as genai
        _NEW_GENAI = False
    except Exception:
        genai = None
        _NEW_GENAI = False

class AiService:
    def __init__(self, api_key: str = None, audit_repository=None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.audit_repository = audit_repository

    def _log_usage(self, syllabus_id, action, in_tok, out_tok):
        if self.audit_repository and syllabus_id:
            try:
                self.audit_repository.create(syllabus_id, action, in_tok, out_tok)
            except Exception as e:
                print(f'Failed to log AI usage: {e}')

    def generate(self, subject_name: str, syllabus_id: int = None):
        if not self.api_key:
            return {"error": "Chưa cấu hình GEMINI_API_KEY"}

        if genai is None:
            return {"error": "No generative AI client installed (install google-genai)"}

        # Strict Template
        json_template = {
            "subject_name_vi": subject_name,
            "subject_name_en": "...",
            "credits": 3,
            "time_allocation": { "theory": 30, "practice": 30, "self_study": 90 },
            "description": "...",
            "clos": [
                { "code": "CLO1", "description": "..." }
            ],
            "materials": [
                { "type": "MAIN", "title": "...", "author": "...", "publisher": "...", "isbn": "..." }
            ],
            "teaching_plans": [
                { "week": 1, "topic": "...", "activity": "...", "assessment": "..." }
            ],
            "assessment_schemes": [
                { 
                    "name": "Midterm", "weight": 50, 
                    "components": [
                        { "name": "Exam 1", "weight": 100, "rubrics": [{"criteria": "...", "max_score": 10}] }
                    ] 
                }
            ]
        }

        prompt = f"""
        You are a curriculum expert. Create a syllabus for: "{subject_name}".
        OUTPUT REQUIREMENT: Return ONLY valid raw JSON. No markdown, no explanations.
        The JSON structure MUST match this template exactly:
        {json.dumps(json_template, ensure_ascii=False)}
        """

        try:
            if _NEW_GENAI:
                # New `google-genai` client APIs can vary by version. Try several common interfaces defensively.
                # Some versions provide a module-level `configure` and helpers; others provide a `Client` class.
                if hasattr(genai, "configure"):
                    try:
                        genai.configure(api_key=self.api_key)
                    except Exception:
                        # Some versions accept different config methods — ignore and continue to client creation
                        pass

                resp_text = None

                # Preferred: Client.generate_text(...) pattern
                if hasattr(genai, "Client"):
                    client = genai.Client()
                    response = client.generate_text(model="gemini-2.5-flash", input=prompt)
                    resp_text = getattr(response, "text", None)
                    if not resp_text and getattr(response, "candidates", None):
                        candidates = getattr(response, "candidates", [])
                        if candidates:
                            resp_text = getattr(candidates[0], "output", None) or getattr(candidates[0], "content", None)

                # Fallback: module-level generate_text
                if resp_text is None and hasattr(genai, "generate_text"):
                    response = genai.generate_text(model="gemini-2.5-flash", input=prompt)
                    resp_text = getattr(response, "text", None)
                    if not resp_text and getattr(response, "candidates", None):
                        candidates = getattr(response, "candidates", [])
                        if candidates:
                            resp_text = getattr(candidates[0], "output", None) or getattr(candidates[0], "content", None)

                # Last resort: string conversion
                if resp_text is None:
                    resp_text = str(response)

            else:
                # Legacy package behavior
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                resp_text = getattr(response, "text", "")

            clean_text = resp_text.replace("```json", "").replace("```", "").strip()
            # Simple token estimation (fallback if client does not provide usage)
            try:
                input_tokens = max(0, len(prompt.split()))
                output_tokens = max(0, len(clean_text.split()))
            except Exception:
                input_tokens = 0
                output_tokens = 0

            # Log usage if syllabus_id provided
            self._log_usage(syllabus_id, 'GENERATE', input_tokens, output_tokens)

            return json.loads(clean_text)
        except Exception as e:
            # Attempt to log error usage with zero tokens (if applicable)
            try:
                self._log_usage(syllabus_id, 'ERROR', 0, 0)
            except Exception:
                pass
            return {"error": str(e)}
