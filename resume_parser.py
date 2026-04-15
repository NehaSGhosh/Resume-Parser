import argparse
import json
import logging
from pathlib import Path

from core.framework import ResumeParserFramework
from core.resume_extractor import ResumeExtractor
from extractors.email_extractor import EmailExtractor
from extractors.name_extractor import NameExtractor
from extractors.skills_extractor import SkillsExtractor
from parsers.pdf_parser import PDFParser
from parsers.word_parser import WordParser
from utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def get_parser(file_path: str):
    suffix = Path(file_path).suffix.lower()
    logger.debug("Selecting parser for suffix: %s", suffix)

    if suffix == ".pdf":
        logger.debug("Using PDFParser for file: %s", file_path)
        return PDFParser()
    if suffix == ".docx":
        logger.info("Using WordParser for file: %s", file_path)
        return WordParser()

    logger.error("Unsupported file type encountered: %s", suffix)
    raise ValueError(f"Unsupported file type: {suffix}. Supported types are .pdf and .docx")


def build_framework(file_path: str) -> ResumeParserFramework:
    """
    Build the resume parsing framework with the appropriate parser
    and configured field extractors.
    """
    logger.debug("Building resume parsing framework for file: %s", file_path)
    parser = get_parser(file_path)

    extractors = {
        "name": NameExtractor(),
        "email": EmailExtractor(),
        "skills": SkillsExtractor(),
    }
    logger.debug("Configured extractors: %s", sorted(extractors.keys()))

    resume_extractor = ResumeExtractor(extractors=extractors)
    logger.debug("Resume parsing framework built successfully.")
    return ResumeParserFramework(parser=parser, extractor=resume_extractor)


def format_output(data: dict) -> str:
    logger.debug("Formatting output for parsed resume data.")
    skills = data.get("skills", [])
    skills_inline = json.dumps(skills)

    return (
        "{\n"
        f'\t"name": {json.dumps(data.get("name"))},\n'
        f'\t"email": {json.dumps(data.get("email"))},\n'
        f'\t"skills": {skills_inline}\n'
        "}"
    )

def parse_resume(file_path: str) -> dict:
    """
    Parse a resume file and return the extracted data as a dictionary.
    """
    logger.info("Starting resume parsing for file: %s", file_path)

    framework = build_framework(file_path)
    result = framework.parse_resume(file_path)

    logger.info("Resume parsing execution completed successfully for file: %s", file_path)

    return {
        "name": result.name,
        "email": result.email,
        "skills": result.skills,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse a resume file and extract name, email, and skills."
    )
    parser.add_argument(
        "file_path",
        type=str,
        help="Path to the resume file (.pdf or .docx)",
    )

    args = parser.parse_args()
    file_path = args.file_path

    if not Path(file_path).exists():
        logger.error("File not found: %s", file_path)
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        parsed_data = parse_resume(file_path)
        print(format_output(parsed_data))
    except Exception as exc:
        logger.exception("Failed to parse resume: %s", exc)
        raise


if __name__ == "__main__":
    main()