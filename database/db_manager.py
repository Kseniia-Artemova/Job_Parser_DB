import psycopg2
import os
from prettytable import PrettyTable

from utils import config, accept_command, run_command


class DB_Manager:

    db_config_file = "db_config_target.ini"
    queries_file = "queries.sql"

    def __init__(self):
        self.db_parameters = config(self._build_path_to_file(self.db_config_file))
        self.text_queries = self._read_sql_file(self._build_path_to_file(self.queries_file)).split(";")
        self.commands = {
            "help":
                ("Показать список доступных команд",
                 self.show_menu),
            "1":
                ("Вывести список всех компаний и количество вакансий у каждой компании",
                 self.run_sql_query),
            "2":
                ("Вывести список всех вакансий с указанием названия компании",
                 self.run_sql_query),
            "3":
                ("Вывести среднюю зарплату по вакансиям",
                 self.run_sql_query),
            "4":
                ("Вывести список всех вакансий, у которых зарплата выше средней по всем вакансиям",
                 self.run_sql_query),
            "5":
                ("Вывести список всех вакансий, в названии которых содержатся переданное в метод слово, например 'python'",
                 self.run_sql_query),
            "exit":
                ("Выход из программы", None)
        }

    def __call__(self):
        print(f"\nВы вошли в режим работы с базой данных."
              f"\nПожалуйста, выберите одно из доступных действий:")

        self.show_menu()

        while True:
            command = accept_command(self.commands)
            if command == "exit":
                print("\nВы вышли из режима работы с базой данных.")
                return
            elif command in ("1", "2", "3", "4", "5"):
                substitutions = None
                if command == "5":
                    substitutions = self._get_substitutions()
                run_command(self.commands, command, command, substitutions)
            else:
                run_command(self.commands, command)

    # Команды основного меню
    def show_menu(self):
        print()
        for command, description in self.commands.items():
            print(f"\t\033[34m{command}\033[0m - {description[0]}")

    def run_sql_query(self, command, substitutions=None):

        query = self._get_query(command)

        if substitutions:
            for substitution in substitutions:
                query = query.replace("placeholder", substitution, 1)

        conn = psycopg2.connect(**self.db_parameters)
        cur = conn.cursor()
        cur.execute(query)
        response = self._create_table(cur, cur.fetchall())

        conn.commit()
        cur.close()
        conn.close()

        print(response)

    # Вспомогательные функции
    @staticmethod
    def _build_path_to_file(file_name):
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        return os.path.join(project_root, current_dir, file_name)

    @staticmethod
    def _read_sql_file(path_to_file):
        with open(path_to_file, "r", encoding="UTF-8") as file:
            text = file.read()
        return text

    @staticmethod
    def _create_table(cur, data):
        table = PrettyTable()
        table.field_names = [desc[0] for desc in cur.description]
        for row in data:
            table.add_row(row)
        return table

    def _get_query(self, command):
        comment = self.commands[command][0]
        query = ""
        for text in self.text_queries:
            if "-- " + comment in text:
                query = text
                break

        return query

    @staticmethod
    def _get_substitutions():
        keyword = input("\nПожалуйста, введите ключевое слово для поиска совпадений в списке вакансий:\n")
        return keyword.capitalize(), keyword.lower()
