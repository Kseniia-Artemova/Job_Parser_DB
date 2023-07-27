from database.db_saver import DB_Saver
from database.db_manager import DB_Manager
from data_storage.data_storage_hh import Data_Storage_HH
from mixins.user_interaction import User_Interaction_Mixin
from utils import basic_logger


class User_Interface(User_Interaction_Mixin):
    """
    Класс, предоставляющий интерфейс для взаимодействия с пользователем
    """

    # имена таблиц для базы данных
    table_name_employers = "employers"
    table_name_vacancies = "vacancies"

    # цвет текста меню
    text_color = "\033[32m"

    def __init__(self) -> None:
        """
        Инициализатор объектов класса.

        Создаёт объект для поиска и хранения данных;
        Создаёт объект для сохранения значений в базу данных;
        Инициализирует меню
        """

        self.data_storage_hh = Data_Storage_HH()
        self.database = DB_Saver()

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
                ("Очистить список компаний, которые используются при поиске вакансий"
                 f"\n\t{' ' * 18}\033[31mБудьте осторожны, это также очистит список найденных вакансий!\033[0m",
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
                ("Сохранить найденные вакансии и компании в базу данных",
                 self.save_to_db),
            "clear db":
                ("Очистить существующие таблицы в базе данных",
                 self.clear_db),
            "enter db":
                ("Войти в режим взаимодействия с базой данных",
                 self.enter_db),
            "exit":
                ("Выйти из программы", None)
        }

    def __call__(self) -> None:
        """
        Запускает основной скрипт пользовательского интерфейса при вызове объекта класса.
        Готовность принять команду от пользователя сохраняется до ввода команды выхода "exit"
        """

        print("Добрый день! Я помогу вам найти вакансии и организовать их в список.")
        print("Пожалуйста, выберите и введите команду.")
        self.show_menu()

        while True:
            command = self.accept_command()
            if command == "exit":
                print("\nВсего доброго! Заходите ещё!")
                return
            self.run_command(command)

    # команды, связанные с базой данных
    def save_to_db(self) -> None:
        """
        Сохраняет найденные вакансии и компании в базу данных
        """

        self.database.save_to_db(self.table_name_employers, self.data_storage_hh.employers)
        self.database.save_to_db(self.table_name_vacancies, self.data_storage_hh.vacancies)

        print("\nДанные сохранены в базу данных.")

    def clear_db(self) -> None:
        """Удаляет все значения из таблиц базы данных"""

        self.database.clear_db()
        print("\nВсе значения были удалены из таблиц.")

    def enter_db(self) -> None:
        """
        Создаёт объект класса DB_Manager и вызывает его для имитации режима взаимодействия с базой данных.
        При выходе из режима работы с базой данных, предоставляет пользователю основное меню

        Закрывает открытое соединение объекта класса DB_Saver, чтобы дать объекту класса DB_Manager
        установить своё собственное соединение.
        При выходе из режима взаимодействия с базой данных соединение DB_Manager закрывается,
        а соединение DB_Saver возобновляется

        Результаты, полученные при запросах одной сессии режима взаимодействия с базой данных
        записываются в файл лога (logs/query_log.log)
        """

        self.database.close_connection_db()

        db_manager = DB_Manager()

        # сюда записываются результаты запросов одной сессии режима работы с базой данных
        results = db_manager()

        db_manager.close_connection_db()
        basic_logger(results)

        self.show_menu()
        self.database.make_connection()
