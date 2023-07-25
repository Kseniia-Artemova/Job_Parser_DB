import psycopg2

from entity.entity_abc import Entity
from database.db_interaction_abc import DB_Interaction


class DB_Saver(DB_Interaction):
    """
    Класс, позволяющий сохранять переданную информацию в базу данных
    """

    # названия ключевых файлов, использующихся для подключения,
    # создания, наполнения или удаления базы данных и таблиц
    table_creation_script = "tables_creation.sql"
    table_remove_script = "tables_remove.sql"
    starting_db = "db_config_starting.ini"
    target_db = "db_config_target.ini"

    def __init__(self) -> None:
        """
        Инициализатор объектов класса.

        Строит пути к конфигурационным файлам и sql-скриптам;
        Создаёт базу данных;
        Создаёт необходимые таблицы, прописанные в файле скрипта
        table_creation_script, если они не существуют
        """

        self.path_to_starting_config = self._build_path_to_file(self.starting_db)
        self.path_to_target_config = self._build_path_to_file(self.target_db)
        self.path_to_table_creation_script = self._build_path_to_file(self.table_creation_script)
        self.path_to_table_remove_script = self._build_path_to_file(self.table_remove_script)

        self.starting_parameters_db = self.config(self.path_to_starting_config)
        self.target_parameters_db = self.config(self.path_to_target_config)

        self._create_db()

        self.conn = None
        self.make_connection()
        self._create_tables()

    def save_to_db(self, table_name: str, data: dict[Entity]) -> None:
        """
        Сохраняет в указанную таблицу данные, полученные из объекта-наследника класса Entity

        :param table_name: имя таблицы, в которую будут сохранены значения
        :param data: словарь с сущностями, информацию о которых следует сохранить в таблицу
        """

        cur = self.conn.cursor()

        for item in data.values():
            fields = item.get_fields()
            values = item.get_values()
            cur.execute(self._get_insert_string(table_name, fields), values)

        cur.close()
        self.conn.commit()

    def clear_db(self) -> None:
        """Удаляет все значения из таблиц базы данных"""

        self._run_script(self.path_to_table_remove_script)

    def make_connection(self) -> None:
        """Устанавливает соединение с базой данных"""

        setattr(self, "conn", psycopg2.connect(**self.target_parameters_db))

    def close_connection_db(self) -> None:
        """Закрывает соединение с базой данных"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def _create_db(self) -> None:
        """
        Создаёт базу данных с именем, указанным в конфигурационном файле target_db,
        если она не существует

        Здесь своё отдельное подключение к базе данных, так как используются
        параметры стартовой базы данных, а не целевой
        """

        conn = psycopg2.connect(**self.starting_parameters_db)
        cur = conn.cursor()
        conn.autocommit = True

        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{self.target_parameters_db['dbname']}'")
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {self.target_parameters_db['dbname']}")

        cur.close()
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
        updated_values = ", ".join([f"{field} = EXCLUDED.{field}" for field in fields])

        return f"""
               INSERT INTO {table_name} ({field_names})
               VALUES ({fields_number})
               ON CONFLICT ({fields[0]}) 
               DO UPDATE SET {updated_values};
               """

    def _create_tables(self) -> None:
        """
        Исполняет скрипт создания таблиц в базе данных
        """

        self._run_script(self.path_to_table_creation_script)
