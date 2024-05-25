import requests
from config import token_api
import os

def repo_exist(url):
    r = requests.get(url, headers={"Authorization": token_api})
    if r.status_code == 404:
        print ("Repository does not exist. Try again.")
        return False
    return True

def clean_user_data(path):
    if not os.path.exists(path): 
        print(f'Создаем {path}...')
        os.makedirs(path)
    else:
        for filename in os.listdir(path):
            print(f'Очищаем {path}...')
            file_path = os.path.join(path, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f'Ошибка при удалении файла {file_path}. {e}')