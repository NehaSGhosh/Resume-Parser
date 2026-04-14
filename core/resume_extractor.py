from typing import Dict
import logging

from models.resume_data import ResumeData
from extractors.base_extractor import FieldExtractor

logger = logging.getLogger(__name__)

class ResumeExtractor:
    """
    Coordinates extraction of all resume fields using field-specific extractors.
    """

    REQUIRED_FIELDS = {"name", "email", "skills"}

    def __init__(self, extractors: Dict[str, FieldExtractor]) -> None:
        missing_fields = self.REQUIRED_FIELDS - set(extractors.keys())
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            logger.error("ResumeExtractor initialization failed. Missing extractors: %s", missing)
            raise ValueError(f"Missing required extractors: {missing}")

        self.extractors = extractors
        logger.debug("ResumeExtractor initialized with extractors: %s", sorted(extractors.keys()))

    def extract(self, text: str) -> ResumeData:
        """
        Extract structured resume data from raw text.
        """
        if text is None:
            logger.error("Received None as input text.")
            raise ValueError("Input text cannot be None.")

        name = self.extractors["name"].extract(text)
        logger.debug("Name extraction complete. Found=%s", bool(name))

        email = self.extractors["email"].extract(text)
        logger.debug("Email extraction complete. Found=%s", bool(email))

        skills = self.extractors["skills"].extract(text)
        logger.debug("Skills extraction complete. Count=%d", len(skills))

        logger.info("All field extraction completed successfully.")
        return ResumeData(
            name=name,
            email=email,
            skills=skills,
        )