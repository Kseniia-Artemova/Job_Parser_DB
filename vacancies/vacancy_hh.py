from vacancies.vacancy_ABC import Vacancy


class Vacancy_HH(Vacancy):

    def __init__(self, vacancy_info: dict):

        self.vacancy_id = vacancy_info.get("id")
        self.name = vacancy_info.get("name")
        self.city = vacancy_info.get("area")
        self.salary_from = vacancy_info.get("salary")
        self.salary_to = vacancy_info.get("salary")
        self.currency = vacancy_info.get("salary")
        self.employer_id = vacancy_info.get("employer")

    def __setattr__(self, key, value):
        especial_keys = ("city", "salary_from", "salary_to", "currency", "employer_id")
        if key in especial_keys and value:
            if key == "city":
                super.__setattr__(self, key, value.get("name"))
            elif key == "salary_from":
                super.__setattr__(self, key, value.get("from"))
            elif key == "salary_to":
                super.__setattr__(self, key, value.get("to"))
            elif key == "currency":
                super.__setattr__(self, key, value.get("currency"))
            elif key == "employer_id":
                super.__setattr__(self, key, value.get("id"))
        else:
            super.__setattr__(self, key, value)

    def __str__(self):
        return f"{self.name} (id: {self.vacancy_id})"

    def __repr__(self):
        return f"{self.__class__.__name__}(" \
               f"vacancy_id='{self.vacancy_id}'" \
               f"name='{self.name}'" \
               f"city='{self.city}'" \
               f"salary_from={self.salary_from}" \
               f"salary_to={self.salary_to}" \
               f"currency='{self.currency}'" \
               f"employer_id='{self.employer_id}'" \
               f")"

    def get_info(self):
        pass



