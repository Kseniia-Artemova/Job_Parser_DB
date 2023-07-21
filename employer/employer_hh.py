import dataclasses

from employer.employer_abc import Employer


@dataclasses.dataclass
class Employer_HH(Employer):

    employer_id: str
    name: str
    url: str
    open_vacancies: int

    def __str__(self):
        return f"{self.name} (id: {self.employer_id})"

    def get_fields(self):
        return tuple(self.__dict__.keys())

    def get_values(self):
        return tuple(map(self._convert_to_str, self.__dict__.values()))

    @staticmethod
    def _convert_to_str(value):
        if not value:
            return
        return str(value)

    def get_info(self):
        employer_info = "\n".join([f"{key}: {value}" for key, value in self.__dict__.items()])
        return employer_info
