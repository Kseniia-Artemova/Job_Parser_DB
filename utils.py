from configparser import ConfigParser
from typing import Any


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


def accept_command(commands: dict[str: tuple]) -> str:
    """
    Спрашивает у пользователя команду и возвращает её.
    В случае отсутствия команды в словаре, просит повторить ввод.

    :param commands: словарь с существующими командами меню

    :return: команда, полученная от пользователя
    """

    while True:
        command = input("\nКоманда: ").lower().strip()
        if command not in commands:
            print("Такая команда не существует. Попробуйте ещё раз.")
            continue

        return command


def run_command(commands: dict[str: tuple], command: str, *args: Any, **kwargs: Any) -> None:
    """
    Ищет в словаре меню переданную команду и исполняет функцию, которая с ней связана

    :param commands: словарь, содержащий команды меню, описание и функции, связанные с командами
    :param command: команда, введённая пользователем
    :param args: любые позиционные аргументы
    :param kwargs: любые именованные аргументы
    """

    commands[command][1](*args, **kwargs)