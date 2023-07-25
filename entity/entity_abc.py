from abc import ABC, abstractmethod
from typing import Any


class Entity(ABC):
    """
    Абстрактный класс для описания сущности,
    которую планируется добавлять в базу данных
    """

    @abstractmethod
    def get_fields(self) -> tuple[str]:
        """Возвращает название полей для заполнения таблицы в базе данных"""
        pass

    @abstractmethod
    def get_values(self) -> tuple:
        """
        Возвращает значения атрибутов для заполнения таблицы в базе данных.
        Значения должны быть согласованы с названиями полей, возвращаемых get_fields
        и идти в порядке, соответствующем названиям полей.
        Значения должны быть приведены к строковому формату
        """
        pass

    @staticmethod
    def _convert_to_str(value: Any) -> str | None:
        """Преобразует переданное значение в строку"""

        if not value:
            return
        return str(value)

    def get_info(self) -> str:
        """Возвращает информацию об объекте класса в формате строки"""

        entity_info = "\n".join([f"{key}: {value}" for key, value in self.__dict__.items()])
        return entity_info