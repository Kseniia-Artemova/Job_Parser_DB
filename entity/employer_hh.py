import dataclasses

from entity.entity_abc import Entity


@dataclasses.dataclass
class Employer_HH(Entity):
    """Класс для описания компании-нанимателя, полученной с сайта https://hh.ru"""

    employer_id: str
    name: str
    url: str
    open_vacancies: int

    def __str__(self) -> str:
        """Строковое представление вакансии для пользователя"""
        return f"{self.name} (id: {self.employer_id})"

    def get_fields(self) -> tuple[str]:
        """Возвращает название полей для заполнения таблицы в базе данных"""
        return tuple(self.__dict__.keys())

    def get_values(self) -> tuple:
        """
        Возвращает значения атрибутов для заполнения таблицы в базе данных.
        Значения должны быть согласованы с названиями полей, возвращаемых get_fields
        и идти в порядке, соответствующем названиям полей.
        Значения должны быть приведены к строковому формату
        """

        return tuple(map(self._convert_to_str, self.__dict__.values()))
