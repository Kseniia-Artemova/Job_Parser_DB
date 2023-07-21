import requests
import json

from vacancy.vacancy_hh import Vacancy_HH
from employer.employer_hh import Employer_HH


class Request_HH:
    url_employers = "https://api.hh.ru/employers"
    url_vacancies = "https://api.hh.ru/vacancies"
    max_vacancies = 500

    def __init__(self):

        self.vacancies = {}
        self.employers = {}

    def find_employers(self):
        employer_name = input("\nВведите название компании: ").lower().strip()

        results = self._cyclic_response(self.url_employers, employer_name)

        print(f"\nВсего найдено: {len(results)}")

        for result in results:
            print(f"\nid: {result.get('id')}"
                  f"\nНазвание: {result.get('name')}"
                  f"\nurl: {result.get('alternate_url')}")

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

    def remove_employers(self):
        removed_employers = []
        employer_ids = input("\nВведите id компании или компаний, которые следует удалить."
                             "\nid должны вводиться в одну строку и разделаться пробелом."
                             "\nНапример: 19833 67432 87566723\n").split()

        for employer_id in employer_ids:
            employer_info = self.employers.pop(employer_id.strip(), False)
            if employer_info:
                removed_employers.append(employer_info)

        removed_employers = list(map(str, removed_employers))
        print(f"Успешно удалены компании: {', '.join(removed_employers)}")

    def show_employers_info(self):
        if not self.employers:
            print("\nСписок компаний пуст.")
            return
        for employer in self.employers.values():
            print(f"{employer}")

    def clear_employers(self):
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
                vacancy_object.show_info()
        print(f"\nВсего найдено {len(results)} вакансий по такому запросу."
              f"\nРезультаты запроса добавлены в общий список.")

    def show_vacancies_info(self):
        for vacancy in self.vacancies:
            print()
            vacancy.show_info()

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