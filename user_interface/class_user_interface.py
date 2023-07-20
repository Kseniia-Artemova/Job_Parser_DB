import requests
import json
from pprint import pprint

from companies.company_hh import Company_HH
from vacancies.vacancy_hh import Vacancy_HH


class User_Interface:

    url_companies = "https://api.hh.ru/employers"
    url_vacancies = "https://api.hh.ru/vacancies"

    max_vacancies = 500

    def __init__(self):

        self.companies = {}
        self.vacancies = {}

        # псевдоним_команды: (описание, команда)
        self.commands = {
            "help":
                ("Показать список доступных команд",
                 self.show_menu),
            "find company":
                ("Найти и вывести компании по названию",
                 self.find_company),
            "add companies":
                ("Добавить компании в список для поиска вакансий (для добавления используется id компании)",
                 self.add_companies),
            "remove companies":
                ("Удалить компании из списка поиска по их id",
                 self.remove_companies),
            "show companies":
                ("Показать список компаний, которые используются при поиске вакансий",
                 self.show_company_list),
            "clean companies":
                ("Очистить список компаний, которые используются при поиске вакансий",
                 self.companies.clear),
            "find vacancies":
                ("Найти вакансии. Если список компаний не пуст, будут найдены вакансии этих компаний",
                 self.find_vacancies),
            "clean vacancies":
                ("Очистить список найденных вакансий",
                 self.vacancies.clear),
            "show vacancies":
                ("Вывести на экран информацию о найденных вакансиях",
                 self.show_vacancies_info),
            "save to db":
                ("Сохранить найденные вакансии в базу данных",
                 self.save_to_db),
            "enter db":
                ("Войти в режим взаимодействия с базой данных",
                 self.enter_db),
            "exit":
                ("Выйти из программы",
                 self.exit)
        }

    # общие команды
    def show_menu(self):
        print()
        for command, description in self.commands.items():
            print(f"\t\033[32m{command}\033[0m - {description[0]}")

    def __call__(self):
        print("Добрый день! Я помогу вам найти вакансии и организовать их в список.")
        print("Пожалуйста, выберите и введите команду.")
        self.show_menu()

        while True:
            command = self._accept_command()
            self._run_command(command)

    def _accept_command(self):
        while True:
            command = input("\nКоманда: ").lower().strip()
            if command not in self.commands:
                print("Такая команда не существует. Попробуйте ещё раз.")
                continue

            return command

    def _run_command(self, command):
        self.commands[command][1]()

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

    @staticmethod
    def exit():
        print("\nВсего доброго! Заходите ещё!")
        quit()

    # команды, связанные с компаниями
    def find_company(self):
        company_name = input("\nВведите название компании: ").lower().strip()

        results = self._cyclic_response(self.url_companies, company_name)

        print(f"\nВсего найдено: {len(results)}")

        for result in results:
            print(f"\nid: {result.get('id')}"
                  f"\nНазвание: {result.get('name')}"
                  f"\nurl: {result.get('alternate_url')}")

    def add_companies(self):
        new_companies = {}

        while True:
            company_id = input("\nВведите id компании или наберите 'stop' для выхода:\n")
            if company_id.lower() == "stop":
                break

            url = self.url_companies + "/" + company_id
            response = self._get_response(url)

            if "errors" in response:
                print("Такой id не найден.")
                continue

            company = Company_HH(
                response.get("id"),
                response.get("name"),
                response.get("alternate_url"),
                response.get("open_vacancies")
            )
            new_companies[company.company_id] = company
            print("Компания успешно добавлена в список.")

        self.companies.update(new_companies)

    def remove_companies(self):
        removed_companies = []
        company_ids = input("\nВведите id компании или компаний, которые следует удалить."
                            "\nid должны вводиться в одну строку и разделаться пробелом."
                            "\nНапример: 19833 67432 87566723\n").split()

        for company_id in company_ids:
            company_info = self.companies.pop(company_id.strip(), False)
            if company_info:
                removed_companies.append(company_info)

        removed_companies = list(map(str, removed_companies))
        print(f"Успешно удалены компании: {', '.join(removed_companies)}")

    def show_company_list(self):
        for company_id, company_info in self.companies.items():
            print(f"\nid: {company_id}"
                  f"\nНазвание: {company_info.name}"
                  f"\nurl: {company_info.url}")

    # команды, связанные с вакансиями
    def find_vacancies(self):
        keyword = input("\nВведите название вакансии или ключевое слово для поиска:\n").lower().strip()

        number = int(input(f"\nВведите требуемое количество вакансий, но не больше {self.max_vacancies}."
                           f"\nПри превышении максимального количества вакансий будет установлено"
                           f"\nзначение по умолчанию (= 50):\n"))

        number = number if number in range(501) else 50

        employers = ["employer_id=" + company for company in self.companies.keys()]
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
                print(vacancy_object.__dict__.items(), sep="\n")

    def show_vacancies_info(self):
        print(*self.vacancies, sep="\n")

    # команды, связанные с базой данных
    def save_to_db(self):
        pass

    def enter_db(self):
        pass
