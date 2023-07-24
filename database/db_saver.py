import psycopg2
import os

from utils import config
from entity.entity_abc import Entity


class DB_Saver:
    """Класс, позволяющий сохранять переданную информацию в базу данных"""

    # названия ключевых файлов, использующихся для подключения,
    # создания и наполнения базы данных и таблиц
    table_script = "tables_creation.sql"
    starting_db = "db_config_starting.ini"
    target_db = "db_config_target.ini"

    def __init__(self) -> None:
        """
        Инициализатор объектов класса.

        Строит пути к конфигурационным файлам и sql-скриптам;
        Создаёт базу данных;
        Создаёт необходимые таблицы, прописанные в файле скрипта table_script.
        """

        self.path_to_starting_config = self._build_path_to_file(self.starting_db)
        self.path_to_target_config = self._build_path_to_file(self.target_db)
        self.path_to_table_script = self._build_path_to_file(self.table_script)

        self.starting_parameters_db = config(self.path_to_starting_config)
        self.target_parameters_db = config(self.path_to_target_config)

        self._create_db()
        self.run_sql_script(self.path_to_table_script, self.target_parameters_db)

    @staticmethod
    def _build_path_to_file(file_name: str) -> str:
        """
        Строит путь к указанному файлу, при условии что он находится в той же директории,
        что и файл класса
        """

        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        return os.path.join(project_root, current_dir, file_name)

    def _create_db(self) -> None:
        """Создаёт базу данных с именем, указанным в конфигурационном файле target_db"""

        conn = psycopg2.connect(**self.starting_parameters_db)
        cur = conn.cursor()
        conn.autocommit = True

        try:
            cur.execute(f"DROP DATABASE {self.target_parameters_db['dbname']};")
        except psycopg2.OperationalError as error:
            print(error)
        finally:
            cur.execute(f"CREATE DATABASE {self.target_parameters_db['dbname']};")
            cur.close()
            conn.close()

    @staticmethod
    def run_sql_script(path_to_script: str, parameters_db: dict) -> None:
        """
        Исполняет скрипт создания таблиц в базе данных

        :param path_to_script: путь к файлу скрипта table_script
        :param parameters_db: параметры для подключения к целевой базе данных
        """

        with open(path_to_script, "r", encoding="UTF-8") as file:
            script = file.read()

        with psycopg2.connect(**parameters_db) as conn:
            with conn.cursor() as cur:
                cur.execute(script)

        conn.close()

    def save_to_db(self, table_name: str, data: dict[Entity]) -> None:
        """
        Сохраняет в указанную таблицу данные, полученные из объекта-наследника класса Entity

        :param table_name: имя таблицы, в которую будут сохранены значения
        :param data: словарь с сущностями, информацию о которых следует сохранить в таблицу
        """

        conn = psycopg2.connect(**self.target_parameters_db)
        cur = conn.cursor()

        for item in data.values():
            fields = item.get_fields()
            values = item.get_values()
            cur.execute(self._get_insert_string(table_name, fields), values)

        cur.close()
        conn.commit()
        conn.close()

    @staticmethod
    def _get_insert_string(table_name: str, fields: tuple) -> str:
        """
        Возвращает строку, которая будет использована для операции вставки значений в базу данных

        :param table_name: имя таблицы
        :param fields: названия полей таблицы в формате кортежа
        :return: конечная строка вида "INSERT INTO table_name (field_1, field_2...) VALUES (%s, %s...);"
        """

        field_names = ", ".join(fields)
        fields_number = ", ".join(['%s'] * len(fields))

        return f"""
               INSERT INTO {table_name} ({field_names})
               VALUES ({fields_number});
               """
