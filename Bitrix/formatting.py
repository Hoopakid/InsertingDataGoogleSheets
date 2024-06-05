from pprint import pprint
from datetime import datetime, timedelta

from Bitrix.datum import get_calls_fast


def format_duration_by_seconds(seconds: int):
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    seconds = td.seconds % 60
    return f"{hours:01d}", f"{minutes:02d}", f"{seconds:02d}"


def format_bitrix_data():
    bitrix_datas = get_calls_fast()
    ctx = []
    for data in bitrix_datas:
        # calculate dialing and call duration
        start_time = datetime.fromisoformat(data['START_TIME'])
        end_time = datetime.fromisoformat(data['END_TIME'])
        created = datetime.fromisoformat(data['CREATED'])
        dialing = (start_time - created).seconds
        duration = (end_time - start_time).seconds
        hour, minute, second = format_duration_by_seconds(duration)
        duration_str = f"{hour}:{minute}:{second}"

        # format data
        created_date_str = created.strftime('%d.%m.%Y %H:%M:%S')

        # client, his/her number and seller
        client = list(data['responsible_user'])[0]
        client_number = list(data['responsible_user_phone'])[0]
        phone_number = client_number
        if not phone_number.startswith('+998') and not phone_number.startswith('998'):
            phone_number = f'+998{phone_number}'
        if not phone_number.startswith('+'):
            phone_number = f'+{phone_number}'
        seller = data['seller']

        user_name = '' if client == 'Без имени' else client
        # call statuses
        direction = 'Входящий' if data['IS_INCOMING_CHANNEL'] == 'Y' else 'Исходящий'
        is_answered = 'Да' if duration != 0 else 'Нет'
        ctx.append({
            'date': created_date_str,
            'seller': seller,
            'client': user_name,
            'client_phone_number': phone_number,
            'direction': direction,
            'answered': is_answered,
            'duration': duration_str,
            'dialing': dialing,
        })
    return ctx
