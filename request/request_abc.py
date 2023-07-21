from abc import ABC, abstractmethod


class Request(ABC):

    max_vacancies = None

    @staticmethod
    @abstractmethod
    def _get_response(url, parameters=None):
        pass

    @abstractmethod
    def _cyclic_response(self, url, text, number=None):
        pass
