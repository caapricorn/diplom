import requests
import json
import pandas as pd
from datetime import datetime
from config import token_api
from languages import extension_to_language
from utils import repo_exist, clean_user_data
import sys

# date_today = datetime.now().isoformat()
date_today = datetime.fromisoformat("2024-05-26T23:59:59Z")
date_start = datetime.fromisoformat("2023-12-31T23:59:59Z")
data_df = []
write_permission = ['added_to_project', 'converted_note_to_issue', 'deployed', 'deployment_environment_changed', 'locked', 'merged', 'moved_columns_in_project',
    'pinned', 'removed_from_project', 'review_dismissed', 'transferred', 'unlocked', 'unpinned', 'user_blocked']
triage_permission = ['assigned', 'demilestoned', 'labeled', 'marked_as_duplicate', 'milestoned', 'unassigned', 'unlabeled', 'unmarked_as_duplicate']
read_permission = ['automatic_base_change_failed', 'automatic_base_change_succeeded', 'base_ref_changed', 'closed', 'comment_deleted',
    'commented', 'committed', 'connected', 'convert_to_draft', 'created', 'cross_referenced', 'disconnected', 'head_ref_deleted', 
    'head_ref_force_pushed', 'head_ref_restored', 'mentioned', 'ready_for_review', 'referenced', 'referenced_by', 'renamed', 'reopened',
    'review_request_removed', 'review_requested', 'reviewed', 'subscribed', 'unsubscribed']

def get_unique_words(row):
        words = row.split(',')
        unique_words = set(words)
        unique_words_list = list(unique_words)
        return unique_words_list

def contributors(data_df, folder_name):
    print("Собираем данные об участниках...")
    index_login = []
    with open(f'./data/{folder_name}/json/contributors.json', "r", encoding="utf-8") as f:
        contributors = json.load(f)
    for contributor in contributors:
        index_login.append(contributor['login'])
        data_df.append({"Contributions": contributor['contributions']})
    data_df = pd.DataFrame(data_df, index=index_login)
    return data_df

def commits(data_df, folder_name):
    print("Собираем данные о коммитах...")
    with open(f'./data/{folder_name}/json/commits.json', "r", encoding="utf-8") as f:
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
            r = requests.get(url_commit, headers={"Authorization": token_api})
            data_json = json.loads(r.text)
            data_df.loc[login, ['Additions']] += data_json['stats']['additions']
            data_df.loc[login, ['Deletions']] += data_json['stats']['deletions']
            if len(data_json['files']) != 0:
                file_of_commit = data_json['files'][0]['filename'].split('.')[-1]
                language = extension_to_language.get(file_of_commit)
                if language is not None:
                    data_df.loc[login, ['Languages']] = data_df.loc[login, ['Languages']] + language[0] + ','
    data_df['Languages'] = data_df['Languages'].apply(get_unique_words)
    return data_df

def commits_comments(data_df, folder_name):
    print("Собираем данные о комментариях в коммитах...")
    with open(f'./data/{folder_name}/json/commits_comments.json', "r", encoding="utf-8") as f:
        comments = json.load(f)
    for comment in comments:
        if comment['user']['login'] in data_df.index:
            data_df.loc[comment['user']['login'], ['CommitCommentEvent']] += 1
            data_of_comment = datetime.fromisoformat(comment['updated_at'])
            if (data_df.loc[comment['user']['login'], ['FirstDataActivity']] > data_of_comment).all():
                data_df.loc[comment['user']['login'], ['FirstDataActivity']] = data_of_comment
            if (data_df.loc[comment['user']['login'], ['LastDataActivity']] < data_of_comment).all():
                data_df.loc[comment['user']['login'], ['LastDataActivity']] = data_of_comment
    return data_df

def events(data_df, folder_name):
    print("Собираем данные о действиях разработчиков...")
    with open(f'./data/{folder_name}/json/events.json', "r", encoding="utf-8") as f:
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
    return data_df

def issues(data_df, folder_name):
    print("Собираем данные об issues...")
    with open(f'./data/{folder_name}/json/issues.json', "r", encoding="utf-8") as f:
        issues = json.load(f)
    for issue in issues:
        if issue['user']['login'] in data_df.index:
            data_df.loc[issue['user']['login'], ['CreateIssueEvent']] += 1
            data_of_issue = datetime.fromisoformat(issue['updated_at'])
            if (data_df.loc[issue['user']['login'], ['FirstDataActivity']] > data_of_issue).all():
                data_df.loc[issue['user']['login'], ['FirstDataActivity']] = data_of_issue
            if (data_df.loc[issue['user']['login'], ['LastDataActivity']] < data_of_issue).all():
                data_df.loc[issue['user']['login'], ['LastDataActivity']] = data_of_issue
    return data_df

def issues_comments(data_df, folder_name):
    print("Собираем данные о комментариях в issues...")
    with open(f'./data/{folder_name}/json/issues_comments.json', "r", encoding="utf-8") as f:
        comments = json.load(f)
    for comment in comments:
        if comment['user']['login'] in data_df.index:
            data_df.loc[comment['user']['login'], ['IssueCommentEvent']] += 1
            data_of_comment = datetime.fromisoformat(comment['updated_at'])
            if (data_df.loc[comment['user']['login'], ['FirstDataActivity']] > data_of_comment).all():
                data_df.loc[comment['user']['login'], ['FirstDataActivity']] = data_of_comment
            if (data_df.loc[comment['user']['login'], ['LastDataActivity']] < data_of_comment).all():
                data_df.loc[comment['user']['login'], ['LastDataActivity']] = data_of_comment
    return data_df

def issues_events(data_df, folder_name):
    print("Собираем данные о действиях в issues...")
    with open(f'./data/{folder_name}/json/issues_events.json', "r", encoding="utf-8") as f:
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
    return data_df

def pulls(data_df, folder_name):
    print("Собираем данные о pull requests...")
    with open(f'./data/{folder_name}/json/pulls.json', "r", encoding="utf-8") as f:
        pulls = json.load(f)
    for pull in pulls:
        if pull['user']['login'] in data_df.index:
            data_df.loc[pull['user']['login'], ['PullRequestEvent']] += 1
            data_of_pull = datetime.fromisoformat(pull['updated_at'])
            if (data_df.loc[pull['user']['login'], ['FirstDataActivity']] > data_of_pull).all():
                data_df.loc[pull['user']['login'], ['FirstDataActivity']] = data_of_pull
            if (data_df.loc[pull['user']['login'], ['LastDataActivity']] < data_of_pull).all():
                data_df.loc[pull['user']['login'], ['LastDataActivity']] = data_of_pull
    return data_df

def releases(data_df, folder_name):
    print("Собираем данные о релизах...")
    with open(f'./data/{folder_name}/json/releases.json', "r", encoding="utf-8") as f:
        releases = json.load(f)
    for release in releases:
        if release['author']['login'] in data_df.index:
            data_df.loc[release['author']['login'], ['ReleaseEvent']] += 1
            data_of_release = datetime.fromisoformat(release['published_at'])
            if (data_df.loc[release['author']['login'], ['FirstDataActivity']] > data_of_release).all():
                data_df.loc[release['author']['login'], ['FirstDataActivity']] = data_of_release
            if (data_df.loc[release['author']['login'], ['LastDataActivity']] < data_of_release).all():
                data_df.loc[release['author']['login'], ['LastDataActivity']] = data_of_release
    return data_df

def collect(username, repo):
    url = f'https://api.github.com/repos/{username}/{repo}'
    folder_name = f'{username}-{repo}'

    if not repo_exist(url):
        sys.exit(0)

    clean_user_data(f'./data/{folder_name}/csv')
    data_df = []
    data_df = contributors(data_df, folder_name)

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

    data_df = commits(data_df, folder_name)

    data_df = commits_comments(data_df, folder_name)

    data_df = events(data_df, folder_name)

    data_df = issues(data_df, folder_name)

    data_df = issues_comments(data_df, folder_name)

    data_df = issues_events(data_df, folder_name)

    data_df = pulls(data_df, folder_name)

    data_df = releases(data_df, folder_name)

    data_df = data_df[(data_df.FirstDataActivity != str(date_today)) & (data_df.LastDataActivity != str(date_start))]
    data_df = data_df[data_df.CommitEvent != 0]
    data_df = data_df[data_df.LastDataActivity >= datetime.fromisoformat('2024-04-23 23:59:59+00:00')]
    data_df = data_df.loc[:, (data_df != 0).any(axis=0)]

    data_df['Add-Del'] = (data_df['Additions'] - data_df['Deletions'])
    data_df = data_df.drop(['Additions', 'Deletions'], axis=1)

    print("Сохранение...")
    data_df.to_csv(f'./data/{folder_name}/csv/data.csv', index=True)