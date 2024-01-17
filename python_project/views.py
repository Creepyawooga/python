import datetime
import sqlite3
import requests
import json

from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def clean_vacancy(vacancy):
    vacancy['area'] = vacancy['area'] if vacancy.__contains__('name') else 'Нет данных'
    vacancy['key_skills'] = ', '.join(map(lambda x: x['name'], vacancy['key_skills']))
    if vacancy['salary']['from'] != None and vacancy['salary']['to'] != None and vacancy['salary'][('from')] != \
            vacancy['salary']['to']:
        vacancy[
            'salary'] = f"от {'{0:,}'.format(vacancy['salary']['from']).replace(',', ' ')} до {'{0:,}'.format(vacancy['salary']['to']).replace(',', ' ')} {vacancy['salary']['currency']}"
    elif vacancy['salary']['from'] != None:
        vacancy[
            'salary'] = f"{'{0:,}'.format(vacancy['salary']['from']).replace(',', ' ')} {vacancy['salary']['currency']}"
    elif vacancy['salary']['to'] != None:
        vacancy[
            'salary'] = f"{'{0:,}'.format(vacancy['salary']['to']).replace(',', ' ')} {vacancy['salary']['currency']}"
    else:
        vacancy['salary'] = 'Нет данных'

    return vacancy


def last_vacancies(request):
    try:

        info = requests.get('https://api.hh.ru/vacancies?text=%22аналитик   %22&specialization=1&per_page=100').json()
        data = [{'id': row['id'], 'published_at': row['published_at']} for row in info['items'] if any(x in row['name'].lower() for x in ['analytic', 'аналитик', 'analyst', 'аналітик']) and not row['salary'] is None]
        data = sorted(data, key=lambda x: x['published_at'])
        vacancies = {index: clean_vacancy(requests.get(f'https://api.hh.ru/vacancies/{vacancy["id"]}').json()) for index, vacancy in enumerate(data[len(data) - 10:])}

        return render(request, 'last_vacancies.html',
                      {'vacancies': vacancies.values()})

    except Exception as e:
        print(e)
        print(datetime.datetime.now())
        return HttpResponse(status=500)


def get_demand(request):
    conn = sqlite3.connect("db.sqlite3")
    sql_query = """SELECT *
                        FROM demand_stats;"""
    cursor = conn.cursor()
    cursor.execute(sql_query)
    data = cursor.fetchall()
    conn.close()

    response = [{'year': vac[0], 'total_avg': vac[1], 'total_count': int(vac[2]),
                 'prof_avg': vac[3] if vac[3] != 0.0 else 'Нет данных',
                 'prof_count': int(vac[4]) if vac[4] != 0.0 else 'Нет данных'} for vac in data]

    return render(request, 'demand.html',
                  {'first_parameter': 'Год', 'second_parameter': 'Общая средняя зарплата',
                   'third_parameter': 'Общее количество вакансий', 'fourth_parameter': 'Средняя зарплата аналитика',
                   'fifth_parameter': 'Количество вакансий аналитика', 'data': response})


def get_geography(request):
    conn = sqlite3.connect("db.sqlite3")
    sql_query = """SELECT *
                        FROM geography_prof_average;"""
    cursor = conn.cursor()
    cursor.execute(sql_query)
    geo_average = cursor.fetchall()
    sql_query = """SELECT *
                            FROM geography_prof_count;"""
    cursor.execute(sql_query)
    geo_count = cursor.fetchall()
    conn.close()

    geo_average.sort(key=lambda x: x[1], reverse=True)
    data_average = [{'area': vac[0], 'average': vac[1]} for index, vac in enumerate(geo_average) if index < 10]
    data_count = [{'area': vac[0], 'count': vac[1]} for index, vac in enumerate(geo_count) if index < 10]

    return render(request, 'geography.html',
                  {'first_parameter': 'Город', 'second_parameter': 'Средняя зарплата',
                   'third_parameter': 'Количество вакансий', 'geo_average': data_average, 'geo_count': data_count})


def get_skills(request):
    conn = sqlite3.connect("db.sqlite3")
    sql_query = """SELECT *
                        FROM skills_prof;"""
    cursor = conn.cursor()
    cursor.execute(sql_query)
    skills_count_year = cursor.fetchall()
    conn.close()

    data = [{'year': skill_year[0], 'skills': [{'name': name, 'count': count} for name, count in json.loads(skill_year[1]).items()]} for skill_year in skills_count_year]

    return render(request, 'skills.html',
                  {'first_parameter': 'Ключевой навык', 'second_parameter': 'Частота', 'data': data})
