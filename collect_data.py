import requests
import json
import pandas as pd
from datetime import datetime
from config import token_api
from languages import extension_to_language

def get_unique_words(row):
        words = row.split(',')
        unique_words = set(words)
        unique_words_list = list(unique_words)
        return unique_words_list

# парсим собранные данные и оформляем их в удобный нам формат
# TODO проверка на ботов
def collect(username, repo):
    git_token = token_api
    url = f'https://api.github.com/repos/{username}/{repo}'
    date_today = datetime.fromisoformat("2024-05-23T23:59:59Z")
    date_start = datetime.fromisoformat("2023-12-31T23:59:59Z")
    data_df = []

    print("Собираем данные об участниках...")
    index_login = []
    with open(f'./data/{username}/contributors.json', "r", encoding="utf-8") as f:
        contributors = json.load(f)
    for contributor in contributors:
        index_login.append(contributor['login'])
        data_df.append({"Contributions": contributor['contributions']})
    data_df = pd.DataFrame(data_df, index=index_login)

    data_df['CommitEvent'] = 0
    data_df['Additions'] = 0
    data_df['Deletions'] = 0
    data_df['Languages'] = ''
    data_df['FirstDataActivity'] = date_today
    data_df['LastDataActivity'] = date_start
    data_df['CommitCommentEvent'] = 0
    data_df['CreateEvent'] = 0
    data_df['DeleteEvent'] = 0
    data_df['ForkEvent'] = 0
    data_df['IssueCommentEvent'] = 0
    data_df['PullRequestEvent'] = 0
    data_df['PullRequestReviewEvent'] = 0
    data_df['PullRequestReviewCommentEvent'] = 0
    data_df['PushEvent'] = 0
    data_df['ReleaseEvent'] = 0
    data_df['IssuesEvent'] = 0
    data_df['CreateIssueEvent'] = 0
    data_df['PermissionRole'] = 0

    print("Собираем данные о коммитах...")
    with open(f'./data/{username}/commits.json', "r", encoding="utf-8") as f:
        commits = json.load(f)
    for commit in commits:
        if commit['author']:
            login = commit['author']['login']
        elif commit['committer']:
            login = commit['committer']['login']
        else: login = ''
        if len(login) != 0 and login in data_df.index:
            data_df.loc[login, ['CommitEvent']] += 1
            data_of_commit = datetime.fromisoformat(commit['commit']['committer']['date'])
            if (data_df.loc[login, ['FirstDataActivity']] > data_of_commit).all():
                data_df.loc[login, ['FirstDataActivity']] = data_of_commit
            if (data_df.loc[login, ['LastDataActivity']] < data_of_commit).all():
                data_df.loc[login, ['LastDataActivity']] = data_of_commit
            url_commit = commit['url']
            r = requests.get(url_commit, headers={"Authorization": git_token})
            data_json = json.loads(r.text)
            data_df.loc[login, ['Additions']] += data_json['stats']['additions']
            data_df.loc[login, ['Deletions']] += data_json['stats']['deletions']
            if len(data_json['files']) != 0:
                file_of_commit = data_json['files'][0]['filename'].split('.')[-1]
                language = extension_to_language.get(file_of_commit)
                if language is not None:
                    data_df.loc[login, ['Languages']] = data_df.loc[login, ['Languages']] + language[0] + ','

    data_df['Languages'] = data_df['Languages'].apply(get_unique_words)

    print("Собираем данные о комментариях в коммитах...")
    with open(f'./data/{username}/commits_comments.json', "r", encoding="utf-8") as f:
        comments = json.load(f)
    for comment in comments:
        if comment['user']['login'] in data_df.index:
            data_df.loc[comment['user']['login'], ['CommitCommentEvent']] += 1
            data_of_comment = datetime.fromisoformat(comment['updated_at'])
            if (data_df.loc[comment['user']['login'], ['FirstDataActivity']] > data_of_comment).all():
                data_df.loc[comment['user']['login'], ['FirstDataActivity']] = data_of_comment
            if (data_df.loc[comment['user']['login'], ['LastDataActivity']] < data_of_comment).all():
                data_df.loc[comment['user']['login'], ['LastDataActivity']] = data_of_comment

    print("Собираем данные о действиях разработчиков...")
    with open(f'./data/{username}/events.json', "r", encoding="utf-8") as f:
        events = json.load(f)
    for event in events:
        if event['actor']['login'] in data_df.index:
            if event['type'] not in data_df:
                data_df[event['type']] = 0
            data_df.loc[event['actor']['login'], [event['type']]] += 1
            data_of_event = datetime.fromisoformat(event['created_at'])
            if (data_df.loc[event['actor']['login'], ['FirstDataActivity']] > data_of_event).all():
                data_df.loc[event['actor']['login'], ['FirstDataActivity']] = data_of_event
            if (data_df.loc[event['actor']['login'], ['LastDataActivity']] < data_of_event).all():
                data_df.loc[event['actor']['login'], ['LastDataActivity']] = data_of_event

    print("Собираем данные о комментариях в issues...")
    with open(f'./data/{username}/issues_comments.json', "r", encoding="utf-8") as f:
        comments = json.load(f)
    for comment in comments:
        if comment['user']['login'] in data_df.index:
            data_df.loc[comment['user']['login'], ['IssueCommentEvent']] += 1
            data_of_comment = datetime.fromisoformat(comment['updated_at'])
            if (data_df.loc[comment['user']['login'], ['FirstDataActivity']] > data_of_comment).all():
                data_df.loc[comment['user']['login'], ['FirstDataActivity']] = data_of_comment
            if (data_df.loc[comment['user']['login'], ['LastDataActivity']] < data_of_comment).all():
                data_df.loc[comment['user']['login'], ['LastDataActivity']] = data_of_comment

    # Тк множество популярных открытых проектов с удовольствием принимают помощь изве, то очень сложно определить 
    # основную команду или отсеить внешних помощников. Определяем уровень доступа каждого пользователя по типу действий. 
    # 3 - write, maintain, or admin permission. 
    # 2 - triage permission. 
    # 1 - read permission

    # Privileged Events Extended Events Common Events (write, maintain, or admin permission)
    # added_to_project, converted_note_to_issue, deployed, deployment_environment_changed,
    # locked, merged, moved_columns_in_project, pinned, removed_from_project,
    # review_dismissed, transferred, unlocked, unpinned, user_blocked

    # (triage permission)
    # assigned, demilestoned, labeled, marked_as_duplicate, milestoned, unassigned, unlabeled, unmarked_as_duplicate

    # (read permission)
    # automatic_base_change_failed, automatic_base_change_succeeded, base_ref_changed, closed, comment_deleted,
    # commented, committed, connected, convert_to_draft, created, cross_referenced, disconnected, head_ref_deleted,
    # head_ref_force_pushed, head_ref_restored, mentioned, ready_for_review, referenced, referenced_by, renamed, 
    # reopened, review_request_removed, review_requested, reviewed, subscribed, unsubscribed

    write_permission = ['added_to_project', 'converted_note_to_issue', 'deployed', 'deployment_environment_changed', 'locked', 'merged', 'moved_columns_in_project',
    'pinned', 'removed_from_project', 'review_dismissed', 'transferred', 'unlocked', 'unpinned', 'user_blocked']
    triage_permission = ['assigned', 'demilestoned', 'labeled', 'marked_as_duplicate', 'milestoned', 'unassigned', 'unlabeled', 'unmarked_as_duplicate']
    read_permission = ['automatic_base_change_failed', 'automatic_base_change_succeeded', 'base_ref_changed', 'closed', 'comment_deleted',
    'commented', 'committed', 'connected', 'convert_to_draft', 'created', 'cross_referenced', 'disconnected', 'head_ref_deleted', 
    'head_ref_force_pushed', 'head_ref_restored', 'mentioned', 'ready_for_review', 'referenced', 'referenced_by', 'renamed', 'reopened',
    'review_request_removed', 'review_requested', 'reviewed', 'subscribed', 'unsubscribed']

    print("Собираем данные о действиях в issues...")
    with open(f'./data/{username}/issues_events.json', "r", encoding="utf-8") as f:
        events = json.load(f)
    for event in events:
        if event['actor']:
            login = event['actor']['login']
        else: login = ''
        if len(login) != 0 and login in data_df.index:
            data_df.loc[login, ['IssuesEvent']] += 1
            data_of_event = datetime.fromisoformat(event['created_at'])
            if (data_df.loc[login, ['FirstDataActivity']] > data_of_event).all():
                data_df.loc[login, ['FirstDataActivity']] = data_of_event
            if (data_df.loc[login, ['LastDataActivity']] < data_of_event).all():
                data_df.loc[login, ['LastDataActivity']] = data_of_event
            if event['event'] in read_permission and (data_df.loc[login, ['PermissionRole']] < 1).all():
                data_df.loc[login, ['PermissionRole']] = 1
            elif event['event'] in triage_permission and (data_df.loc[login, ['PermissionRole']] < 2).all():
                data_df.loc[login, ['PermissionRole']] = 2
            elif event['event'] in write_permission and (data_df.loc[login, ['PermissionRole']] < 3).all():
                data_df.loc[login, ['PermissionRole']] = 3

    print("Собираем данные об issues...")
    with open(f'./data/{username}/issues.json', "r", encoding="utf-8") as f:
        issues = json.load(f)
    for issue in issues:
        if issue['user']['login'] in data_df.index:
            data_df.loc[issue['user']['login'], ['CreateIssueEvent']] += 1
            data_of_issue = datetime.fromisoformat(issue['updated_at'])
            if (data_df.loc[issue['user']['login'], ['FirstDataActivity']] > data_of_issue).all():
                data_df.loc[issue['user']['login'], ['FirstDataActivity']] = data_of_issue
            if (data_df.loc[issue['user']['login'], ['LastDataActivity']] < data_of_issue).all():
                data_df.loc[issue['user']['login'], ['LastDataActivity']] = data_of_issue

    print("Собираем данные о pull requests...")
    with open(f'./data/{username}/pulls.json', "r", encoding="utf-8") as f:
        pulls = json.load(f)
    for pull in pulls:
        if pull['user']['login'] in data_df.index:
            data_df.loc[pull['user']['login'], ['PullRequestEvent']] += 1
            data_of_pull = datetime.fromisoformat(pull['updated_at'])
            if (data_df.loc[pull['user']['login'], ['FirstDataActivity']] > data_of_pull).all():
                data_df.loc[pull['user']['login'], ['FirstDataActivity']] = data_of_pull
            if (data_df.loc[pull['user']['login'], ['LastDataActivity']] < data_of_pull).all():
                data_df.loc[pull['user']['login'], ['LastDataActivity']] = data_of_pull

    print("Собираем данные о релизах...")
    with open(f'./data/{username}/releases.json', "r", encoding="utf-8") as f:
        releases = json.load(f)
    for release in releases:
        if release['author']['login'] in data_df.index:
            data_df.loc[release['author']['login'], ['ReleaseEvent']] += 1
            data_of_release = datetime.fromisoformat(release['published_at'])
            if (data_df.loc[release['author']['login'], ['FirstDataActivity']] > data_of_release).all():
                data_df.loc[release['author']['login'], ['FirstDataActivity']] = data_of_release
            if (data_df.loc[release['author']['login'], ['LastDataActivity']] < data_of_release).all():
                data_df.loc[release['author']['login'], ['LastDataActivity']] = data_of_release

    # Удаляем неактивных разработчиков. Неактивными являются те, которые не совершили ни одного действия в этом году + отсутствие коммитов + бездействие 
    # за последний месяц. Так же удаляем нулевые столбцы.

    data_df = data_df[(data_df.FirstDataActivity != str(date_today)) & (data_df.LastDataActivity != str(date_start))]
    data_df = data_df[data_df.CommitEvent != 0]
    data_df = data_df[data_df.LastDataActivity >= datetime.fromisoformat('2024-04-23 23:59:59+00:00')]
    # data_df = data_df[data_df.index != "nodejs-github-bot"]
    data_df = data_df.loc[:, (data_df != 0).any(axis=0)]

    print("Сохранение...")
    data_df.to_csv(f'./data/{username}/{repo}.csv', index=True)