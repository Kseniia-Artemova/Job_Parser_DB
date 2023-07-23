import psycopg2
import os

from utils import config
from entity.entity_abc import Entity


class DB_Creator:

    db_name = "my_vacancies"
    table_script = "tables_creation.sql"
    configuration_db = "database_config.ini"
    current_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(current_dir)

    path_to_config = os.path.join(project_root, current_dir, configuration_db)
    path_to_table_script = os.path.join(project_root, current_dir, table_script)

    def __init__(self):
        self.parameters_db = config(self.path_to_config)
        self._create_db()
        self.parameters_db["dbname"] = self.db_name
        self.run_sql_script(self.path_to_table_script, self.parameters_db)

    def _create_db(self):
        conn = psycopg2.connect(**self.parameters_db)
        cur = conn.cursor()
        conn.autocommit = True

        try:
            cur.execute(f"DROP DATABASE {self.db_name};")
        except psycopg2.errors.InvalidCatalogName:
            pass
        finally:
            cur.execute(f"CREATE DATABASE {self.db_name};")
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

        conn = psycopg2.connect(**self.parameters_db)
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
               VALUES ({fields_number})
               RETURNING *;
               """
