import os
import sys
from flask import Flask, render_template, request, jsonify, redirect, send_from_directory
from celery import Celery
from tabulate import tabulate
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../core')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))

from find_png_images import find_png_images
from check_folder_and_get_last_modified_date import check_folder_and_get_last_modified_date
from parse_json import parse
from collect_data import collect
from analyse_data import analyse

app = Flask(__name__)

STATIC_DIR = os.path.abspath('.')

print(STATIC_DIR)

# Настройка Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/image')
def serve_static():
    print(request.args.get('path')[1::])
    return send_from_directory(STATIC_DIR, request.args.get('path')[1::])

@celery.task(name="run.parse_job", bind="True")
def parse_job(self, username, repo):
    def changeState(str):
        self.update_state(state='PENDING', meta=str)
        print(str)
    parse(username, repo, changeState)
    return f"Загрузка данных прошла успешно!"

@celery.task(name="run.collect_job", bind="True")
def collect_job(self, username, repo):
    def changeState(str):
        self.update_state(state='PENDING', meta=str)
        print(str)
    collect(username, repo, changeState)
    return f"Обработка данных прошла успешно!"

@celery.task(name="run.analyse_job", bind="True")
def analyse_job(self, username, repo):
    def changeState(str):
        self.update_state(state='PENDING', meta=str)
        print(str)
    changeState('Создание изображений...')
    analyse(username, repo)
    return f"Обработка данных прошла успешно!"

@app.route('/status_job', methods=['GET'])
def start_task():
    owner = request.args.get('owner')
    repo = request.args.get('repo')
    action = request.args.get('action')

    if action == 'status':
        return redirect(f'/current_status/{owner}/{repo}')
    if action == 'load':
        task = parse_job.apply_async(args=[owner, repo])
        return render_template('status.html', state=task.state, result=task.result, id=task.id, repo=repo, owner=owner, type='Загрузка данных')
    
    if action == 'parse':
        task = collect_job.apply_async(args=[owner, repo])
        return render_template('status.html', state=task.state, result=task.result, id=task.id, repo=repo, owner=owner, type='Обработка данных')
    
    if action == 'image':
        task = analyse_job.apply_async(args=[owner, repo])
        return render_template('status.html', state=task.state, result=task.result, id=task.id, repo=repo, owner=owner, type='Генерация изображений')

@app.route('/status_job/<task_id>', methods=['GET'])
def check_task(task_id):
    task = parse_job.AsyncResult(task_id)
    return jsonify({
        'state': task.state,
        'result': task.result,
    })

@app.route('/current_status/<owner>/<repo>', methods=['GET'])
def current_status(owner, repo):
    path = f'./data/{owner}-{repo}'
    isLoaded, loaded_time = check_folder_and_get_last_modified_date(f'{path}/json')
    isParsed, parsed_time = check_folder_and_get_last_modified_date(f'{path}/csv')
    isImage, imaged_time = check_folder_and_get_last_modified_date(f'{path}/web')

    csvs = {}
    images = {}
    if isImage:
        images = find_png_images(f'{path}/web')
        csvs = find_png_images(f'{path}/web', '.csv')
    
    csv_html = {}
    for csv in csvs:
        data = pd.read_csv(f'.{csvs[csv][0]}')
        table_data = data.values.tolist()
        html_table = tabulate(table_data, headers=data.columns, tablefmt='html')
        csv_html[csv] = html_table
        print(html_table)


    return render_template('info.html', owner=owner, repo=repo, isLoaded=isLoaded, loaded_time=loaded_time, isParsed=isParsed, parsed_time=parsed_time, isImage=isImage, imaged_time=imaged_time, images=images, csv_html=csv_html) 


if __name__ == '__main__':
    app.run(debug=True)