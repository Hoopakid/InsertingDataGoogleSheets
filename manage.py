import os
import requests
import logging
from celery import Celery
from celery.schedules import crontab

from setup import GoogleSheetsManager, CallData
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = Celery(
    'manage',
    broker='redis://redis_sheet:6379/0',
    backend='redis://redis_sheet:6379/0'
)

app.conf.beat_schedule = {
    'add_margarit': {
        'task': 'manage.add_margarit',
        'schedule': crontab(hour=2, minute=0)
    },
    'add_bulut': {
        'task': 'manage.add_bulut',
        'schedule': crontab(hour=1, minute=0)
    },
    'add_bulut1': {
        'task': 'manage.add_bulut1',
        'schedule': crontab(hour=3, minute=0)
    },
    'add_salesdoctor': {
        'task': 'manage.add_salesdoctor',
        'schedule': crontab(hour=20, minute=0)
    }
}

SHEET_URL = os.environ.get('SHEET_URL')
API_URL = os.environ.get('API_URL')
SALESDOCTOR_SHEET_URL = os.environ.get('SALESDOCTOR_SHEET_URL')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
USER_CHAT_ID = os.environ.get('USER_CHAT_ID')


def get_obj_sheet(worksheet_name):
    return GoogleSheetsManager(
        credentials_file='credentials.json',
        sheet_url=SHEET_URL,
        worksheet_name=worksheet_name
    )


@app.task()
def add_margarit():
    bulut_margarit_akb_url = f'{API_URL}/get-akb-data'
    r = requests.get(bulut_margarit_akb_url)
    logging.info('Data fetched')
    margarit_google_obj = get_obj_sheet('Margaritto Yangi akab')
    if r.json()['status'] == 200:
        margarit_data = r.json()['data']['Margarit']
        for data in margarit_data:
            temp = []
            for key, val in data.items():
                temp.append(val)
            margarit_google_obj.append_row(temp)
        logging.info('Margarit data added')
        url = f'https://api.telegram.org/bot{BOT_TOKEN}'
        requests.post(url + '/sendMessage',
                      data={'chat_id': USER_CHAT_ID, 'text': 'Margaritto data added to Google Sheets'})
        return True
    return False


@app.task()
def add_bulut():
    bulut_margarit_akb_url = f'{API_URL}/get-akb-data'
    r = requests.get(bulut_margarit_akb_url)
    logging.info('Data fetched')
    bulut_google_obj = get_obj_sheet('Bulut Yangi AKB')
    if r.status_code == 200:
        bulut_data = r.json()['data']['Bulut']
        for data in bulut_data:
            temp = []
            for key, val in data.items():
                temp.append(val)
            bulut_google_obj.append_row(temp)
        logging.info('Bulut data added')
        url = f'https://api.telegram.org/bot{BOT_TOKEN}'
        requests.post(url + '/sendMessage',
                      data={'chat_id': USER_CHAT_ID, 'text': 'Bulut data added to Google Sheets'})
        return True
    return False


@app.task()
def add_bulut1():
    bulut_margarit_akb_url = f'{API_URL}/get-all-data'
    r = requests.get(bulut_margarit_akb_url)
    logging.info('Data fetched')
    google_obj = get_obj_sheet('Bulut/Margaritto')
    if r.status_code == 200:
        datas = r.json()
        for data in datas:
            temp = []
            for key, val in data.items():
                temp.append(val)
            google_obj.append_row(temp)
        logging.info('Bulut data added')
        url = f'https://api.telegram.org/bot{BOT_TOKEN}'
        requests.post(url + '/sendMessage',
                      data={'chat_id': USER_CHAT_ID, 'text': 'Bulut/Margaritto data added to Google Sheets'})
        return True
    return False


@app.task()
def add_salesdoctor():
    salesdoctor_url = f'{API_URL}/data-google-sheet'
    response = requests.get(salesdoctor_url)
    logging.info('Data fetched')
    sheet_obj = GoogleSheetsManager(
        credentials_file='credentials.json',
        sheet_url=SALESDOCTOR_SHEET_URL,
        worksheet_name='Baza'
    )
    if response.status_code == 200:
        datas = response.json()
        for data in datas['data']:
            obj_call = CallData(
                date_str=data['date'],
                employee=data['seller'],
                phone_number=data['client_phone_number'],
                client=data['client'],
                call_status=data['direction'],
                answered=data['answered'],
                call_duration=data['duration'],
                dialing=data['dialing'],
                source='Номер не указан'
            )
            sheet_obj.append_row(obj_call.format_data(len(sheet_obj.get_sheet_data()) + 1))
        logging.info("Google sheet objects added")
        url = f'https://api.telegram.org/bot{BOT_TOKEN}'
        requests.post(url + '/sendMessage',
                      data={'chat_id': USER_CHAT_ID, 'text': 'SalesDoctor data added to Google Sheets'})
        return True
    return False
