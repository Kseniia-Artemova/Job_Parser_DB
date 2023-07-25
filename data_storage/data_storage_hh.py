import requests
import json

from data_storage.data_storage_abc import Data_Storage
from entity.vacancy_hh import Vacancy_HH
from entity.employer_hh import Employer_HH


class Data_Storage_HH(Data_Storage):
    """Класс, описывающий объекты способные искать и хранить данные с сайта https://hh.ru"""

    # основные ссылки, использующиеся для обращения к API сайта
    url_employers = "https://api.hh.ru/employers"
    url_vacancies = "https://api.hh.ru/vacancies"

    # максимальное количество вакансий, которое пользователь может запросить за один раз
    max_vacancies = 500
    # максимальное разрешенное количество страниц для выдачи результатов запроса
    max_page = 100
    # количество результатов поиска на одной странице
    per_page = 50

    def __init__(self) -> None:
        """
        Инициализатор объектов класса, присваивает объекту пустые словари
        для хранения объектов вакансий и нанимателей
        """

        self.vacancies = {}
        self.employers = {}

    def find_employers(self) -> None:
        """Ищет и выводит на экран компании, в названии которых есть введённый пользователем текст"""

        employer_name = input("\nВведите название компании: ").lower().strip()

        print("\nПодождите минутку, ищу подходящие компании...")

        results = self._cyclic_response(self.url_employers, employer_name)
        counter = 0

        for result in results:
            open_vacancies = result.get('open_vacancies')
            if open_vacancies > 0:
                counter += 1
                print(f"\nid: {result.get('id')}"
                      f"\nНазвание: {result.get('name')}"
                      f"\nurl: {result.get('alternate_url')}"
                      f"\nОткрытых вакансий: {open_vacancies}")

        print(f"\nВсего найдено: {len(results)}, с активными вакансиями: {counter}")

    def add_employers(self) -> None:
        """
        Запрашивает у пользователя id нанимателя,
        получает через API сайта информацию об этом нанимателе
        и создаёт объект Employer_HH.
        Созданные объекты добавляются в словарь employers в формате 'id: объект'

        Приём ввода id продолжается до слова "stop"
        """

        new_employers = {}

        while True:
            employer_id = input("\nВведите id компании или наберите 'stop' для выхода:\n")
            if employer_id.lower() == "stop":
                break

            url = self.url_employers + "/" + employer_id
            response = self._get_response(url)

            if "errors" in response or not employer_id:
                print("Такой id не найден.")
                continue

            employer = Employer_HH(
                response.get("id"),
                response.get("name"),
                response.get("alternate_url"),
                response.get("open_vacancies")
            )
            new_employers[employer.employer_id] = employer
            print("Компания успешно добавлена в список.")

        self.employers.update(new_employers)

    def show_employers_info(self) -> None:
        """Выводит на экран информацию о компаниях, которые содержатся в словаре employers"""

        if not self.employers:
            print("\nСписок компаний пуст.")
            return
        print()
        for employer in self.employers.values():
            print(f"{employer}")

    def clear_employers(self) -> None:
        """
        Опустошает словарь employers вместе со словарём vacancies
        (для избежания ошибок при сохранении в базу данных)
        """

        self.vacancies.clear()
        self.employers.clear()
        print("\nСписок компаний очищен.")

    def find_vacancies(self) -> None:
        """
        Находит и добавляет в словарь вакансии тех компаний, которые есть в словаре employers.
        Пользователь может указать ключевое слово и требуемое количество вакансий для поиска

        При указании некорректного числа вакансий для поиска (больше максимального разрешенного или
        нечисловое) устанавливается значение по умолчанию = 50.
        Поиск вакансий при условии пустого словаря employers невозможен
        """

        if not self.employers:
            print("\nСначала укажите компании для поиска командой\033[32m add employers\033[0m.")
            return

        keyword = input("\nВведите название вакансии или ключевое слово для поиска:\n").lower().strip()

        number = input(f"\nВведите требуемое количество вакансий, но не больше {self.max_vacancies}."
                       f"\n\033[033mПри превышении максимального количества вакансий или передаче некорректного значения"
                       f"\nбудет установлено значение по умолчанию (= 50)\033[0m:\n")

        try:
            number = int(number)
        except ValueError:
            number = 50
        else:
            number = number if number in range(self.max_vacancies + 1) else 50

        employers = ["employer_id=" + company for company in self.employers.keys()]
        url = self.url_vacancies + "?" + "&".join(employers)

        print("\nПодождите минутку, ищу подходящие вакансии...")
        results = self._cyclic_response(url, keyword, number)[:number]

        if not results:
            print("Вакансии по такому запросу не найдены.")
            return

        for vacancy in results:
            if vacancy.get("id") not in self.vacancies:
                vacancy_object = Vacancy_HH(vacancy)
                self.vacancies[vacancy.get("id")] = vacancy_object
                print()
                print(vacancy_object.get_info())
        print(f"\nВсего найдено {len(results)} вакансий по такому запросу."
              f"\nРезультаты запроса добавлены в общий список.")

    def show_vacancies_info(self) -> None:
        """Выводит на экран информацию о вакансиях из словаря vacancies"""

        if not self.vacancies:
            print("\nСписок вакансий пуст.")
            return
        for vacancy in self.vacancies.values():
            print()
            print(vacancy.get_info())

    def clear_vacancies(self) -> None:
        """Опустошает словарь вакансий"""

        self.vacancies.clear()
        print("\nСписок вакансий очищен.")

    @staticmethod
    def _get_response(url: str, parameters: None | dict = None) -> list[dict] | dict:
        """
        Отправляет запрос к API сайта, возвращает ответ в виде списка словарей

        :param url: ссылка на ресурс
        :param parameters: параметры запроса
        """

        with requests.get(url, parameters) as request:
            response = request.content.decode("utf-8")
            response = json.loads(response)

        return response

    def _cyclic_response(self, url: str, text: str, number: int | None = None) -> list[dict]:
        """
        Осуществляет циклическую отправку запросов, изменяя номер страницы запроса.
        Завершает цикл, если закончились страницы или число элементов достигло желаемого

        :param url: ссылка на ресурс
        :param text: ключевое слово для поиска
        :param number: искомое количество элементов
        """
        page = 0
        per_page = self.per_page
        parameters = {"text": text, "page": page, "per_page": per_page}
        results = []

        while True:
            response = self._get_response(url, parameters)
            results.extend(response["items"])

            total_pages = response.get("pages")
            parameters["page"] += 1

            if number and len(results) > number:
                break
            elif parameters["page"] >= total_pages:
                break
            elif parameters["page"] >= self.max_page:
                break

        return results
