import requests
import json
from pprint import pprint


class User_Interface:
    url_companies = "https://api.hh.ru/employers"
    url_vacancies = "https://api.hh.ru/vacancies"

    def __init__(self):

        self.companies = {}
        self.vacancies = []

        # псевдоним_команды: (описание, команда)
        self.commands = {
            "help":
                ("Показать список доступных команд",
                 self.show_menu),
            "find_company":
                ("Найти и вывести компании по названию",
                 self.find_company),
            "add_companies":
                ("Добавить компании в список для поиска вакансий (для добавления используется id компании)",
                 self.add_companies),
            "remove_companies":
                ("Удалить компании из списка поиска по их id",
                 self.remove_companies),
            "show_companies":
                ("Показать список компаний, которые используются при поиске вакансий",
                 self.show_company_list),
            "clean_companies":
                ("Очистить список компаний, которые используются при поиске вакансий",
                 self.companies.clear),
            "find_vacancies":
                ("Найти вакансии. Если список компаний не пуст, будут найдены вакансии этих компаний",
                 self.find_vacancies),
            "clean_vacancies":
                ("Очистить список найденных вакансий",
                 self.vacancies.clear),
            "show_vacancies":
                ("Вывести на экран информацию о найденных вакансиях",
                 self.show_vacancies_info),
            "save_to_db":
                ("Сохранить найденные вакансии в базу данных",
                 self.save_to_db),
            "enter_db":
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
            command = input("\nКоманда: ").lower()
            if command not in self.commands:
                print("Такая команда не существует. Попробуйте ещё раз.")
                continue

            return command

    def _run_command(self, command):
        self.commands[command][1]()

    @staticmethod
    def exit():
        print("\nВсего доброго! Заходите ещё!")
        quit()

    # команды, связанные с компаниями
    def find_company(self):
        company_name = input("\nВведите название компании: ")
        page = 0
        per_page = 50
        results = []

        while True:
            with requests.get(self.url_companies, {"text": company_name,
                                                   "page": page,
                                                   "per_page": per_page}
                              ) as request:

                response = request.content.decode("utf-8")
                response = json.loads(response)

                results.extend(response["items"])

                total_pages = response.get("pages")
                page += 1

            if page >= total_pages:
                break

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

            with requests.get(self.url_companies + "/" + company_id) as request:
                response = request.content.decode("utf-8")
                response = json.loads(response)

                if "errors" in response:
                    print("Такой id не найден.")
                    continue

                new_companies[response.get("id")] = (response.get("name"), response.get("alternate_url"))
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
                removed_companies.append(company_info[0])

        print(f"Успешно удалены компании: {', '.join(removed_companies)}")

    def show_company_list(self):
        for company_id, company_info in self.companies.items():
            print(f"\nid: {company_id}"
                  f"\nНазвание: {company_info[0]}"
                  f"\nurl: {company_info[1]}")

    # команды, связанные с вакансиями
    def find_vacancies(self):
        pass

    def show_vacancies_info(self):
        pass

    # команды, связанные с базой данных
    def save_to_db(self):
        pass

    def enter_db(self):
        pass
