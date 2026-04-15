import json
import os
import logging
import re
from typing import Any, Optional
from dotenv import load_dotenv
from openai import OpenAI

from extractors.base_extractor import FieldExtractor

load_dotenv()
logger = logging.getLogger(__name__)

class NameExtractor(FieldExtractor):

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        max_input_chars: int = 3000,
    ) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.model = model
        self.max_input_chars = max_input_chars

        if self.client:
            logger.debug("NameExtractor initialized with OpenAI model: %s", self.model)
        else:
            logger.warning(
                "OPENAI_API_KEY not found. NameExtractor will use fallback heuristic extraction."
            )

    def extract(self, text: str) -> Optional[str]:
        if not text or not text.strip():
            logger.warning("Name extraction skipped because input text is empty.")
            return None

        if not self.client:
            logger.debug("Using fallback name extraction because LLM client is unavailable.")
            return self._fallback_from_top_lines(text)

        trimmed_text = text[: self.max_input_chars]
        logger.debug("Starting LLM-based name extraction. Character count=%d", len(trimmed_text))

        prompt = f"""
You are an information extraction assistant.

Extract the candidate's full name from the resume text below.

Rules:
- Return only valid JSON.
- Output format must be:
  {{"name": "Full Name"}}
- Return the candidate's actual name only.
- Do not return labels like "Resume", "Profile", or section headings.
- If the name cannot be determined, return:
  {{"name": null}}

Resume text:
\"\"\"
{trimmed_text}
\"\"\"
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": "You extract structured information from resumes.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )

            content = response.choices[0].message.content
            parsed_name = self._parse_name_response(content)

            if parsed_name and self._is_valid_name(parsed_name):
                logger.info("Name extracted successfully using LLM.")
                return parsed_name

            logger.warning("LLM returned no valid name. Falling back to heuristic extraction.")

        except Exception as exc:
            logger.exception("LLM-based name extraction failed: %s", exc)
            pass

        return self._fallback_from_top_lines(text)

    @staticmethod
    def _parse_name_response(content: str) -> Optional[str]:
        if not content:
            logger.warning("Received empty response while parsing extracted name.")
            return None

        try:
            parsed: Any = json.loads(content)
        except json.JSONDecodeError:
            logger.exception("Failed to decode LLM response for name extraction.")
            return None

        value = parsed.get("name")
        if value is None or not isinstance(value, str):
            logger.info("Parsed name response did not contain a valid string name.")
            return None

        value = value.strip()
        return value if value else None

    @staticmethod
    def _fallback_from_top_lines(text: str) -> Optional[str]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        blocked_terms = {
            "resume",
            "curriculum vitae",
            "profile",
            "summary",
            "experience",
            "education",
            "skills",
            "contact",
        }

        for line in lines[:8]:
            cleaned = re.sub(r"^[^A-Za-z]+|[^A-Za-z]+$", "", line)
            cleaned = re.sub(r"\s+", " ", cleaned).strip()

            if not cleaned:
                continue

            if cleaned.lower() in blocked_terms:
                continue

            if 2 <= len(cleaned.split()) <= 4 and re.fullmatch(r"[A-Za-z .'\-]+", cleaned):
                return cleaned.title()
        
        logger.info("No valid name found using fallback heuristic.")
        return None

    @staticmethod
    def _is_valid_name(value: str) -> bool:
        if len(value.split()) < 2:
            return False

        if any(char.isdigit() for char in value):
            return False

        if "@" in value:
            return False

        blocked_terms = {
            "resume",
            "curriculum vitae",
            "profile",
            "summary",
            "experience",
            "education",
            "skills",
            "contact",
        }

        if value.lower() in blocked_terms:
            return False

        return True