# Выбранная ранее библиотека PyGithub оказалась менее удобной, чем предполагалось. 
# Намного удобнее собирать данные напрямую через json. APi GitHub ограничивает до 50 запросов в час, что сильно проблематично. 
# При аутентификации по созданному личному токену лимит увеличивается до 5000, но это все равно может вызвать неудобности при анализе большого репозитория.

import requests
import json
from datetime import datetime
from config import token_api

username = 'nodejs'
repo = 'node'
git_token = token_api
url = f'https://api.github.com/repos/{username}/{repo}'
is_date_limit = datetime.fromisoformat("2023-12-31T23:59:59Z")

# TODO удаление данных

# Так как GitHub API ограничивает количество запросов, было принято решение выгрузить данные и сохранить в формате json для последующего анализа.

# Собираем данные об участниках с более чем 100 действиями активности на 20 мая 2024
url_contributors = url + f'/contributors?per_page=100'
r = requests.get(url_contributors, headers={"Authorization": git_token})
data_json = json.loads(r.text)
is_action_limit = False
is_first = True

with open('./data/contributors.json', 'a', encoding='utf-8') as f:
    f.write('[')

while 'next' in r.links.keys() and not is_action_limit:
    for contributor in data_json:
        if contributor['contributions'] < 100: 
            is_action_limit = True
            break
        with open('./data/contributors.json', 'a', encoding='utf-8') as f:
            if not is_first:
                f.write(',')
            else:
                is_first = False
            json.dump(contributor, f, ensure_ascii=False, indent=4)
    r=requests.get(r.links['next']['url'], headers={"Authorization": git_token})
    data_json = json.loads(r.text)

with open('./data/contributors.json', 'a', encoding='utf-8') as f:
    f.write(']')

# Собираем данные о коммитах за 2024 год на 20 мая 2024
url_commit = url + f'/commits?per_page=100'
r = requests.get(url_commit, headers={"Authorization": git_token})
data_json = json.loads(r.text)
is_limit = False
is_first = True

with open('./data/commits.json', 'a', encoding='utf-8') as f:
    f.write('[')

while 'next' in r.links.keys() and not is_limit:
    for commit in data_json:
        if datetime.fromisoformat(commit['commit']['committer']['date']) < is_date_limit:
            is_limit = True
            break
        with open('./data/commits.json', 'a', encoding='utf-8') as f:
            if not is_first:
                f.write(',')
            else:
                is_first = False
            json.dump(commit, f, ensure_ascii=False, indent=4)
    r=requests.get(r.links['next']['url'], headers={"Authorization": git_token})
    data_json = json.loads(r.text)

with open('./data/commits.json', 'a', encoding='utf-8') as f:
    f.write(']')

# Собираем данные о комментариях в коммитах за 2024 год на 20 мая 2024
url_commit_comment = url + f'/comments?per_page=100'
r = requests.get(url_commit_comment, headers={"Authorization": git_token})
is_limit = False
is_first = True

with open('./data/commits_comments.json', 'a', encoding='utf-8') as f:
    f.write('[')

r = requests.get(r.links['last']['url'], headers={"Authorization": git_token})
data_json = json.loads(r.text)

while 'prev' in r.links.keys() and not is_limit:
    for comment in reversed(data_json):
        if datetime.fromisoformat(comment['updated_at']) < is_date_limit:
            is_limit = True
            break
        with open('./data/commits_comments.json', 'a', encoding='utf-8') as f:
            if not is_first:
                f.write(',')
            else:
                is_first = False
            json.dump(comment, f, ensure_ascii=False, indent=4)
    r=requests.get(r.links['prev']['url'], headers={"Authorization": git_token})
    data_json = json.loads(r.text)

with open('./data/commits_comments.json', 'a', encoding='utf-8') as f:
    f.write(']')

# Собираем данные о комментариях в issues за 2024 год на 20 мая 2024
url_issues_comments = url + f'/issues/comments?since="2023-12-31T23:59:59Z"&&per_page=100'
r = requests.get(url_issues_comments, headers={"Authorization": git_token})
data_json = json.loads(r.text)
is_first = True

with open('./data/issues_comments.json', 'a', encoding='utf-8') as f:
    f.write('[')

while 'next' in r.links.keys():
    for comment in data_json:
        with open('./data/issues_comments.json', 'a', encoding='utf-8') as f:
            if not is_first:
                f.write(',')
            else:
                is_first = False
            json.dump(comment, f, ensure_ascii=False, indent=4)
    r=requests.get(r.links['next']['url'], headers={"Authorization": git_token})
    data_json = json.loads(r.text)

with open('./data/issues_comments.json', 'a', encoding='utf-8') as f:
    f.write(']')

# Собираем данные об issues за 2024 год на 20 мая 2024
url_issues = url + f'/issues?per_page=100'
r = requests.get(url_issues, headers={"Authorization": git_token})
data_json = json.loads(r.text)
is_limit = False
is_first = True

with open('./data/issues.json', 'a', encoding='utf-8') as f:
    f.write('[')

while 'next' in r.links.keys() and not is_limit:
    for issue in data_json:
        if datetime.fromisoformat(issue['created_at']) < is_date_limit:
            is_limit = True
            break
        with open('./data/issues.json', 'a', encoding='utf-8') as f:
            if not is_first:
                f.write(',')
            else:
                is_first = False
            json.dump(issue, f, ensure_ascii=False, indent=4)
    r=requests.get(r.links['next']['url'], headers={"Authorization": git_token})
    data_json = json.loads(r.text)

with open('./data/issues.json', 'a', encoding='utf-8') as f:
    f.write(']')

# Собираем данные о pull requests за 2024 год на 20 мая 2024
url_pulls = url + f'/pulls?state=all&per_page=100'
r = requests.get(url_pulls, headers={"Authorization": git_token})
data_json = json.loads(r.text)
is_limit = False
is_first = True

with open('./data/pulls.json', 'a', encoding='utf-8') as f:
    f.write('[')

while 'next' in r.links.keys() and not is_limit:
    for pull in data_json:
        if datetime.fromisoformat(pull['updated_at']) < is_date_limit:
            is_limit = True
            break
        with open('./data/pulls.json', 'a', encoding='utf-8') as f:
            if not is_first:
                f.write(',')
            else:
                is_first = False
            json.dump(pull, f, ensure_ascii=False, indent=4)
    r=requests.get(r.links['next']['url'], headers={"Authorization": git_token})
    data_json = json.loads(r.text)

with open('./data/pulls.json', 'a', encoding='utf-8') as f:
    f.write(']')

# Собираем данные о releases за 2024 год на 20 мая 2024
url_releases = url + f'/releases?per_page=100'
r = requests.get(url_releases, headers={"Authorization": git_token})
data_json = json.loads(r.text)
is_limit = False
is_first = True

with open('./data/releases.json', 'a', encoding='utf-8') as f:
    f.write('[')

while 'next' in r.links.keys() and not is_limit:
    for release in data_json:
        if datetime.fromisoformat(release['published_at']) < is_date_limit:
            is_limit = True
            break
        with open('./data/releases.json', 'a', encoding='utf-8') as f:
            if not is_first:
                f.write(',')
            else:
                is_first = False
            json.dump(release, f, ensure_ascii=False, indent=4)
    r=requests.get(r.links['next']['url'], headers={"Authorization": git_token})
    data_json = json.loads(r.text)

with open('./data/releases.json', 'a', encoding='utf-8') as f:
    f.write(']')

# issues events за 2024 год на 20 мая 2024
url_issues_events = url + f'/issues/events?per_page=100'
r = requests.get(url_issues_events, headers={"Authorization": git_token})
data_json = json.loads(r.text)
is_limit = False
is_first = True

with open('./data/issues_events.json', 'a', encoding='utf-8') as f:
    f.write('[')

while 'next' in r.links.keys() and not is_limit:
    for event in data_json:
        if datetime.fromisoformat(event['created_at']) < is_date_limit:
            is_limit = True
            break
        with open('./data/issues_events.json', 'a', encoding='utf-8') as f:
            if not is_first:
                f.write(',')
            else:
                is_first = False
            json.dump(event, f, ensure_ascii=False, indent=4)
    r=requests.get(r.links['next']['url'], headers={"Authorization": git_token})
    data_json = json.loads(r.text)

with open('./data/issues_events.json', 'a', encoding='utf-8') as f:
    f.write(']')

# events за 2024 год на 20 мая 2024
url_events = url + f'/events?per_page=100'
r = requests.get(url_events, headers={"Authorization": git_token})
data_json = json.loads(r.text)
is_limit = False
is_first = True

with open('./data/events.json', 'a', encoding='utf-8') as f:
    f.write('[')

while 'next' in r.links.keys() and not is_limit:
    for event in data_json:
        if datetime.fromisoformat(event['created_at']) < is_date_limit:
            is_limit = True
            break
        with open('./data/events.json', 'a', encoding='utf-8') as f:
            if not is_first:
                f.write(',')
            else:
                is_first = False
            json.dump(event, f, ensure_ascii=False, indent=4)
    r=requests.get(r.links['next']['url'], headers={"Authorization": git_token})
    data_json = json.loads(r.text)

with open('./data/events.json', 'a', encoding='utf-8') as f:
    f.write(']')