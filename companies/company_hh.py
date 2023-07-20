import dataclasses

from companies.company_ABC import Company


@dataclasses.dataclass
class Company_HH(Company):

    company_id: str
    name: str
    url: str
    open_vacancies: int

    def __str__(self):
        return f"{self.name} (id: {self.company_id})"
