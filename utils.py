import requests

class HeadHunterAPI():
    """Класс для работы с API HeadHunter."""
    def __init__(self):
        self.url = 'https://api.hh.ru/'
        self.headers = {'User-Agent': 'HH-User-Agent'}
        self.employers = [
            'ДубльГИС       ',
            'QIWI',
            'СберМаркет',
            'КРОК',
            'Skyeng',
            'ЦИАН',
            'Skillbox',
            'OCS Distribution',
            'IT_One',
            'СберЗдоровье'
        ]

    def get_employers(self):
        """Получение информации о работодателях"""
        employers_info = []
        for employer_name in self.employers:
            params = {'text': employer_name, 'sort_by': 'by_name', 'page': 0, 'per_page': 1}

            try:
                response = requests.get(f"{self.url}employers", headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                if data['found'] > 0:
                    employer_id = data['items'][0]['id']
                    employer_name = data['items'][0]['name']
                    open_vacancies = data['items'][0]['open_vacancies']

                    # Получаем полную информацию о работодателе
                    employer_response = requests.get(f"{self.url}employers/{employer_id}", headers=self.headers)
                    employer_response.raise_for_status()
                    employer_data = employer_response.json()
                    description = employer_data.get('description', 'Нет описания')

                    employer_info = {
                            'employer_id': employer_id,
                            'employer_name': employer_name,
                            'open_vacancies': open_vacancies,
                            'description': description
                    }
                    employers_info.append(employer_info)
                else:
                    print(f"Работодатель с именем: {employer_name} не найден")
            except requests.RequestException as e:
                print(f"Не удалось получить полную информацию для работодателя: {employer_name}. Ошибка: {e}")
        return employers_info

    def get_vacancies(self, employer_id):
        """Получение списка вакансий для конкретного работодателя"""
        params = {
            "employer_id": employer_id,
            "only_with_salary": True,
            "name": "Россия",
            # "area": 113,
            "area_id": "Калининград",
            "only_with_vacancies": True,
            "per_page": 100,
            "page": 0
        }

        try:
            response = requests.get(f"{self.url}vacancies", headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()['items']
        except requests.RequestException as e:
            print(f"Не удалось получить полную информацию для работодателя: {employer_id}. Ошибка: {e}")
        return []

    def get_vacancies_details(self):
        """Получение деталей по всем вакансиям всех работодателей"""
        employers = self.get_employers()
        vacancies_list = []
        for employer in employers:
            employer_id = employer['employer_id']
            employer_name = employer['employer_name']
            vacancies = self.get_vacancies(employer_id)
            for vacancy in vacancies:
                vacancy_details = {
                    'employer_id': employer_id,
                    'employer_name': employer_name,
                    'vacancy_id': vacancy['id'],
                    'vacancy_name': vacancy['name'],
                    'url': vacancy['alternate_url'],
                    'salary_from': vacancy['salary']['from'],
                    'salary_to': vacancy['salary']['to'],
                    'area': vacancy['area']['name'],
                    'description': vacancy.get('snippet', {}).get('responsibility', 'Описание отсутствует')
                }
                vacancies_list.append(vacancy_details)
        return vacancies_list