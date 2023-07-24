from database.db_saver import DB_Saver
from database.db_manager import DB_Manager
from data_storage.data_storage_hh import Data_Storage_HH
from utils import accept_command, run_command


class User_Interface:
    """
    Класс, предоставляющий интерфейс для взаимодействия с пользователем
    """

    # имена таблиц для базы данных
    table_name_employers = "employers"
    table_name_vacancies = "vacancies"

    def __init__(self) -> None:
        """
        Инициализатор объектов класса.
        Создаёт объект для поиска и хранения данных, инициализирует меню.
        """

        self.data_storage_hh = Data_Storage_HH()

        # псевдоним_команды: (описание, команда)
        self.commands = {
            "help":
                ("Показать список доступных команд",
                 self.show_menu),
            "find employers":
                ("Найти и вывести компании по названию",
                 self.data_storage_hh.find_employers),
            "add employers":
                ("Добавить компании в список для поиска вакансий (для добавления используется id компании)",
                 self.data_storage_hh.add_employers),
            "show employers":
                ("Показать список компаний, которые используются при поиске вакансий",
                 self.data_storage_hh.show_employers_info),
            "clear employers":
                ("Очистить список компаний, которые используются при поиске вакансий. "
                 f"\033[31mБудьте осторожны, это также очистит список найденных вакансий!\033[0m",
                 self.data_storage_hh.clear_employers),
            "find vacancies":
                ("Найти вакансии. Если список компаний не пуст, будут найдены вакансии этих компаний",
                 self.data_storage_hh.find_vacancies),
            "show vacancies":
                ("Вывести на экран информацию о найденных вакансиях",
                 self.data_storage_hh.show_vacancies_info),
            "clear vacancies":
                ("Очистить список найденных вакансий",
                 self.data_storage_hh.clear_vacancies),
            "save to db":
                ("Сохранить найденные вакансии в базу данных",
                 self.save_to_db),
            "enter db":
                ("Войти в режим взаимодействия с базой данных",
                 self.enter_db),
            "exit":
                ("Выйти из программы", None)
        }

    # общие команды
    def show_menu(self) -> None:
        """
        Выводит меню для пользователя в читаемом виде.
        """

        print()
        for command, description in self.commands.items():
            print(f"\t\033[32m{command}\033[0m - {description[0]}")

    def __call__(self) -> None:
        """
        Запускает основной скрипт пользовательского интерфейса при вызове объекта класса.
        Готовность принять команду от пользователя сохраняется до ввода команды выхода "exit"
        """

        print("Добрый день! Я помогу вам найти вакансии и организовать их в список.")
        print("Пожалуйста, выберите и введите команду.")
        self.show_menu()

        while True:
            command = accept_command(self.commands)
            if command == "exit":
                print("\nВсего доброго! Заходите ещё!")
                return
            run_command(self.commands, command)

    # команды, связанные с базой данных
    def save_to_db(self) -> None:
        """
        Сохраняет данные в базу данных.
        Для сохранения в базу данных создаётся объект класса DB_Saver,
        который создает базу данных, основные таблицы и заполняет их полученными в ходе поиска данными.
        """

        database = DB_Saver()
        database.save_to_db(self.table_name_employers, self.data_storage_hh.employers)
        database.save_to_db(self.table_name_vacancies, self.data_storage_hh.vacancies)

        print("\nДанные сохранены в базу данных.")

    def enter_db(self) -> None:
        """
        Создаёт объект класса DB_Manager и вызывает его для имитации режима взаимодействия с базой данных.
        При выходе из режима работы с базой данных, предоставляет пользователю основное меню
        """

        db_manager = DB_Manager()
        db_manager()
        self.show_menu()
