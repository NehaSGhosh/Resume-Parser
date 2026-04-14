import logging
from parsers.base_parser import FileParser
from core.resume_extractor import ResumeExtractor
from models.resume_data import ResumeData

logger = logging.getLogger(__name__)

class ResumeParserFramework:
    """
    Combines a file parser and a resume extractor into one end-to-end framework.
    """

    def __init__(self, parser: FileParser, extractor: ResumeExtractor) -> None:
        self.parser = parser
        self.extractor = extractor

    def parse_resume(self, file_path: str) -> ResumeData:
        """
        Parse a resume file into structured ResumeData.
        """
        logger.info("Framework parsing started for file: %s", file_path)
        raw_text = self.parser.parse(file_path)
        logger.debug("Raw text extracted. Character count=%d", len(raw_text))

        result = self.extractor.extract(raw_text)
        logger.info("Framework parsing completed for file: %s", file_path)
        return result