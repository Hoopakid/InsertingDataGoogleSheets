import os
from Bitrix.formatting import format_bitrix_data
from celery import Celery
from celery.schedules import crontab

from setup import GoogleSheetsManager, CallData
from dotenv import load_dotenv

load_dotenv()

app = Celery(
    'manage',
    broker='redis://redis_sheet:6379/0',
    backend='redis://redis_sheet:6379/0'
)

app.conf.beat_schedule = {
    'add_every_night': {
        'task': 'manage.add_every_night',
        'schedule': crontab(hour=20, minute=0)
    }
}

SHEET_URL = os.environ.get('SHEET_URL')

google_obj = GoogleSheetsManager(
    credentials_file='credentials.json',
    sheet_url=SHEET_URL
)


@app.task()
def add_every_night():
    bitrix_datas = format_bitrix_data()
    for data in bitrix_datas:
        call_data = CallData(
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
        google_obj.append_row(call_data.format_data(len(google_obj.get_sheet_data()) + 1))
