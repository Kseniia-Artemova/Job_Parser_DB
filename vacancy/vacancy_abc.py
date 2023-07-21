from abc import ABC, abstractmethod


class Vacancy(ABC):

    @abstractmethod
    def convert_currency(self, number: int | None, currency: str | None) -> int:
        pass

    @abstractmethod
    def show_info(self):
        pass

    @abstractmethod
    def get_fields(self):
        pass

    @abstractmethod
    def get_values(self):
        pass

    @staticmethod
    @abstractmethod
    def _convert_to_str(value):
        pass