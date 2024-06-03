import gspread
import datetime
from oauth2client.service_account import ServiceAccountCredentials


class GoogleSheetsManager:
    def __init__(self, credentials_file, sheet_url):
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, self.scope)
        self.gc = gspread.authorize(self.credentials)
        self.sheet_url = sheet_url
        self.sheet = self.gc.open_by_url(self.sheet_url)
        self.worksheet = self.sheet.get_worksheet(0)

    def get_sheet_data(self):
        return self.worksheet.get_all_values()

    def append_row(self, data):
        self.worksheet.append_row(data, value_input_option='USER_ENTERED')


class CallData:
    def __init__(self, date_str, employee, phone_number, client, call_status, answered, call_duration, dialing, source):
        self.date_str = date_str
        self.employee = employee
        self.phone_number = phone_number
        self.client = client
        self.call_status = call_status
        self.answered = answered
        self.call_duration = call_duration
        self.dialing = dialing
        self.source = source

    def format_data(self, length_data):
        custom_datetime = datetime.datetime.strptime(self.date_str, '%d.%m.%Y %H:%M:%S')
        finally_date = custom_datetime.strftime('%d.%m.%Y %H:%M:%S')

        sorted_number = f'=RIGHT(C{length_data};9)'
        seconds = f'=HOUR(G{length_data})*3600+MINUTE(G{length_data})*60+SECOND(G{length_data})'
        above_hundred = f'=IF(K{length_data}>179;1;0)'
        above_thirty = f'=IF(K{length_data}>29;1;0)'

        thirty = "30 sekundgacha"
        one_minute = "1 minutgacha"
        two_hundred = "3 minutgacha"
        five_hundred = "5 minutgacha"
        thousand = "10 minutgacha"
        above_thousand = "10 minutdan ko'p"

        category = (
            f'=IF(K{length_data}<30;"{thirty}";'
            f'IF(K{length_data}<60;"{one_minute}";'
            f'IF(K{length_data}<180;"{two_hundred}";'
            f'IF(K{length_data}<300;"{five_hundred}";'
            f'IF(K{length_data}<600;"{thousand}";'
            f'"{above_thousand}")))))'
        )

        minutes = f"=K{length_data}/60"
        weekday = f"=WEEKDAY(A{length_data})"
        hours = f"=HOUR(A{length_data})"

        first_category = "8dan-13gacha"
        second_category = "13dan-16gacha"
        third_category = "16 dan keyin"
        category_time = (
            f'=IF(Q{length_data}<13;"{first_category}";'
            f'IF(Q{length_data}<16;"{second_category}";'
            f'"{third_category}"))'
        )

        return [
            finally_date, self.employee, self.phone_number, self.client, self.call_status, self.answered,
            self.call_duration, self.dialing, self.source, sorted_number, seconds, above_hundred,
            above_thirty, category, minutes, weekday, hours, category_time
        ]
