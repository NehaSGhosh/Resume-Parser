import re
from typing import Optional
import logging
from extractors.base_extractor import FieldExtractor

logger = logging.getLogger(__name__)

class EmailExtractor(FieldExtractor):
    """
    Extracts the first valid email address from resume text using regex.
    """

    EMAIL_PATTERN = re.compile(
        r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b"
    )

    def extract(self, text: str) -> Optional[str]:
        if not text or not text.strip():
            logger.warning("Email extraction skipped because input text is empty.")
            return None
        text = self._normalize_email_text(text)
        match = self.EMAIL_PATTERN.search(text)
        if not match:
            logger.info("No email address found in resume text.")
            return None

        email = match.group(0).strip()
        logger.info("Email extracted successfully.")
        logger.debug("Extracted email domain: %s", email.split("@")[-1])
        return email

    @staticmethod
    def _normalize_email_text(text: str) -> str:
        return (
            text.replace("(at)", "@")
                .replace("[at]", "@")
                .replace(" at ", "@")
                .replace("(dot)", ".")
                .replace("[dot]", ".")
                .replace(" dot ", ".")
        )