--
-- Запросы для выдачи данных из БД
--

--
-- Вывести список всех компаний и количество вакансий у каждой компании
--

SELECT
    e.employer_id,
    e.name,
    open_vacancies,
    COUNT(vacancy_id) AS number_vacancies
FROM employers e
LEFT JOIN vacancies v
    USING(employer_id)
GROUP BY e.employer_id;

--
-- Вывести список всех вакансий с указанием названия компании
--

SELECT
    vacancy_id,
    v.name,
    location,
    currency,
    salary_min,
    salary_max,
    v.url,
    e.name AS employer_name
FROM vacancies v
JOIN employers e
    USING(employer_id);

--
-- Вывести среднюю зарплату по вакансиям
--

SELECT ROUND(AVG((salary_min + salary_max) / 2)) AS avg_salary
FROM vacancies;

--
-- Вывести список всех вакансий, у которых зарплата выше средней по всем вакансиям
--

SELECT *
FROM vacancies
WHERE (salary_min + salary_max) / 2 > (
    SELECT AVG((salary_min + salary_max) / 2)
    FROM vacancies
    );

--
-- Вывести список всех вакансий, в названии которых содержится указанное слово, например 'python'
--

SELECT *
FROM vacancies
WHERE name LIKE '%placeholder%' OR name LIKE '%placeholder%';