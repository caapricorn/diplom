import requests
from config import token_api
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

def repo_exist(url, log = lambda x: print(x)):
    r = requests.get(url, headers={"Authorization": token_api})
    if r.status_code == 404:
        log("Repository does not exist. Try again.")
        return False
    return True

def clean_user_data(path):
    if not os.path.exists(path): 
        print(f'Создаем {path}...')
        os.makedirs(path)
    else:
        try:
            for root, dirs, files in os.walk(path, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for directory in dirs:
                    os.rmdir(os.path.join(root, directory))
        except Exception as e:
                print(f'Ошибка при удалении {path}. {e}')

def get_creation_date(file_path):
    file_creation_time = os.path.getctime(file_path)
    creation_datetime = datetime.fromtimestamp(file_creation_time)
    date_data = creation_datetime.isoformat() + 'Z'
    return date_data

def minus_month(date_str, count):
    date_obj = datetime.fromisoformat(date_str.replace('Z', ''))
    new_date_obj = date_obj - relativedelta(months=count)
    new_date_str = new_date_obj.isoformat() + 'Z'
    return new_date_str

def make_request_with_retries(url):
    attempt = 0
    initial_delay=1
    delay = initial_delay
    max_retries = 100
    backoff_factor=2

    while attempt < max_retries:
        response = requests.get(url, headers={"Authorization": token_api})

        if 200 <= response.status_code < 300:
            return response
        else:
            time.sleep(delay)
            delay *= backoff_factor
            attempt += 1