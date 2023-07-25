from abc import ABC, abstractmethod
from configparser import ConfigParser
import os


class DB_Interaction(ABC):
    """
    Абстрактный класс для описания объектов, подключающихся к базе данных
    и взаимодействующих с ней
    """

    # при инициализации объектов классов-наследников
    # должно устанавливаться соединение с именем conn (self.conn)
    conn = None

    @staticmethod
    def _build_path_to_file(file_name: str) -> str:
        """
        Строит путь к указанному файлу, при условии что он находится в той же директории,
        что и файл класса
        """

        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        return os.path.join(project_root, current_dir, file_name)

    @staticmethod
    def _read_script(path_to_script: str) -> str:
        """
        Читает файл SQL-скрипта и возвращает прочитанный файл в виде строки

        :param path_to_script: путь к SQL-скрипту
        """

        with open(path_to_script, "r", encoding="UTF-8") as file:
            script = file.read()
        return script

    def _run_script(self, path_to_script: str) -> None:
        """
        Исполняет переданный в метод SQL-скрипт

        :param path_to_script: путь к SQL-скрипту
        """

        script = self._read_script(path_to_script)

        cur = self.conn.cursor()
        cur.execute(script)
        cur.close()
        self.conn.commit()

    def __del__(self) -> None:
        """Метод, предписывающий закрыть соединение с базой данных при удалении объекта"""

        if hasattr(self, 'conn') and self.conn is not None:
            self.conn.close()

    @abstractmethod
    def make_connection(self) -> None:
        """Устанавливает соединение с базой данных"""
        pass

    @abstractmethod
    def close_connection_db(self) -> None:
        """Закрывает соединение с базой данных"""
        pass

    @staticmethod
    def config(path_to_file: str, section: str = "postgresql") -> dict[str]:
        """
        Функция считывает информацию о базе данных из конфигурационного файла
        в формате .ini и возвращает её в виде словаря

        :param path_to_file: путь к конфигурационному файлу с расширением .ini
        :param section: указание на раздел (или "секцию"), который нужно прочитать в конфигурационном файле

        :return: словарь с параметрами базы данных
        """

        # create a parser
        parser = ConfigParser()
        # read config file
        parser.read(path_to_file)
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception(
                'Section {0} is not found in the {1} file.'.format(section, path_to_file))
        return db
