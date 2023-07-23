import requests
import json

from data_storage.data_storage_abc import Data_Storage
from entity.vacancy_hh import Vacancy_HH
from entity.employer_hh import Employer_HH


class Data_Storage_HH(Data_Storage):

    url_employers = "https://api.hh.ru/employers"
    url_vacancies = "https://api.hh.ru/vacancies"
    max_vacancies = 500

    def __init__(self):

        self.vacancies = {}
        self.employers = {}

    def find_employers(self):
        employer_name = input("\nВведите название компании: ").lower().strip()

        print("\nПодождите минутку, ищу подходящие компании...")

        results = self._cyclic_response(self.url_employers, employer_name)

        for result in results:
            print(f"\nid: {result.get('id')}"
                  f"\nНазвание: {result.get('name')}"
                  f"\nurl: {result.get('alternate_url')}"
                  f"\nОткрытых вакансий: {result.get('open_vacancies')}")

        print(f"\nВсего найдено: {len(results)}")

    def add_employers(self):
        new_employers = {}

        while True:
            employer_id = input("\nВведите id компании или наберите 'stop' для выхода:\n")
            if employer_id.lower() == "stop":
                break

            url = self.url_employers + "/" + employer_id
            response = self._get_response(url)

            if "errors" in response or not employer_id:
                print("Такой id не найден.")
                continue

            employer = Employer_HH(
                response.get("id"),
                response.get("name"),
                response.get("alternate_url"),
                response.get("open_vacancies")
            )
            new_employers[employer.employer_id] = employer
            print("Компания успешно добавлена в список.")

        self.employers.update(new_employers)

    def show_employers_info(self):
        if not self.employers:
            print("\nСписок компаний пуст.")
            return
        print()
        for employer in self.employers.values():
            print(f"{employer}")

    def clear_employers(self):
        self.vacancies.clear()
        self.employers.clear()
        print("\nСписок компаний очищен.")

    def find_vacancies(self):

        if not self.employers:
            print("\nСначала укажите компании для поиска командой add employers.")
            return

        keyword = input("\nВведите название вакансии или ключевое слово для поиска:\n").lower().strip()

        number = input(f"\nВведите требуемое количество вакансий, но не больше {self.max_vacancies}."
                       f"\nПри превышении максимального количества вакансий будет установлено"
                       f"\nзначение по умолчанию (= 50):\n")

        if not number or int(number) not in range(self.max_vacancies + 1):
            number = 50
        else:
            number = int(number)

        employers = ["employer_id=" + company for company in self.employers.keys()]
        url = self.url_vacancies + "?" + "&".join(employers)

        results = self._cyclic_response(url, keyword, number)[:number]

        if not results:
            print("Вакансии по такому запросу не найдены.")
            return

        for vacancy in results:
            if vacancy.get("id") not in self.vacancies:
                vacancy_object = Vacancy_HH(vacancy)
                self.vacancies[vacancy.get("id")] = vacancy_object
                print()
                print(vacancy_object.get_info())
        print(f"\nВсего найдено {len(results)} вакансий по такому запросу."
              f"\nРезультаты запроса добавлены в общий список.")

    def show_vacancies_info(self):
        if not self.vacancies:
            print("\nСписок вакансий пуст.")
            return
        for vacancy in self.vacancies.values():
            print()
            print(vacancy.get_info())

    def clear_vacancies(self):
        self.vacancies.clear()
        print("\nСписок вакансий очищен.")

    @staticmethod
    def _get_response(url, parameters=None):
        with requests.get(url, parameters) as request:
            response = request.content.decode("utf-8")
            response = json.loads(response)

        return response

    def _cyclic_response(self, url, text, number=None):
        page = 0
        per_page = 50
        parameters = {"text": text, "page": page, "per_page": per_page}
        results = []

        while True:
            response = self._get_response(url, parameters)
            results.extend(response["items"])

            total_pages = response.get("pages")
            parameters["page"] += 1

            if number and len(results) > number:
                break

            if parameters["page"] >= total_pages:
                break

        return results
