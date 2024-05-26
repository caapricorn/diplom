import requests
import json
from datetime import datetime
from config import token_api
import sys
from utils import repo_exist, clean_user_data
import os

is_date_limit = datetime.fromisoformat("2023-12-31T23:59:59Z")

def contributors(folder_name, url, log = lambda x: print(x)):
    log("Скачиваем данные об участниках...")
    url_contributors = url + f'/contributors?per_page=100'
    r = requests.get(url_contributors, headers={"Authorization": token_api})
    data_json = json.loads(r.text)
    is_action_limit = False
    is_first = True
    path = f'./data/{folder_name}/json/contributors.json'

    with open(path, 'a', encoding='utf-8') as f:
        f.write('[')

    while 'next' in r.links.keys() and not is_action_limit:
        for contributor in data_json:
            if contributor['contributions'] < 100: 
                is_action_limit = True
                break
            with open(path, 'a', encoding='utf-8') as f:
                if not is_first:
                    f.write(',')
                else:
                    is_first = False
                json.dump(contributor, f, ensure_ascii=False, indent=4)
        r=requests.get(r.links['next']['url'], headers={"Authorization": token_api})
        data_json = json.loads(r.text)

    with open(path, 'a', encoding='utf-8') as f:
        f.write(']')

def commits(folder_name, url, log = lambda x: print(x)):
    log("Скачиваем данные о коммитах...")
    url_commit = url + f'/commits?per_page=100'
    r = requests.get(url_commit, headers={"Authorization": token_api})
    data_json = json.loads(r.text)
    is_limit = False
    is_first = True
    path = f'./data/{folder_name}/json/commits.json'

    with open(path, 'a', encoding='utf-8') as f:
        f.write('[')

    while 'next' in r.links.keys() and not is_limit:
        for commit in data_json:
            if datetime.fromisoformat(commit['commit']['committer']['date']) < is_date_limit:
                is_limit = True
                break
            with open(path, 'a', encoding='utf-8') as f:
                if not is_first:
                    f.write(',')
                else:
                    is_first = False
                json.dump(commit, f, ensure_ascii=False, indent=4)
        r=requests.get(r.links['next']['url'], headers={"Authorization": token_api})
        data_json = json.loads(r.text)

    with open(path, 'a', encoding='utf-8') as f:
        f.write(']')

def comments(folder_name, url, log = lambda x: print(x)):
    log("Скачиваем данные о комментариях в коммитах...")
    url_commit_comment = url + f'/comments?per_page=100'
    r = requests.get(url_commit_comment, headers={"Authorization": token_api})
    is_limit = False
    is_first = True
    path = f'./data/{folder_name}/json/commits_comments.json'

    with open(path, 'a', encoding='utf-8') as f:
        f.write('[')

    if 'last' in r.links.keys():
        r = requests.get(r.links['last']['url'], headers={"Authorization": token_api})
    data_json = json.loads(r.text)

    while 'prev' in r.links.keys() and not is_limit:
        for comment in reversed(data_json):
            if datetime.fromisoformat(comment['updated_at']) < is_date_limit:
                is_limit = True
                break
            with open(path, 'a', encoding='utf-8') as f:
                if not is_first:
                    f.write(',')
                else:
                    is_first = False
                json.dump(comment, f, ensure_ascii=False, indent=4)
        r=requests.get(r.links['prev']['url'], headers={"Authorization": token_api})
        data_json = json.loads(r.text)

    with open(path, 'a', encoding='utf-8') as f:
        f.write(']')

def issues(folder_name, url, log = lambda x: print(x)):
    log("Скачиваем данные об issues...")
    url_issues = url + f'/issues?per_page=100'
    r = requests.get(url_issues, headers={"Authorization": token_api})
    data_json = json.loads(r.text)
    is_limit = False
    is_first = True
    path = f'./data/{folder_name}/json/issues.json'

    with open(path, 'a', encoding='utf-8') as f:
        f.write('[')

    while 'next' in r.links.keys() and not is_limit:
        for issue in data_json:
            if datetime.fromisoformat(issue['created_at']) < is_date_limit:
                is_limit = True
                break
            with open(path, 'a', encoding='utf-8') as f:
                if not is_first:
                    f.write(',')
                else:
                    is_first = False
                json.dump(issue, f, ensure_ascii=False, indent=4)
        r=requests.get(r.links['next']['url'], headers={"Authorization": token_api})
        data_json = json.loads(r.text)

    with open(path, 'a', encoding='utf-8') as f:
        f.write(']')

def issues_comments(folder_name, url, log = lambda x: print(x)):
    log("Скачиваем данные о комментариях в issues...")
    url_issues_comments = url + f'/issues/comments?since="2023-12-31T23:59:59Z"&&per_page=100'
    r = requests.get(url_issues_comments, headers={"Authorization": token_api})
    data_json = json.loads(r.text)
    is_first = True
    path = f'./data/{folder_name}/json/issues_comments.json'

    with open(path, 'a', encoding='utf-8') as f:
        f.write('[')

    while 'next' in r.links.keys():
        for comment in data_json:
            with open(path, 'a', encoding='utf-8') as f:
                if not is_first:
                    f.write(',')
                else:
                    is_first = False
                json.dump(comment, f, ensure_ascii=False, indent=4)
        r=requests.get(r.links['next']['url'], headers={"Authorization": token_api})
        data_json = json.loads(r.text)

    with open(path, 'a', encoding='utf-8') as f:
        f.write(']')

def issues_events(folder_name, url, log = lambda x: print(x)):
    log("Скачиваем данные о issues events...")
    url_issues_events = url + f'/issues/events?per_page=100'
    r = requests.get(url_issues_events, headers={"Authorization": token_api})
    data_json = json.loads(r.text)
    is_limit = False
    is_first = True
    path = f'./data/{folder_name}/json/issues_events.json'

    with open(path, 'a', encoding='utf-8') as f:
        f.write('[')

    while 'next' in r.links.keys() and not is_limit:
        for event in data_json:
            if datetime.fromisoformat(event['created_at']) < is_date_limit:
                is_limit = True
                break
            with open(path, 'a', encoding='utf-8') as f:
                if not is_first:
                    f.write(',')
                else:
                    is_first = False
                json.dump(event, f, ensure_ascii=False, indent=4)
        r=requests.get(r.links['next']['url'], headers={"Authorization": token_api})
        data_json = json.loads(r.text)

    with open(path, 'a', encoding='utf-8') as f:
        f.write(']')

def pulls(folder_name, url, log = lambda x: print(x)):
    log("Скачиваем данные о pull requests...")
    url_pulls = url + f'/pulls?state=all&per_page=100'
    r = requests.get(url_pulls, headers={"Authorization": token_api})
    data_json = json.loads(r.text)
    is_limit = False
    is_first = True
    path = f'./data/{folder_name}/json/pulls.json'

    with open(path, 'a', encoding='utf-8') as f:
        f.write('[')

    while 'next' in r.links.keys() and not is_limit:
        for pull in data_json:
            if datetime.fromisoformat(pull['updated_at']) < is_date_limit:
                is_limit = True
                break
            with open(path, 'a', encoding='utf-8') as f:
                if not is_first:
                    f.write(',')
                else:
                    is_first = False
                json.dump(pull, f, ensure_ascii=False, indent=4)
        r=requests.get(r.links['next']['url'], headers={"Authorization": token_api})
        data_json = json.loads(r.text)

    with open(path, 'a', encoding='utf-8') as f:
        f.write(']')

def releases(folder_name, url, log = lambda x: print(x)):
    log("Скачиваем данные о releases...")
    url_releases = url + f'/releases?per_page=100'
    r = requests.get(url_releases, headers={"Authorization": token_api})
    data_json = json.loads(r.text)
    is_limit = False
    is_first = True
    path = f'./data/{folder_name}/json/releases.json'

    with open(path, 'a', encoding='utf-8') as f:
        f.write('[')

    while 'next' in r.links.keys() and not is_limit:
        for release in data_json:
            if datetime.fromisoformat(release['published_at']) < is_date_limit:
                is_limit = True
                break
            with open(path, 'a', encoding='utf-8') as f:
                if not is_first:
                    f.write(',')
                else:
                    is_first = False
                json.dump(release, f, ensure_ascii=False, indent=4)
        r=requests.get(r.links['next']['url'], headers={"Authorization": token_api})
        data_json = json.loads(r.text)

    with open(path, 'a', encoding='utf-8') as f:
        f.write(']')

def events(folder_name, url, log = lambda x: print(x)):
    log("Скачиваем данные о events...")
    url_events = url + f'/events?per_page=100'
    r = requests.get(url_events, headers={"Authorization": token_api})
    data_json = json.loads(r.text)
    is_limit = False
    is_first = True
    path = f'./data/{folder_name}/json/events.json'

    with open(path, 'a', encoding='utf-8') as f:
        f.write('[')

    while 'next' in r.links.keys() and not is_limit:
        for event in data_json:
            if datetime.fromisoformat(event['created_at']) < is_date_limit:
                is_limit = True
                break
            with open(path, 'a', encoding='utf-8') as f:
                if not is_first:
                    f.write(',')
                else:
                    is_first = False
                json.dump(event, f, ensure_ascii=False, indent=4)
        r=requests.get(r.links['next']['url'], headers={"Authorization": token_api})
        data_json = json.loads(r.text)

    with open(path, 'a', encoding='utf-8') as f:
        f.write(']')

def parse(username, repo, log = lambda x: print(x)):
    url = f'https://api.github.com/repos/{username}/{repo}'
    folder_name = f'{username}-{repo}'

    if not repo_exist(url, log):
        sys.exit(0)

    clean_user_data(f'./data/{folder_name}')
    os.makedirs(f'./data/{folder_name}/json')

    contributors(folder_name, url, log)
    
    commits(folder_name, url, log)
    
    comments(folder_name, url, log)

    issues(folder_name, url, log)
    
    issues_comments(folder_name, url, log)

    issues_events(folder_name, url, log)
    
    pulls(folder_name, url, log)

    releases(folder_name, url, log)  

    events(folder_name, url, log)