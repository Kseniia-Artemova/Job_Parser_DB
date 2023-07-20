import requests

from vacancies.vacancy_ABC import Vacancy


class Vacancy_HH(Vacancy):

    cbr_rate_url = "https://www.cbr-xml-daily.ru/daily_json.js"

    def __init__(self, vacancy_info: dict):

        self.vacancy_id = vacancy_info.get("id")
        self.name = vacancy_info.get("name")
        self.city = vacancy_info.get("area")
        self.currency = vacancy_info.get("salary")
        self.salary = vacancy_info.get("salary")
        self.employer_id = vacancy_info.get("employer")
        self.url = vacancy_info.get("alternate_url")

    def __str__(self):
        return f"{self.name} (id: {self.vacancy_id})"

    def __repr__(self):
        return f"{self.__class__.__name__}(" \
               f"vacancy_id='{self.vacancy_id}'" \
               f"name='{self.name}'" \
               f"city='{self.city}'" \
               f"salary_from={self.salary[0]}" \
               f"salary_to={self.salary[1]}" \
               f"currency='{self.currency}'" \
               f"employer_id='{self.employer_id}'" \
               f")"

    def __setattr__(self, key, value):
        especial_keys = ("city", "salary", "currency", "employer_id")

        if key in especial_keys and value:

            if key == "city":
                super.__setattr__(self, key, value.get("name"))

            elif key == "currency":
                if type(value) is dict:
                    super.__setattr__(self, key, value.get("currency"))
                else:
                    super.__setattr__(self, key, value)

            elif key == "salary":
                amount_from = value.get("from")
                amount_to = value.get("to")

                if amount_from and self.currency not in ("RUR", None):
                    amount_from = self.convert_currency(amount_from, self.currency)
                if amount_to and self.currency not in ("RUR", None):
                    amount_to = self.convert_currency(amount_to, self.currency)

                self.currency = "RUR"
                super.__setattr__(self, key, (amount_from, amount_to))

            elif key == "employer_id":
                super.__setattr__(self, key, value.get("id"))

        else:
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

    def show_info(self):
        for key, value in self.__dict__.items():
            print(f"{key}: {value}")
