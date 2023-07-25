--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: employers; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE IF NOT EXISTS employers (
    employer_id int,
    name varchar(200) NOT NULL,
    url varchar(50) NOT NULL,
    open_vacancies int,

    CONSTRAINT pk_employers_employer_id PRIMARY KEY(employer_id)
);

--
-- Name: vacancies; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE IF NOT EXISTS vacancies (
    vacancy_id int,
    name varchar(200) NOT NULL,
    location varchar(50) NOT NULL,
    currency varchar(3),
    salary_min int,
    salary_max int,
    url varchar(50) NOT NULL,
    employer_id int,

    CONSTRAINT pk_vacancies_vacancy_id PRIMARY KEY(vacancy_id),
    CONSTRAINT fk_vacancies_employer_id FOREIGN KEY(employer_id) REFERENCES employers(employer_id)
);

