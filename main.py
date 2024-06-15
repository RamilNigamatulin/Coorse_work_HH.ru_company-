from utils import HeadHunterAPI
from dbmanager import DBManager


def main():
    hh_api = HeadHunterAPI()
    db_manager = DBManager()

    db_manager.create_database()
    db_manager.create_tables()
    employers_info = hh_api.get_employers()
    vacancies_details = hh_api.get_vacancies_details()
    db_manager.save_info_db(employers_info, vacancies_details)

    print("Список компаний и количество вакансий в компаниях:")
    elements = db_manager.get_companies_and_vacancies_count()
    for i, element in enumerate(elements, start=1):
        print(f'{i}. {element[0]} - {element[1]};')

    print("Список вакансий, заработная плата и ссылка на вакансию:")
    results = db_manager.get_all_vacancies()
    for i, result in enumerate(results[:], start=1):
        employer_name, vacancy_name, salary_from, salary_to, url = result
        if salary_to is None and salary_from is None:
            print(f'{i}. {employer_name} - {vacancy_name} - Заработная плата не указана - {url};')
        elif salary_to is None:
            print(f'{i}. {employer_name} - {vacancy_name} - Заработная плата от {salary_from} - {url};')
        elif salary_from is None:
            print(f'{i}. {employer_name} - {vacancy_name} - Заработная плата до {salary_to} - {url};')
        else:
            print(f'{i}. {employer_name} - {vacancy_name} - Заработная плата от {salary_from} до {salary_to} - {url};')

    print("Средняя заработная плата по компаниям:")
    results = db_manager.get_avg_salary()
    for i, result in enumerate(results, start=1):
        print(f'{i}. {result[0]} - {int(result[1])}')

    print("Список всех вакансий, у которых заработная плата выше средней: ")
    results = db_manager.get_all_vacancies()
    for i, result in enumerate(results[:], start=1):
        print(f'{i}. {result[1]}')

    user_input = input('Введите необходимые условия поиска: (например "python").\n'
                       'В случае нежелания дальнейшего поиска, введите слово "exit":  ')
    if user_input == 'exit':
        pass
    else:
        results = db_manager.get_vacancies_with_keyword(user_input)
        for i, result in enumerate(results[:], start=1):
            print(f'{i}. {result};')


if __name__ == '__main__':
    main()