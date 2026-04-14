import logging
import fitz
from parsers.base_parser import FileParser

logger = logging.getLogger(__name__)

class PDFParser(FileParser):
    def parse(self, file_path: str) -> str:
        logger.info("Starting PDF parsing for file: %s", file_path)
        try:
            doc = fitz.open(file_path)
            pages = []

            for page_number, page in enumerate(doc, start=1):
                text = page.get_text("text", sort=True)
                if text:
                    pages.append(text)
                    logger.debug(
                        "Extracted text from PDF page %d. Character count=%d",
                        page_number,
                        len(text),
                    )
                else:
                    logger.debug("No extractable text found on PDF page %d", page_number)

            combined_text = "\n".join(pages)
            logger.info(
                "Completed PDF parsing for file: %s. Total characters=%d",
                file_path,
                len(combined_text),
            )
            return combined_text
        except Exception as e:
            logger.exception("Error parsing PDF file: %s", e)
            return ""
