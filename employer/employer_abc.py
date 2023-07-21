from abc import ABC, abstractmethod


class Employer(ABC):

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def get_fields(self):
        pass

    @abstractmethod
    def get_info(self):
        pass

    @staticmethod
    @abstractmethod
    def _convert_to_str(value):
        pass

