import requests

from entity.entity_abc import Entity
from typing import Any


class Vacancy_HH(Entity):
    """Класс для описания вакансии, полученной с сайта https://hh.ru"""

    # ссылка на данные о текущем курсе валют центрального банка России
    cbr_rate_url = "https://www.cbr-xml-daily.ru/daily_json.js"

    def __init__(self, vacancy_info: dict) -> None:
        """
        Инициализатор класса, задаёт свойства объекта класса,
        используя полученный словарь с данными
        """

        self.vacancy_id = vacancy_info.get("id")
        self.name = vacancy_info.get("name")
        self.location = vacancy_info.get("area")
        self.currency = vacancy_info.get("salary")
        self.salary = vacancy_info.get("salary")
        self.url = vacancy_info.get("alternate_url")
        self.employer_id = vacancy_info.get("employer")

    def __str__(self) -> str:
        """Строковое представление вакансии для пользователя"""

        return f"{self.name} (id: {self.vacancy_id})"

    def __repr__(self) -> str:
        """Строковое представление вакансии для режима отладки"""

        return f"{self.__class__.__name__}(" \
               f"vacancy_id='{self.vacancy_id}'" \
               f"name='{self.name}'" \
               f"location='{self.location}'" \
               f"currency='{self.currency}'" \
               f"salary={self.salary}" \
               f"url='{self.url}'" \
               f"employer_id='{self.employer_id}'" \
               f")"

    def __setattr__(self, key: str, value: Any) -> None:
        """
        Настраивает установление значений для некоторых ключей, значения которых могут обладать
        большей вложенностью, чем остальные.
        Также конвертирует сумму зарплаты в рубли, если она представлена в другой валюте

        :param key: имя свойства класса
        :param value: значение свойства класса
        """

        especial_keys = ("location", "salary", "currency", "employer_id")

        if key in especial_keys and value:

            if key == "location":
                value = value.get("name")

            elif key == "currency":
                if type(value) is dict:
                    value = value.get("currency")

            elif key == "salary":
                amount_from = value.get("from")
                amount_to = value.get("to")

                if amount_from and self.currency not in ("RUR", None):
                    amount_from = self.convert_currency(amount_from, self.currency)
                if amount_to and self.currency not in ("RUR", None):
                    amount_to = self.convert_currency(amount_to, self.currency)

                self.currency = "RUR"
                value = (amount_from, amount_to)

            elif key == "employer_id":
                value = value.get("id")

        elif key == "salary" and not value:
            value = (None, None)

        super.__setattr__(self, key, value)

    def convert_currency(self, number: int | None, currency: str | None) -> int:
        """
        Конвертирует сумму в иностранной валюте в эквивалентную сумму в рублях,
        основываясь на данных ЦБР, получаемых с сайта
        """

        response = requests.get(self.cbr_rate_url)
        if response.status_code != 200:
            raise requests.RequestException("Ошибка при загрузке словаря с текущим курсом валют")
        currency_dictionary = response.json().get("Valute")

        number_rub = 0

        if currency in currency_dictionary and number:
            rate = currency_dictionary[currency]["Value"] / currency_dictionary[currency]["Nominal"]
            number_rub = int(rate * number)

        return number_rub

    def get_fields(self) -> tuple[str]:
        """Возвращает название полей для заполнения таблицы в базе данных"""

        fields = []
        for key in self.__dict__.keys():
            if key == "salary":
                fields.extend(["salary_min", "salary_max"])
                continue
            fields.append(key)

        return tuple(fields)

    def get_values(self) -> tuple:
        """
        Возвращает значения атрибутов для заполнения таблицы в базе данных.
        Значения должны быть согласованы с названиями полей, возвращаемых get_fields
        и идти в порядке, соответствующем названиям полей.
        Значения должны быть приведены к строковому формату
        """

        values = []
        for value in self.__dict__.values():
            if isinstance(value, tuple):
                values.extend([*value])
                continue
            values.append(value)

        return tuple(map(self._convert_to_str, values))
