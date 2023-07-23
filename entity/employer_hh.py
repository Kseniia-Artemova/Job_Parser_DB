import dataclasses

from entity.entity_abc import Entity


@dataclasses.dataclass
class Employer_HH(Entity):

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
