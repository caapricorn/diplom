from parse_json import parse
from collect_data import collect
from analyse_data import analyse

username = input("Enter username organization: ")
repo = input("Enter name of repository: ")
print("Choose:")
print("1 -- Download data from this repository")
print("2 -- Collect data from this repository")
print("3 -- Analyse data from this repository")
active = input("Number mode: ")

match active:
    case '1':
        parse(username, repo)
    case '2':
        collect(username, repo)
    case '3':
        analyse(username, repo)
