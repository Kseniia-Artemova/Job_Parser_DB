import psycopg2

from database.db_creator import DB_Creator
from request.request_hh import Request_HH


class User_Interface:

    table_name_employers = "employers"
    table_name_vacancies = "vacancies"

    def __init__(self):

        self.request_hh = Request_HH()

        # псевдоним_команды: (описание, команда)
        self.commands = {
            "help":
                ("Показать список доступных команд",
                 self.show_menu),
            "find employers":
                ("Найти и вывести компании по названию",
                 self.request_hh.find_employers),
            "add employers":
                ("Добавить компании в список для поиска вакансий (для добавления используется id компании)",
                 self.request_hh.add_employers),
            "show employers":
                ("Показать список компаний, которые используются при поиске вакансий",
                 self.request_hh.show_employers_info),
            "clear employers":
                ("Очистить список компаний, которые используются при поиске вакансий. "
                 f"\033[31mБудьте осторожны, это также очистит список найденных вакансий!\033[0m",
                 self.request_hh.clear_employers),
            "find vacancies":
                ("Найти вакансии. Если список компаний не пуст, будут найдены вакансии этих компаний",
                 self.request_hh.find_vacancies),
            "show vacancies":
                ("Вывести на экран информацию о найденных вакансиях",
                 self.request_hh.show_vacancies_info),
            "clear vacancies":
                ("Очистить список найденных вакансий",
                 self.request_hh.clear_vacancies),
            "save to db":
                ("Сохранить найденные вакансии в базу данных",
                 self.save_to_db),
            "enter db":
                ("Войти в режим взаимодействия с базой данных",
                 self.enter_db),
            "exit":
                ("Выйти из программы",
                 self.exit)
        }

    # общие команды
    def show_menu(self):
        print()
        for command, description in self.commands.items():
            print(f"\t\033[32m{command}\033[0m - {description[0]}")

    def __call__(self):
        print("Добрый день! Я помогу вам найти вакансии и организовать их в список.")
        print("Пожалуйста, выберите и введите команду.")
        self.show_menu()

        while True:
            command = self._accept_command()
            self._run_command(command)

    @staticmethod
    def exit():
        print("\nВсего доброго! Заходите ещё!")
        quit()

    # команды, связанные с базой данных
    def save_to_db(self):
        database = DB_Creator()
        database.save_to_db(self.table_name_employers, self.request_hh.employers)
        database.save_to_db(self.table_name_vacancies, self.request_hh.vacancies)

        print("\nДанные сохранены в базу данных.")

    def enter_db(self):
        pass

    # вспомогательные
    def _accept_command(self):
        while True:
            command = input("\nКоманда: ").lower().strip()
            if command not in self.commands:
                print("Такая команда не существует. Попробуйте ещё раз.")
                continue

            return command

    def _run_command(self, command):
        self.commands[command][1]()
