import psycopg2
import os

from utils import config
from request.request_hh import Request_HH


class User_Interface:

    db_name = "my_vacancies"
    project_root = os.path.dirname(os.path.dirname(__file__))
    path_to_table_script = os.path.join(project_root, "db_manager", "tables_creation.sql")

    def __init__(self):

        self.request_hh = Request_HH()

        # псевдоним_команды: (описание, команда)
        self.commands = {
            "help":
                ("Показать список доступных команд",
                 self.show_menu),
            "find employers":
                ("Найти и вывести компании по названию",
                 self.request_hh.find_employers),
            "add employers":
                ("Добавить компании в список для поиска вакансий (для добавления используется id компании)",
                 self.request_hh.add_employers),
            "remove employers":
                ("Удалить компании из списка поиска по их id",
                 self.request_hh.remove_employers),
            "show employers":
                ("Показать список компаний, которые используются при поиске вакансий",
                 self.request_hh.show_employers_info),
            "clear employers":
                ("Очистить список компаний, которые используются при поиске вакансий. "
                 f"\033[31mБудьте осторожны, это также очистит список найденных вакансий!\033[0m",
                 self.request_hh.clear_employers),
            "find vacancies":
                ("Найти вакансии. Если список компаний не пуст, будут найдены вакансии этих компаний",
                 self.request_hh.find_vacancies),
            "show vacancies":
                ("Вывести на экран информацию о найденных вакансиях",
                 self.request_hh.show_vacancies_info),
            "clear vacancies":
                ("Очистить список найденных вакансий",
                 self.request_hh.clear_vacancies),
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

    @staticmethod
    def exit():
        print("\nВсего доброго! Заходите ещё!")
        quit()

    # команды, связанные с базой данных
    def save_to_db(self):
        parameters_db = config()

        self._create_db(parameters_db)

        with psycopg2.connect(dbname=self.db_name, **parameters_db) as conn:
            with conn.cursor() as cur:
                cur.execute(self._read_file(self.path_to_table_script))

                self._save_employers(cur)
                self._save_vacancies(cur)

            cur.close()
        conn.close()

        print("\nДанные сохранены в базу данных.")

    def enter_db(self):
        pass

    # вспомогательные
    def _create_db(self, parameters):
        db_name = "postgres"

        conn = psycopg2.connect(dbname=db_name, **parameters)
        cur = conn.cursor()
        conn.autocommit = True

        try:
            cur.execute(f"DROP DATABASE {self.db_name}")
        except psycopg2.errors.InvalidCatalogName:
            pass
        finally:
            cur.execute(f"CREATE DATABASE {self.db_name}")
            cur.close()
            conn.close()

    @staticmethod
    def _read_file(path):
        with open(path, "r", encoding="UTF-8") as file:
            return file.read()

    @staticmethod
    def _get_insert_string(table_name, fields):

        field_names = ", ".join(fields)
        fields_number = ", ".join(['%s'] * len(fields))

        return f"""
               INSERT INTO {table_name} ({field_names})
               VALUES ({fields_number})
               """

    def _save_employers(self, cur):
        for employer in self.request_hh.employers.values():
            fields = (
                "employer_id",
                "name",
                "url",
                "open_vacancies"
            )
            values = (
                employer.employer_id,
                employer.name,
                employer.url,
                employer.open_vacancies
            )
            values = tuple(map(self._convert_to_str, values))
            cur.execute(self._get_insert_string("employers", fields), values)

    def _save_vacancies(self, cur):
        for vacancy in self.request_hh.vacancies.values():

            salary_min = vacancy.salary[0] if vacancy.salary else None
            salary_max = vacancy.salary[1] if vacancy.salary else None

            fields = (
                "vacancy_id",
                "name",
                "city",
                "currency",
                "salary_min",
                "salary_max",
                "url",
                "employer_id"
            )
            values = (
                vacancy.vacancy_id,
                vacancy.name,
                vacancy.city,
                vacancy.currency,
                salary_min,
                salary_max,
                vacancy.url,
                vacancy.employer_id
            )
            values = tuple(map(self._convert_to_str, values))
            cur.execute(self._get_insert_string("vacancies", fields), values)

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
    def _convert_to_str(value):
        if not value:
            return
        return str(value)