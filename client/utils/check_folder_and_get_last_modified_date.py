import os
from datetime import datetime

def check_folder_and_get_last_modified_date(folder_path):
    if not os.path.isdir(folder_path):
        return False, None
    
    items = os.listdir(folder_path)
    
    if not items:
        return False, None
    
    latest_mod_time = 0
    for item in items:
        item_path = os.path.join(folder_path, item)
        item_mod_time = os.path.getmtime(item_path)
        if item_mod_time > latest_mod_time:
            latest_mod_time = item_mod_time
    
    latest_mod_datetime = datetime.fromtimestamp(latest_mod_time)
    
    return True, latest_mod_datetime