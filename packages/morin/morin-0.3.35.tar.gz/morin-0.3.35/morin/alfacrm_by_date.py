from .common import Common
from .clickhouse import Clickhouse
import requests
from datetime import datetime,timedelta
import clickhouse_connect
import pandas as pd
import os
from dateutil import parser
import time
import hashlib
from io import StringIO
import json
from dateutil.relativedelta import relativedelta


class ALFAbyDate:
    def __init__(self,  bot_token:str, chats:str, message_type: str, subd: str,
                 host: str, port: str, username: str, password: str, database: str,
                                  add_name: str, main_url:str, token: str ,  xappkey:str, email: str ,
                 start: str, backfill_days: int, reports :str, branches: str):
        self.bot_token = bot_token
        self.chat_list = chats.replace(' ', '').split(',')
        self.message_type = message_type
        self.common = Common(self.bot_token, self.chat_list, self.message_type)
        self.main_url = main_url
        self.token = token
        self.branches_list = branches.replace(' ','').strip().split(',')
        self.xappkey = xappkey
        self.email = email
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.subd = subd
        self.add_name = self.common.transliterate_key(add_name)
        self.now = datetime.now()
        self.today = datetime.now().date()
        self.start = start
        self.reports = reports
        self.backfill_days = backfill_days
        self.platform = 'alfa'
        self.err429 = False
        self.branch = '0'
        self.source_dict = {
            'branch': {
                'platform': 'alfa',
                'report_name': 'branch',
                'upload_table': 'branch',
                'func_name': self.get_branch,
                'uniq_columns': 'id',
                'partitions': '',
                'merge_type': 'ReplacingMergeTree(timeStamp)',
                'refresh_type': 'nothing',
                'history': False,
                'frequency': 'daily',  # '2dayOfMonth,Friday'
                'delay': 3
            },
            'location': {
                'platform': 'alfa',
                'report_name': 'location',
                'upload_table': 'location',
                'func_name': self.get_location,
                'uniq_columns': 'id',
                'partitions': '',
                'merge_type': 'ReplacingMergeTree(timeStamp)',
                'refresh_type': 'nothing',
                'history': False,
                'frequency': 'daily',  # '2dayOfMonth,Friday'
                'delay': 3
            },
            'teacher': {
                'platform': 'alfa',
                'report_name': 'teacher',
                'upload_table': 'teacher',
                'func_name': self.get_teacher,
                'uniq_columns': 'id',
                'partitions': '',
                'merge_type': 'ReplacingMergeTree(timeStamp)',
                'refresh_type': 'nothing',
                'history': False,
                'frequency': 'daily',  # '2dayOfMonth,Friday'
                'delay': 3
            },
            'customer': {
                'platform': 'alfa',
                'report_name': 'customer',
                'upload_table': 'customer',
                'func_name': self.get_customer,
                'uniq_columns': 'id',
                'partitions': '',
                'merge_type': 'ReplacingMergeTree(timeStamp)',
                'refresh_type': 'nothing',
                'history': True,
                'frequency': 'daily',  # '2dayOfMonth,Friday'
                'delay': 3
            },
            'pay': {
                'platform': 'alfa',
                'report_name': 'pay',
                'upload_table': 'pay',
                'func_name': self.get_pay,
                'uniq_columns': 'id',
                'partitions': '',
                'merge_type': 'ReplacingMergeTree(timeStamp)',
                'refresh_type': 'nothing',
                'history': True,
                'frequency': 'daily',  # '2dayOfMonth,Friday'
                'delay': 3
            },
            'lesson': {
                'platform': 'alfa',
                'report_name': 'lesson',
                'upload_table': 'lesson',
                'func_name': self.get_lesson,
                'uniq_columns': 'id',
                'partitions': '',
                'merge_type': 'ReplacingMergeTree(timeStamp)',
                'refresh_type': 'nothing',
                'history': True,
                'frequency': 'daily',  # '2dayOfMonth,Friday'
                'delay': 3
            },
            'update_customer': {
                'platform': 'alfa',
                'report_name': 'update_customer',
                'upload_table': 'customer',
                'func_name': self.update_customer,
                'uniq_columns': 'id',
                'partitions': '',
                'merge_type': 'ReplacingMergeTree(timeStamp)',
                'refresh_type': 'nothing',
                'history': True,
                'frequency': 'daily',  # '2dayOfMonth,Friday'
                'delay': 3
            },
            'update_pay': {
                'platform': 'alfa',
                'report_name': 'update_pay',
                'upload_table': 'pay',
                'func_name': self.update_pay,
                'uniq_columns': 'id',
                'partitions': '',
                'merge_type': 'ReplacingMergeTree(timeStamp)',
                'refresh_type': 'nothing',
                'history': True,
                'frequency': 'daily',  # '2dayOfMonth,Friday'
                'delay': 3
            },
            'update_lesson': {
                'platform': 'alfa',
                'report_name': 'update_lesson',
                'upload_table': 'lesson',
                'func_name': self.update_lesson,
                'uniq_columns': 'id',
                'partitions': '',
                'merge_type': 'ReplacingMergeTree(timeStamp)',
                'refresh_type': 'nothing',
                'history': True,
                'frequency': 'daily',  # '2dayOfMonth,Friday'
                'delay': 3
            },
        }

    def auth(self):
        try:
            url = f"{self.main_url.rstrip('/')}/v2api/auth/login"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-APP-KEY": self.xappkey
            }
            data = {
                "email": self.email,
                "api_key": self.token
            }
            response = requests.post(url, headers=headers, data=json.dumps(data))
            code = response.status_code
            if code != 200:
                response.raise_for_status()
            else:
                result = response.json()
                self.access_token = result.get("token")
        except Exception as e:
            message = f'Платформа: ALFA. Имя: {self.add_name}. Функция: auth. Ошибка: {e}.'
            self.common.log_func(self.bot_token, self.chat_list, message, 3)
            raise



    def get_basic(self,url,filter_field_1=None, filter_value_1=None,filter_field_2=None, filter_value_2=None):
        try:
            all_data = []
            id0 = 0
            page = 0
            url = f"{self.main_url.rstrip('/')}/{url}"
            headers = {
                "X-ALFACRM-TOKEN": self.access_token,
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            while True:
                if filter_field_1 and filter_value_1 and filter_field_2 and filter_value_2:
                    data = {"page": page,                        filter_field_1: filter_value_1, filter_field_2: filter_value_2}
                elif filter_field_1 and filter_value_1 :
                    data = {"page": page, filter_field_1: filter_value_1}
                else:
                    data = {                        "page": page                    }
                response = requests.post(url, headers=headers, data=json.dumps(data))
                code = response.status_code
                if code == 401:
                    self.auth()
                    time.sleep(1)
                    response = requests.post(url, headers=headers, data=json.dumps(data))
                    code = response.status_code
                if code != 200:
                    response.raise_for_status()
                else:
                    result = response.json()
                    data = result['items']
                    if len(data) > 0:
                        id1 = int(data[0]['id'])
                        if id0 == id1:
                            break
                        all_data += data
                if len(data) < 50:
                    break
                page +=1
                time.sleep(1)
                id0 = id1
            return all_data
        except Exception as e:
            message = f'Платформа: ALFA. Имя: {self.add_name}. Функция: get_basic. Ошибка: {e}.'
            self.common.log_func(self.bot_token, self.chat_list, message, 3)
            raise

    def get_branch(self, date):
        try:
            final_result = self.get_basic('v2api/branch/index')
            message = f'Платформа: ALFA. Имя: {self.add_name}. Дата: {str(date)}. Функция: get_branch. Результат: ОК'
            self.common.log_func(self.bot_token, self.chat_list, message, 1)
            return final_result
        except Exception as e:
            message = f'Платформа: ALFA. Имя: {self.add_name}. Дата: {str(date)}. Функция: get_branch. Ошибка: {e}.'
            self.common.log_func(self.bot_token, self.chat_list, message, 3)
            return message

    def get_location(self, date):
        try:
            final_result = self.get_basic(f'v2api/{self.branch}/location/index')
            message = f'Платформа: ALFA. Имя: {self.add_name}. Дата: {str(date)}. Функция: get_location. Результат: ОК'
            self.common.log_func(self.bot_token, self.chat_list, message, 1)
            return final_result
        except Exception as e:
            message = f'Платформа: ALFA. Имя: {self.add_name}. Дата: {str(date)}. Функция: get_location. Ошибка: {e}.'
            self.common.log_func(self.bot_token, self.chat_list, message, 3)
            return message

    def get_customer(self, date):
        try:
            final_result = self.get_basic(f'v2api/{self.branch}/customer/index', 'created_at_to', self.common.flip_date(date),'created_at_from', self.common.flip_date(date))
            message = f'Платформа: ALFA. Имя: {self.add_name}. Дата: {str(date)}. Функция: get_customer. Результат: ОК'
            self.common.log_func(self.bot_token, self.chat_list, message, 1)
            return final_result
        except Exception as e:
            message = f'Платформа: ALFA. Имя: {self.add_name}. Дата: {str(date)}. Функция: get_customer. Ошибка: {e}.'
            self.common.log_func(self.bot_token, self.chat_list, message, 3)
            return message

    def get_lesson(self, date):
        try:
            final_result = self.get_basic(f'v2api/{self.branch}/lesson/index', 'created_at_to', self.common.flip_date(date),'created_at_from', self.common.flip_date(date))
            message = f'Платформа: ALFA. Имя: {self.add_name}. Дата: {str(date)}. Функция: get_lesson. Результат: ОК'
            self.common.log_func(self.bot_token, self.chat_list, message, 1)
            return final_result
        except Exception as e:
            message = f'Платформа: ALFA. Имя: {self.add_name}. Дата: {str(date)}. Функция: get_lesson. Ошибка: {e}.'
            self.common.log_func(self.bot_token, self.chat_list, message, 3)
            return message

    def get_pay(self, date):
        try:
            final_result = self.get_basic(f'v2api/{self.branch}/pay/index', 'created_at_to', self.common.flip_date(date),'created_at_from', self.common.flip_date(date))
            message = f'Платформа: ALFA. Имя: {self.add_name}. Дата: {str(date)}. Функция: get_pay. Результат: ОК'
            self.common.log_func(self.bot_token, self.chat_list, message, 1)
            return final_result
        except Exception as e:
            message = f'Платформа: ALFA. Имя: {self.add_name}. Дата: {str(date)}. Функция: get_pay. Ошибка: {e}.'
            self.common.log_func(self.bot_token, self.chat_list, message, 3)
            return message

    def update_customer(self, date):
        try:
            final_result = self.get_basic(f'v2api/{self.branch}/customer/index', 'updated_at_to', self.common.flip_date(date),'updated_at_from', self.common.flip_date(date))
            message = f'Платформа: ALFA. Имя: {self.add_name}. Дата: {str(date)}. Функция: update_customer. Результат: ОК'
            self.common.log_func(self.bot_token, self.chat_list, message, 1)
            return final_result
        except Exception as e:
            message = f'Платформа: ALFA. Имя: {self.add_name}. Дата: {str(date)}. Функция: update_customer. Ошибка: {e}.'
            self.common.log_func(self.bot_token, self.chat_list, message, 3)
            return message

    def update_lesson(self, date):
        try:
            final_result = self.get_basic(f'v2api/{self.branch}/lesson/index', 'updated_at_to', self.common.flip_date(date),'updated_at_from', self.common.flip_date(date))
            message = f'Платформа: ALFA. Имя: {self.add_name}. Дата: {str(date)}. Функция: update_lesson. Результат: ОК'
            self.common.log_func(self.bot_token, self.chat_list, message, 1)
            return final_result
        except Exception as e:
            message = f'Платформа: ALFA. Имя: {self.add_name}. Дата: {str(date)}. Функция: update_lesson. Ошибка: {e}.'
            self.common.log_func(self.bot_token, self.chat_list, message, 3)
            return message

    def update_pay(self, date):
        try:
            final_result = self.get_basic(f'v2api/{self.branch}/pay/index', 'updated_at_to', self.common.flip_date(date),'updated_at_from', self.common.flip_date(date))
            message = f'Платформа: ALFA. Имя: {self.add_name}. Дата: {str(date)}. Функция: update_pay. Результат: ОК'
            self.common.log_func(self.bot_token, self.chat_list, message, 1)
            return final_result
        except Exception as e:
            message = f'Платформа: ALFA. Имя: {self.add_name}. Дата: {str(date)}. Функция: update_pay. Ошибка: {e}.'
            self.common.log_func(self.bot_token, self.chat_list, message, 3)
            return message

    def get_teacher(self, date):
        try:
            final_result = self.get_basic(f'v2api/{self.branch}/teacher/index')
            message = f'Платформа: ALFA. Имя: {self.add_name}. Дата: {str(date)}. Функция: get_teacher. Результат: ОК'
            self.common.log_func(self.bot_token, self.chat_list, message, 1)
            return final_result
        except Exception as e:
            message = f'Платформа: ALFA. Имя: {self.add_name}. Дата: {str(date)}. Функция: get_teacher. Ошибка: {e}.'
            self.common.log_func(self.bot_token, self.chat_list, message, 3)
            return message


    def collecting_manager(self):
        self.auth()
        report_list = self.reports.replace(' ', '').lower().split(',')
        for report in report_list:
            self.clickhouse = Clickhouse(self.bot_token, self.chat_list, self.message_type, self.host, self.port,
                                         self.username, self.password,
                                         self.database, self.start, self.add_name, self.err429, self.backfill_days,
                                         self.platform)
            if report == 'branch':
                    self.clickhouse.collecting_report(
                        self.source_dict[report]['platform'],
                        self.source_dict[report]['report_name'],
                        self.source_dict[report]['upload_table'],
                        self.source_dict[report]['func_name'],
                        self.source_dict[report]['uniq_columns'],
                        self.source_dict[report]['partitions'],
                        self.source_dict[report]['merge_type'],
                        self.source_dict[report]['refresh_type'],
                        self.source_dict[report]['history'],
                        self.source_dict[report]['frequency'],
                        self.source_dict[report]['delay']
                    )
            else:
                for branch in self.branches_list:
                    self.branch = str(branch).strip()
                    self.clickhouse.collecting_report(
                        self.source_dict[report]['platform'],
                        self.source_dict[report]['report_name'],
                        self.source_dict[report]['upload_table'],
                        self.source_dict[report]['func_name'],
                        self.source_dict[report]['uniq_columns'],
                        self.source_dict[report]['partitions'],
                        self.source_dict[report]['merge_type'],
                        self.source_dict[report]['refresh_type'],
                        self.source_dict[report]['history'],
                        self.source_dict[report]['frequency'],
                        self.source_dict[report]['delay']
                    )




