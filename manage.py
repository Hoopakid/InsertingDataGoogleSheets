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
        'schedule': crontab(hour=20, minute=0)
    },
    'add_bulut': {
        'task': 'manage.add_bulut',
        'schedule': crontab(hour=22, minute=0)
    }
}

SHEET_URL = os.environ.get('SHEET_URL')
API_URL = os.environ.get('API_URL')

margarit_google_obj = GoogleSheetsManager(
    credentials_file='credentials.json',
    sheet_url=SHEET_URL,
    worksheet_name='Margaritto Yangi akab'
)

bulut_google_obj = GoogleSheetsManager(
    credentials_file='credentials.json',
    sheet_url=SHEET_URL,
    worksheet_name='Bulut Yangi AKB'
)


@app.task()
def add_margarit():
    bulut_margarit_akb_url = f'{API_URL}/get-akb-data'
    r = requests.get(bulut_margarit_akb_url)
    logging.info('Data fetched')
    if r.json()['status'] == 200:
        margarit_data = r.json()['data']['Margarit']
        for data in margarit_data:
            temp = []
            for key, val in data.items():
                temp.append(val)
            margarit_google_obj.append_row(temp)
        logging.info('Margarit data added')


@app.task()
def add_bulut():
    bulut_margarit_akb_url = f'{API_URL}/get-akb-data'
    r = requests.get(bulut_margarit_akb_url)
    logging.info('Data fetched')
    if r.json()['status'] == 200:
        bulut_data = r.json()['data']['Bulut']
        for data in bulut_data:
            temp = []
            for key, val in data.items():
                temp.append(val)
            bulut_google_obj.append_row(temp)
        logging.info('Bulut data added')
