import logging
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class FieldExtractor(ABC):
    @abstractmethod
    def extract(self, text: str):
        logger.debug("Abstract extract called on %s", self.__class__.__name__)
        raise NotImplementedError
