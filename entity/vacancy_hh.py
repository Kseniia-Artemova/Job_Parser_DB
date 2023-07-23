import requests

from entity.entity_abc import Entity


class Vacancy_HH(Entity):

    cbr_rate_url = "https://www.cbr-xml-daily.ru/daily_json.js"

    def __init__(self, vacancy_info: dict):

        self.vacancy_id = vacancy_info.get("id")
        self.name = vacancy_info.get("name")
        self.location = vacancy_info.get("area")
        self.currency = vacancy_info.get("salary")
        self.salary = vacancy_info.get("salary")
        self.url = vacancy_info.get("alternate_url")
        self.employer_id = vacancy_info.get("employer")

    def __str__(self):
        return f"{self.name} (id: {self.vacancy_id})"

    def __repr__(self):
        return f"{self.__class__.__name__}(" \
               f"vacancy_id='{self.vacancy_id}'" \
               f"name='{self.name}'" \
               f"location='{self.location}'" \
               f"currency='{self.currency}'" \
               f"salary={self.salary}" \
               f"url='{self.url}'" \
               f"employer_id='{self.employer_id}'" \
               f")"

    def __setattr__(self, key, value):
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

    def get_fields(self):
        fields = []
        for key in self.__dict__.keys():
            if key == "salary":
                fields.extend(["salary_min", "salary_max"])
                continue
            fields.append(key)

        return tuple(fields)

    def get_values(self):
        values = []
        for value in self.__dict__.values():
            if isinstance(value, tuple):
                values.extend([*value])
                continue
            values.append(value)

        return tuple(map(self._convert_to_str, values))
