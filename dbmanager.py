import psycopg2
from config import config


class DBManager:
    def __init__(self):
        params = config()
        self.conn = psycopg2.connect(**params)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()
        self.database_name = 'test'


    def get_companies_and_vacancies_count(self):
        """получает список всех компаний и количество вакансий у каждой компании."""
        with psycopg2.connect(dbname=self.database_name, **config()) as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT employer_name, COUNT(vacancy_id) AS vacancy_count FROM vacancies GROUP BY employer_name""")
                result = cur.fetchall()
        return result


    def get_all_vacancies(self):
        """получает список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию."""
        with psycopg2.connect(dbname=self.database_name, **config()) as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT employer_name, vacancy_name, salary_from, salary_to, url FROM vacancies""")
                result = cur.fetchall()
            return result


    def get_avg_salary(self):
        """получает среднюю зарплату по вакансиям."""
        with psycopg2.connect(dbname=self.database_name, **config()) as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT employer_name, 
                            AVG((salary_from + salary_to) / 2) AS average_salary FROM vacancies 
                            WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL GROUP BY employer_name
                            """)
                result = cur.fetchall()
            return result


    def get_vacancies_with_higher_salary(self):
        """получает список всех вакансий, у которых зарплата выше средней по всем вакансиям."""
        with psycopg2.connect(dbname=self.database_name, **config()) as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT * FROM vacancies 
                               WHERE (salary_from + salary_to) / 2 > (SELECT AVG((salary_from + salary_to) / 2) FROM vacancies)
                            """)
                result = cur.fetchall()
            return result


    def get_vacancies_with_keyword(self, keyword):
        """получает список всех вакансий, в названии которых содержатся переданные в метод слова, например python."""
        with psycopg2.connect(dbname=self.database_name, **config()) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM vacancies WHERE vacancy_name ILIKE %s", ('%' + keyword + '%',))
                result = cur.fetchall()
        return result

    def create_database(self):
        """Удаление и создание базы данных."""
        self.cur.execute(f'DROP DATABASE IF EXISTS {self.database_name}')
        self.cur.execute(f'CREATE DATABASE {self.database_name}')

    def create_tables(self):
        """Создание таблиц companies и vacancies в базе данных"""
        with psycopg2.connect(dbname=self.database_name, **config()) as conn:
            with conn.cursor() as cur:
                cur.execute("""CREATE TABLE companies (
                                    employer_id serial primary key,
                                    employer_name varchar(100) unique,
                                    open_vacancies int,
                                    description text
                                )""")
                cur.execute("""CREATE TABLE vacancies (
                                                vacancy_id serial primary key,
                                                employer_id int,
                                                FOREIGN KEY (employer_id) references companies(employer_id),
                                                employer_name varchar(100) REFERENCES companies(employer_name) NOT NULL,
                                                vacancy_name varchar(100) not null,
                                                url varchar(100),
                                                salary_from int,
                                                salary_to int,
                                                description text
                                            )""")

    def save_info_db(self, employers_info, vacancies_details):
        with psycopg2.connect(dbname=self.database_name, **config()) as conn:
            with conn.cursor() as cur:
                for employer in employers_info:
                    cur.execute(
                        f"INSERT INTO companies(employer_id, employer_name, open_vacancies, description) VALUES"
                        f"('{employer['employer_id']}', '{employer['employer_name']}', "
                        f"'{employer['open_vacancies']}', '{employer['description']}')"
                    )

                for vacancy in vacancies_details:
                    salary_to = vacancy['salary_to'] if vacancy['salary_to'] is not None else 'NULL'
                    salary_from = vacancy['salary_from'] if vacancy['salary_from'] is not None else 'NULL'
                    cur.execute(
                        f"INSERT INTO vacancies(vacancy_id, employer_id, employer_name, vacancy_name, url, salary_from, salary_to, description) VALUES"
                        f"('{vacancy['vacancy_id']}', '{vacancy['employer_id']}',"
                        f"'{vacancy['employer_name']}', '{vacancy['vacancy_name']}',"
                        f"'{vacancy['url']}', {salary_from},"
                        f"{salary_to}, '{vacancy['description']}')"
                    )

        conn.close()