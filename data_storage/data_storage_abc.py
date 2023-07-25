from abc import ABC, abstractmethod


class Data_Storage(ABC):
    """Класс, описывающий объекты способные искать и хранить данные с сайта"""

    # максимальное количество вакансий, которое пользователь может запросить за один раз
    max_vacancies = None

    @abstractmethod
    def find_employers(self) -> None:
        """Ищет и выводит на экран компании, в названии которых есть введённый пользователем текст"""
        pass

    @abstractmethod
    def add_employers(self) -> None:
        """
        Запрашивает у пользователя id нанимателя,
        получает через API сайта информацию об этом нанимателе
        и создаёт объект Employer.
        Созданные объекты добавляются в словарь employers в формате 'id: объект'
        """
        pass

    @abstractmethod
    def show_employers_info(self) -> None:
        """Выводит на экран информацию о компаниях, которые содержатся в словаре объекта этого класса"""
        pass

    @abstractmethod
    def clear_employers(self) -> None:
        """
        Опустошает словарь компаний вместе со словарём вакансий
        (для избежания ошибок при сохранении в базу данных)
        """
        pass

    @abstractmethod
    def find_vacancies(self) -> None:
        """
        Находит и добавляет в словарь вакансии тех компаний, которые есть в словаре компаний

        При указании некорректного числа вакансий для поиска (больше максимального разрешенного или
        нечисловое) устанавливается значение по умолчанию.
        Поиск вакансий при условии пустого словаря компаний невозможен
        """
        pass

    @abstractmethod
    def show_vacancies_info(self) -> None:
        """Выводит на экран информацию о вакансиях из словаря вакансий"""
        pass

    @abstractmethod
    def clear_vacancies(self) -> None:
        """Опустошает словарь вакансий"""
        pass

    @staticmethod
    @abstractmethod
    def _get_response(url: str, parameters: None | dict = None):
        """
        Отправляет запрос к API сайта, возвращает ответ

        :param url: ссылка на ресурс
        :param parameters: параметры запроса
        """
        pass

    @abstractmethod
    def _cyclic_response(self, url: str, text: str, number: int | None = None):
        """
        Осуществляет циклическую отправку запросов, изменяя номер страницы запроса.
        Завершает цикл, если закончились страницы или число элементов достигло желаемого

        :param url: ссылка на ресурс
        :param text: ключевое слово для поиска
        :param number: искомое количество элементов
        """
        pass
