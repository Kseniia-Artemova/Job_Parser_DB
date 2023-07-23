import psycopg2
import os
from prettytable import PrettyTable

from utils import config, accept_command, run_command


class DB_Manager:
    db_config_file = "db_config_target.ini"

    def __init__(self):
        self.db_parameters = config(self._build_path_to_file(self.db_config_file))
        self.commands = {
            "help":
                ("Показать список доступных команд",
                 self.show_menu),
            "1":
                ("Вывести список всех компаний и количество вакансий у каждой компании",
                 self.get_companies_and_vacancies_count),
            "2":
                ("Вывести список всех вакансий с указанием названия компании",
                 self.get_all_vacancies),
            "3":
                ("Вывести среднюю зарплату по вакансиям",
                 self.get_avg_salary),
            "4":
                ("Вывести список всех вакансий, у которых зарплата выше средней по всем вакансиям",
                 self.get_vacancies_with_higher_salary),
            "5":
                ("Вывести список всех вакансий, в названии которых содержатся переданные в метод слова, например 'python'",
                 self.get_vacancies_with_keyword),
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
            run_command(self.commands, command)

    def show_menu(self):
        print()
        for command, description in self.commands.items():
            print(f"\t\033[34m{command}\033[0m - {description[0]}")

    @staticmethod
    def _build_path_to_file(file_name):
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        return os.path.join(project_root, current_dir, file_name)

    def _make_connection(self):
        conn = psycopg2.connect(**self.db_parameters)
        cur = conn.cursor()

        return conn, cur

    @staticmethod
    def _end_connection(conn, cur):
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def _create_table(cur, data):
        table = PrettyTable()
        table.field_names = [desc[0] for desc in cur.description]
        for row in data:
            table.add_row(row)
        return table

    def get_companies_and_vacancies_count(self):
        conn, cur = self._make_connection()
        cur.execute("""
            SELECT 
                e.employer_id,
                e.name,
                open_vacancies,
                COUNT(vacancy_id) AS number_vacancies
            FROM employers e
            JOIN vacancies v
                USING(employer_id)
            GROUP BY e.employer_id;
        """)

        response = self._create_table(cur, cur.fetchall())
        self._end_connection(conn, cur)

        print(response)

    def get_all_vacancies(self):
        conn, cur = self._make_connection()
        cur.execute("""
            SELECT 
                vacancy_id,
                v.name,
                location,
                currency,
                salary_min,
                salary_max,
                v.url,
                e.name AS employer_name
            FROM vacancies v
            JOIN employers e
                USING(employer_id);
        """)

        response = self._create_table(cur, cur.fetchall())
        self._end_connection(conn, cur)

        print(response)

    def get_avg_salary(self):
        conn, cur = self._make_connection()
        cur.execute("""
            SELECT ROUND(AVG((salary_min + salary_max) / 2)) AS avg_salary
            FROM vacancies;
        """)

        response = self._create_table(cur, cur.fetchall())
        self._end_connection(conn, cur)

        print(response)

    def get_vacancies_with_higher_salary(self):
        conn, cur = self._make_connection()
        cur.execute("""
            SELECT *
            FROM vacancies
            WHERE (salary_min + salary_max) / 2 > (
                SELECT AVG((salary_min + salary_max) / 2)
                FROM vacancies
                );
        """)

        response = self._create_table(cur, cur.fetchall())
        self._end_connection(conn, cur)

        print(response)

    def get_vacancies_with_keyword(self):
        keyword = input("\nПожалуйста, введите ключевое слово для поиска совпадений в списке вакансий:\n")
        conn, cur = self._make_connection()
        cur.execute(f"""
            SELECT *
            FROM vacancies
            WHERE name LIKE '%{keyword.capitalize()}%' OR name LIKE '%{keyword.lower()}%';
        """)

        response = self._create_table(cur, cur.fetchall())
        self._end_connection(conn, cur)

        print(response)
