import psycopg2
from configuration.config import config


class DBManager:
    def __init__(self):
        params = config()
        self.conn = psycopg2.connect(**params)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()
        self.database_name = 'test'

    def get_companies_and_vacancies_count(self):
        """
        Получает список всех компаний и количество вакансий у каждой компании.
        """
        with psycopg2.connect(dbname=self.database_name, **config()) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT employer_name,
                    COUNT(vacancy_id) AS vacancy_count
                    FROM vacancies
                    GROUP BY employer_name
                """)
                result = cur.fetchall()
        return result

    def get_all_vacancies(self):
        """
        Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию.
        """
        with psycopg2.connect(dbname=self.database_name, **config()) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT employer_name,
                    vacancy_name,
                    salary_from,
                    salary_to,
                    url
                    FROM vacancies
                """)
                result = cur.fetchall()
            return result

    def get_avg_salary(self):
        """Получает среднюю зарплату по вакансиям."""
        with psycopg2.connect(dbname=self.database_name, **config()) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT employer_name,
                    AVG((salary_from + salary_to) / 2) AS average_salary
                    FROM vacancies
                    WHERE salary_from IS NOT NULL
                    AND salary_to IS NOT NULL
                    GROUP BY employer_name
                """)
                result = cur.fetchall()
            return result

    def get_vacancies_with_higher_salary(self):
        """Получает список всех вакансий,
        у которых зарплата выше средней по всем вакансиям."""
        with psycopg2.connect(dbname=self.database_name, **config()) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM vacancies
                    WHERE (salary_from + salary_to) / 2 > (
                    SELECT AVG((salary_from + salary_to) / 2)
                    FROM vacancies)
                """)
                result = cur.fetchall()
            return result

    def get_vacancies_with_keyword(self, keyword):
        """Получает список всех вакансий,
        в названии которых содержатся переданные в метод слова."""
        with psycopg2.connect(dbname=self.database_name, **config()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM vacancies"
                    " WHERE vacancy_name ILIKE %s", ('%' + keyword + '%',))
                result = cur.fetchall()
        return result

    def create_database(self):
        """Удаляет и создает базу данных."""
        self.cur.execute(f'DROP DATABASE IF EXISTS {self.database_name}')
        self.cur.execute(f'CREATE DATABASE {self.database_name}')

    def create_tables(self):
        """Создает таблицы 'companies' и 'vacancies' в базе данных."""
        with psycopg2.connect(dbname=self.database_name, **config()) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE companies (
                        employer_id serial primary key,
                        employer_name varchar(100) unique,
                        open_vacancies int,
                        description text
                    )
                """)
                cur.execute("""
                    CREATE TABLE vacancies (
                        vacancy_id serial primary key,
                        employer_id int,
                        FOREIGN KEY (employer_id)
                        references companies(employer_id),
                        employer_name varchar(100)
                        REFERENCES companies(employer_name) NOT NULL,
                        vacancy_name varchar(100) not null,
                        url varchar(100),
                        salary_from int,
                        salary_to int,
                        description text
                    )
                """)

    def save_info_db(self, employers_info, vacancies_details):
        with psycopg2.connect(dbname=self.database_name, **config()) as conn:
            with conn.cursor() as cur:
                for employer in employers_info:
                    cur.execute(
                        "INSERT INTO companies("
                        "employer_id, "
                        "employer_name, "
                        "open_vacancies, "
                        "description"
                        ") "
                        "VALUES (%s, %s, %s, %s)",
                        (employer['employer_id'],
                         employer['employer_name'],
                         employer['open_vacancies'],
                         employer['description'])
                    )

                for vacancy in vacancies_details:
                    cur.execute(
                        "INSERT INTO vacancies("
                        "vacancy_id, employer_id,"
                        "employer_name,"
                        "vacancy_name,"
                        "url,"
                        "salary_from,"
                        "salary_to,"
                        "description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (vacancy['vacancy_id'],
                         vacancy['employer_id'],
                         vacancy['employer_name'],
                         vacancy['vacancy_name'],
                         vacancy['url'],
                         vacancy['salary_from'],
                         vacancy['salary_to'],
                         vacancy['description'])
                    )
