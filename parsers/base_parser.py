import logging
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class FileParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> str:
        logger.debug("Abstract parse called on %s", self.__class__.__name__)
        raise NotImplementedError
