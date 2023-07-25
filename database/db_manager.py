import psycopg2
from prettytable import PrettyTable
from psycopg2.extensions import cursor

from database.db_interaction_abc import DB_Interaction
from mixins.user_interaction import User_Interaction_Mixin


class DB_Manager(DB_Interaction, User_Interaction_Mixin):
    """
    Класс для выполнения запросов к базе данных, получения результатов запроса
    и вывода их на экран
    """

    # названия ключевых файлов, использующихся для подключения,
    # и выполнения запросов к базе данных
    db_config_file = "db_config_target.ini"
    queries_file = "queries.sql"

    # цвет текста меню
    text_color = "\033[34m"

    def __init__(self) -> None:
        """
        Инициализатор объектов класса.

        Строит пути к конфигурационным файлам и sql-скриптам;
        Получает текст sql-скрипта из файла queries_file;
        Устанавливает соединение с базой данных;
        Инициализирует меню
        """

        self.db_parameters = self.config(self._build_path_to_file(self.db_config_file))
        self.text_queries = self._read_script(self._build_path_to_file(self.queries_file)).split(";")

        self.conn = None
        self.make_connection()

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
                ("Вывести список всех вакансий, в названии которых содержится указанное слово, например 'python'",
                 self.get_vacancies_with_keyword),
            "exit":
                ("Выход из программы", None)
        }

    def __call__(self) -> None | list:
        """
        Запускает скрипт взаимодействия с пользователем при вызове объекта класса.
        Готовность принять команду от пользователя сохраняется до ввода команды выхода "exit"

        При завершении возвращает результаты SQL-запросов, если такие были в течение сессии
        """

        print(f"\nВы вошли в режим работы с базой данных."
              f"\nПожалуйста, выберите одно из доступных действий:")

        self.show_menu()

        results = []

        while True:
            command = self.accept_command()
            if command == "exit":
                print("\nВы вышли из режима работы с базой данных.")
                return results
            elif command.isdigit():
                result = self.run_command(command)
                results.append(result)
            else:
                self.run_command(command)

    # Команды основного меню
    def make_connection(self) -> None:
        """Устанавливает соединение с базой данных"""
        setattr(self, "conn", psycopg2.connect(**self.db_parameters))

    def close_connection_db(self) -> None:
        """Закрывает соединение с базой данных"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def get_companies_and_vacancies_count(self) -> list[tuple]:
        """Возвращает список всех компаний и количество вакансий у каждой компании"""

        return self._run_sql_query("1")

    def get_all_vacancies(self) -> list[tuple]:
        """Возвращает список всех вакансий с указанием названия компании"""

        return self._run_sql_query("2")

    def get_avg_salary(self) -> list[tuple]:
        """Возвращает среднюю зарплату по вакансиям"""

        return self._run_sql_query("3")

    def get_vacancies_with_higher_salary(self) -> list[tuple]:
        """Возвращает список всех вакансий, у которых зарплата выше средней по всем вакансиям"""

        return self._run_sql_query("4")

    def get_vacancies_with_keyword(self) -> list[tuple] | None:
        """
        Запрашивает у пользователя слово, которое будет использовано в качестве ключевого
        при выполнении SQL-запроса.
        Возвращает список всех вакансий, в названии которых содержится указанное слово
        """

        keyword = input("\nПожалуйста, введите ключевое слово для поиска совпадений в списке вакансий:\n")
        while not keyword:
            keyword = input("\nНевозможно выполнить запрос без ключевого слова."
                            "\nПопробуйте ещё раз или введите 'stop' для отмены запроса:\n")
            if keyword.lower().strip() == "stop":
                return

        substitutions = (keyword.capitalize(), keyword.lower())
        return self._run_sql_query("5", substitutions)

    # Вспомогательные методы
    def _run_sql_query(self, command: str, substitutions: tuple | None = None) -> list[tuple]:
        """
        Возвращает результат SQL-запроса в зависимости от выбранной
        пользователем команды меню в виде списка кортежей.
        Выводит результат запроса на экран в виде таблицы

        :param command: команда, введённая пользователем
        :param substitutions: опциональный параметр, используется для вставки в запрос каких-то значений,
                              полученных от пользователя
        """

        query = self._get_query(command)

        if substitutions:
            for substitution in substitutions:
                query = query.replace("placeholder", substitution, 1)

        cur = self.conn.cursor()
        cur.execute(query)
        response = cur.fetchall()
        print(self._create_table(cur, response))

        self.conn.commit()
        cur.close()

        return response

    @staticmethod
    def _create_table(cur: cursor, data: list[tuple]) -> PrettyTable:
        """
        Создаёт и возвращает объект PrettyTable, представляющий собой
        таблицу для вывода данных на экран

        :param cur: объект cursor библиотеки psycopg2, представляющий собой интерфейс
                    для выполнения SQL-запросов и получения результатов
        :param data: данные, полученные в результате исполнения запроса

        :return: объект таблицы (PrettyTable) библиотеки prettytable
        """

        table = PrettyTable()
        table.field_names = [desc[0] for desc in cur.description]
        for row in data:
            table.add_row(row)
        return table

    def _get_query(self, command: str) -> str:
        """
        Возвращает строку sql-запроса, которая соответствует заданному в меню описанию действия

        :param command: команда, введённая пользователем
        """

        comment = self.commands[command][0]
        query = ""
        for text in self.text_queries:
            if "-- " + comment in text:
                query = text
                break

        return query
