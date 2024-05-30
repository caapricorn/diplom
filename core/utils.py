import requests
from config import token_api
import os

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