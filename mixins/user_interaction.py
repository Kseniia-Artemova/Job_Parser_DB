from typing import Any


class User_Interaction_Mixin:
    """
    Класс-миксин для добавления методов взаимодействия с пользователем

    В основном классе обязательно должен быть словарь меню с именем self.commands,
    данные должны быть представлены в виде:
    "command": ("description", method/function)
    """

    text_color = "\033[0m"

    def show_menu(self) -> None:
        """
        Выводит меню для пользователя в читаемом виде
        """

        print()
        for command, description in self.commands.items():
            print(f"\t{self.text_color}{command}\033[0m - {description[0]}")

    def accept_command(self) -> str:
        """
        Спрашивает у пользователя команду и возвращает её.
        В случае отсутствия команды в словаре, просит повторить ввод

        :return: команда, полученная от пользователя
        """

        while True:
            command = input("\nКоманда: ").lower().strip()
            if command not in self.commands:
                print("Такая команда не существует. Попробуйте ещё раз.")
                continue

            return command

    def run_command(self, command: str, *args: Any, **kwargs: Any) -> Any:
        """
        Ищет в словаре меню переданную команду и исполняет функцию, которая с ней связана

        :param command: команда, введённая пользователем
        :param args: любые позиционные аргументы
        :param kwargs: любые именованные аргументы
        """

        return self.commands[command][1](*args, **kwargs)