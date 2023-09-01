import glob
import sys
import requests
import yaml
import json


if len(sys.argv) != 2:
    print('First parameter must be the absolute path to the folder containing the .json files.')
path = sys.argv[1]


with open(path + '/config.yaml') as config_file:
    grafana_config = yaml.safe_load(config_file)

if 'base_url' not in grafana_config:
    print('Missing base_url in config.yaml')
    exit(1)

base_url = grafana_config['base_url']

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
files = glob.glob(path + '/*.json')
user_counter = 0
for user_path in files:
    with open(user_path) as user_file:
        user_config = json.load(user_file)
        login_name = user_config['login']
        user_exists = session.get(f'{base_url}/api/users/lookup?loginOrEmail={login_name}')
        if user_exists.status_code == 404:
            print(f'User {login_name} does not exist yet - creating')
            creation_response = session.post(f'{base_url}/api/admin/users', json=user_config, headers=headers)
            creation_response_json = json.loads(creation_response.text)
            user_id = creation_response_json['id']
        else:
            user_id = json.loads(user_exists.text)['id']
        user_response = session.get(f'{base_url}/api/users/{user_id}')
        user_response_json = json.loads(user_response.text)
        org_id = user_response_json['orgId']
        org_role = {
            "role": "Editor"
        }
        session.patch(f'{base_url}/api/orgs/{org_id}/users/{user_id}', json=org_role, headers=headers)
        user_counter += 1

print(f'Done deploying {user_counter} users')
