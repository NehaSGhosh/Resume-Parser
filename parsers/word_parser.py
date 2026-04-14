import logging
from docx import Document

from parsers.base_parser import FileParser

logger = logging.getLogger(__name__)


class WordParser(FileParser):
    """
    Parses Word (.docx) files and extracts text.
    """

    def parse(self, file_path: str) -> str:
        logger.info("Starting Word parsing for file: %s", file_path)
        try:
            doc = Document(file_path)
            text = []

            for index, para in enumerate(doc.paragraphs, start=1):
                if para.text:
                    text.append(para.text)
                    logger.debug(
                        "Extracted paragraph %d from Word file. Character count=%d",
                        index,
                        len(para.text),
                    )

            combined_text = "\n".join(text)
            logger.info(
                "Completed Word parsing for file: %s. Total characters=%d",
                file_path,
                len(combined_text),
            )
            return combined_text
        except Exception as e:
            logger.exception("Error parsing Word file: %s", e)
            return ""
