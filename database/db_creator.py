import psycopg2
import os

from utils import config
from entity.entity_abc import Entity


class DB_Creator:

    table_script = "tables_creation.sql"
    starting_db = "db_config_starting.ini"
    target_db = "db_config_target.ini"

    def __init__(self):

        self.path_to_starting_config = self._build_path_to_file(self.starting_db)
        self.path_to_target_config = self._build_path_to_file(self.target_db)
        self.path_to_table_script = self._build_path_to_file(self.table_script)

        self.starting_parameters_db = config(self.path_to_starting_config)
        self.target_parameters_db = config(self.path_to_target_config)

        self._create_db()
        self.run_sql_script(self.path_to_table_script, self.target_parameters_db)

    @staticmethod
    def _build_path_to_file(file_name):
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        return os.path.join(project_root, current_dir, file_name)

    def _create_db(self):
        conn = psycopg2.connect(**self.starting_parameters_db)
        cur = conn.cursor()
        conn.autocommit = True

        try:
            cur.execute(f"DROP DATABASE {self.target_parameters_db['dbname']};")
        except psycopg2.errors.InvalidCatalogName:
            pass
        finally:
            cur.execute(f"CREATE DATABASE {self.target_parameters_db['dbname']};")
            cur.close()
            conn.close()

    @staticmethod
    def run_sql_script(path_to_script, parameters_db):
        with open(path_to_script, "r", encoding="UTF-8") as file:
            script = file.read()

        with psycopg2.connect(**parameters_db) as conn:
            with conn.cursor() as cur:
                cur.execute(script)

        conn.close()

    def save_to_db(self, table_name, data: dict[Entity]):

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
    def _get_insert_string(table_name, fields):

        field_names = ", ".join(fields)
        fields_number = ", ".join(['%s'] * len(fields))

        return f"""
               INSERT INTO {table_name} ({field_names})
               VALUES ({fields_number});
               """
