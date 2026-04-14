import json
import os
import logging
from typing import Any, List
from dotenv import load_dotenv
from openai import OpenAI

from extractors.base_extractor import FieldExtractor
load_dotenv()
logger = logging.getLogger(__name__)

class SkillsExtractor(FieldExtractor):

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        max_input_chars: int = 6000,
    ) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable is not set.")
            raise ValueError("OPENAI_API_KEY environment variable is not set.")

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_input_chars = max_input_chars

    def extract(self, text: str) -> List[str]:
        if not text or not text.strip():
            logger.warning("Skills extraction skipped because input text is empty.")
            return []

        trimmed_text = text[: self.max_input_chars]
        logger.debug("Starting LLM-based skills extraction. Character count=%d", len(trimmed_text))

        prompt = f"""
            You are an information extraction assistant.

            Extract the candidate's technical and professional skills from the resume text below.

            Rules:
            - Return only valid JSON.
            - Output format must be:
            {{"skills": ["skill1", "skill2"]}}
            - Include only actual skills mentioned in the resume.
            - Remove duplicates.
            - Prefer concise normalized skill names.
            - If no skills are found, return:
            {{"skills": []}}

            Resume text:
            \"\"\"
            {trimmed_text}
            \"\"\"
            """

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
        skills = self._parse_skills_response(content)
        logger.info("Skills extraction completed. Count=%d", len(skills))
        return skills

    @staticmethod
    def _parse_skills_response(content: str) -> List[str]:
        if not content:
            logger.warning("Received empty response while parsing extracted skills.")
            return []

        try:
            parsed: Any = json.loads(content)
        except json.JSONDecodeError:
            logger.exception("Failed to decode LLM response for skills extraction.")
            return []

        raw_skills = parsed.get("skills", [])
        if not isinstance(raw_skills, list):
            logger.warning("Parsed skills response is not a list.")
            return []

        cleaned_skills: List[str] = []
        seen = set()

        for skill in raw_skills:
            if not isinstance(skill, str):
                logger.debug("Skipping non-string skill value: %r", skill)
                continue

            normalized = skill.strip()
            if not normalized:
                continue

            dedupe_key = normalized.lower()
            if dedupe_key in seen:
                logger.debug("Skipping duplicate skill: %s", normalized)
                continue

            seen.add(dedupe_key)
            cleaned_skills.append(normalized)

        logger.debug("Skill response parsing completed successfully.")
        return cleaned_skills