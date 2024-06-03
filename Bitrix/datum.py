import os
import datetime, math, requests
from fast_bitrix24 import Bitrix
from dotenv import load_dotenv

load_dotenv()

BITRIX_URL = os.environ.get('BITRIX_URL')


def prepare_params(params, prev=""):
    """Transforms list of params to a valid bitrix array."""
    ret = ""
    if isinstance(params, dict):
        for key, value in params.items():
            if isinstance(value, dict):
                if prev:
                    key = "{0}[{1}]".format(prev, key)
                ret += prepare_params(value, key)
            elif (isinstance(value, list) or isinstance(value, tuple)) and len(
                    value
            ) > 0:
                for offset, val in enumerate(value):
                    if isinstance(val, dict):
                        ret += prepare_params(
                            val, "{0}[{1}][{2}]".format(prev, key, offset)
                        )
                    else:
                        if prev:
                            ret += "{0}[{1}][{2}]={3}&".format(prev, key, offset, val)
                        else:
                            ret += "{0}[{1}]={2}&".format(key, offset, val)
            else:
                if prev:
                    ret += "{0}[{1}]={2}&".format(prev, key, value)
                else:
                    ret += "{0}={1}&".format(key, value)
    return ret


def create_batch(method, params: dict = {}):
    params['start'] = 0
    r = requests.get(f'{BITRIX_URL}{method}',
                     params=prepare_params(params))
    record_count = r.json()['time']['duration']
    params['start'] = -1
    batches = []
    cmds = {}
    for i in range(math.ceil(record_count / 50)):
        if i >= 50:
            batches.append({'halt': 0, 'cmd': cmds})
            cmds = {}
        params['start'] = i * 50
        filter_param = prepare_params(params)
        cmds[f'get_{i}'] = f'{method}?{filter_param}'
    batches.append({'halt': 0, 'cmd': cmds})
    return batches


def get_contact_by_id(contact_id: int):
    btx = Bitrix(BITRIX_URL)
    batches = create_batch('crm.contact.get', params={'ID': contact_id})
    contact_info = {}
    for batch in batches:
        r: dict = btx.call_batch(batch)
        for key, res in r.items():
            name = res['NAME'] if res['NAME'] else ''
            phone = res['PHONE'][0]['VALUE'] if res['PHONE'] and res['PHONE'][0]['VALUE'] else 'Undefined'
            contact_info[name] = phone
    return contact_info


def get_user_by_id(user_id: int):
    btx = Bitrix(BITRIX_URL)
    batches = create_batch('user.get', params={'ID': user_id})
    for batch in batches:
        temp: dict = btx.call_batch(batch)
        for key, res in temp.items():
            user_name = res[0]['NAME'] if res[0]['NAME'] else 'Unknown'
            user_surname = res[0]['LAST_NAME'] if res[0]['LAST_NAME'] else 'Unknown'
    user = f'{user_name} {user_surname}'
    return user


def get_deal_by_id(deal_id: int):
    btx = Bitrix(BITRIX_URL)
    batches = create_batch('crm.deal.get', params={'ID': deal_id})
    deal_info = []
    for batch in batches:
        r: dict = btx.call_batch(batch)
        for key, res in r.items():
            deal_info.append(res)
    contact = get_contact_by_id(deal_info[0]['CONTACT_ID'])
    return contact


def get_calls_fast():
    yesterday_date = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
    calls = []
    params = {
        'filter': {
            'TYPE_ID': 2, 'OWNER_TYPE_ID': 2, '>CREATED': yesterday_date
        },
        'select': ['OWNER_ID', 'CREATED', 'AUTHOR_ID', 'START_TIME', 'END_TIME',
                   'IS_INCOMING_CHANNEL', 'LAST_UPDATE', 'SUBJECT'],
    }

    batches = create_batch('crm.activity.list', params)
    btx = Bitrix(BITRIX_URL)
    for batch in batches:
        resp = btx.call_batch(batch)
        for key, val in resp.items():
            calls.extend(val)

    for call in calls:
        call['contact'] = get_deal_by_id(call['OWNER_ID'])
        author_id = call['AUTHOR_ID']
        user = get_user_by_id(author_id)
        call.update({'seller': user})
        call['responsible_user'] = call['contact'].keys()
        call['responsible_user_phone'] = call['contact'].values()

    return calls
