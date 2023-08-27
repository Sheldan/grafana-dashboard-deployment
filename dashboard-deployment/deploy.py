import glob
import json
import sys
import requests
import yaml


if len(sys.argv) != 2:
    print('First parameter must be the absolute path to the folder containing the .json files.')
path = sys.argv[1]


with open(path + '/config.yaml') as config_file:
    grafana_config = yaml.safe_load(config_file)

if 'base_url' not in grafana_config:
    print('Missing base_url in config.yaml')
    exit(1)

base_url = grafana_config['base_url']

folder_name = None

if 'folder_name' in grafana_config:
    folder_name = grafana_config['folder_name']

use_auth = False
if 'username' in grafana_config and 'password' in grafana_config:
    use_auth = True
    user_name = grafana_config['username']
    password = grafana_config['password']
    print(f'Using basic auth.')

print(f'Using grafana at {base_url}')
session = requests.Session()
if use_auth:
    session.auth = (user_name, password)

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

folder_id = None
if folder_name is not None:
    existing_folders_str = session.get(f'{base_url}/api/folders', headers=headers)
    existing_folders = json.loads(existing_folders_str.text)
    for existing_folder in existing_folders:
        if existing_folder['title'] == folder_name:
            folder_id = existing_folder['id']

if folder_id is None and folder_name is not None:
    folder_config = {
        "title": folder_name
    }
    folder_response_str = session.post(f'{base_url}/api/folders', json=folder_config, headers=headers)
    folder_id = json.loads(folder_response_str.text)['id']
files = glob.glob(path + '/*.json')
dashboard_counter = 0
for dashboard in files:
    with open(dashboard) as dashboard_file:
        dashboard_config = json.loads(dashboard_file.read())
        if folder_id is not None:
            dashboard_config['folderId'] = folder_id
        response = session.post(f'{base_url}/api/dashboards/db', json=dashboard_config, headers=headers)
        if response.status_code != 200:
            print(f'Failed to update/create dashboard - {response.status_code} - body "{response.text}"')
            exit(1)
        print(f'Uploaded {dashboard} json.')
        dashboard_counter += 1

print(f'Done deploying {dashboard_counter}')