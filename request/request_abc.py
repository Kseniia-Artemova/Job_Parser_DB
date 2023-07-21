from abc import ABC, abstractmethod


class Request(ABC):

    max_vacancies = None

    def __init__(self):

        self.vacancies = {}
        self.employers = {}

    @abstractmethod
    def find_employers(self):
        pass

    @abstractmethod
    def add_employers(self):
        pass

    @abstractmethod
    def show_employers_info(self):
        pass

    @abstractmethod
    def clear_employers(self):
        pass

    @abstractmethod
    def find_vacancies(self):
        pass

    @abstractmethod
    def show_vacancies_info(self):
        pass

    @abstractmethod
    def clear_vacancies(self):
        pass

    @staticmethod
    @abstractmethod
    def _get_response(url, parameters=None):
        pass

    @abstractmethod
    def _cyclic_response(self, url, text, number=None):
        pass
