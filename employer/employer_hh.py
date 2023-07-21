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

