from parse_json import parse
from collect_data import collect
from analyse_data import analyse
from dateutil.relativedelta import relativedelta
from datetime import datetime

username = input("Enter username organization: ")
repo = input("Enter name of repository: ")
print("Choose:")
print("1 -- Download data from this repository")
print("2 -- Collect data from this repository")
print("3 -- Analyse data from this repository")
active = input("Number mode: ")

current_date = datetime.now()
future_date = current_date - relativedelta(months=3)
iso_date_limit = future_date.isoformat(timespec='seconds') + "Z"
is_date_limit = datetime.fromisoformat(iso_date_limit)

match active:
    case '1':
        parse(username, repo, is_date_limit)
    case '2':
        collect(username, repo)
    case '3':
        analyse(username, repo)
