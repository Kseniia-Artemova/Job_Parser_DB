from abc import ABC, abstractmethod


class Entity(ABC):

    @abstractmethod
    def get_fields(self):
        pass

    @abstractmethod
    def get_values(self):
        pass

    @staticmethod
    def _convert_to_str(value):
        if not value:
            return
        return str(value)

    def get_info(self):
        entity_info = "\n".join([f"{key}: {value}" for key, value in self.__dict__.items()])
        return entity_info