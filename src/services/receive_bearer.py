import json
import requests
from src.core.config import NIFI_IP, NIFI_USER, NIFI_PASSWORD
import urllib.parse


def get_bearer_token():
    headers = {
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': '*/*',
    }

    data = f'username={NIFI_IP}&password={urllib.parse.quote(NIFI_PASSWORD, safe="")}'

    response = requests.post(f'{NIFI_IP}/nifi-api/access/token', headers=headers, data=data, verify=False)
    return f"Bearer {response.text}"


def check_connection():
    headers = {
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': '*/*',
    }

    data = f'username={NIFI_USER}&password={urllib.parse.quote(NIFI_PASSWORD, safe="")}'

    response = requests.post(f'{NIFI_IP}/nifi-api/access/token', headers=headers,
                             data=data, verify=False)

    return response.ok


def get_root_canvas_id(token):
    headers = {
        'Content-Type': 'application/json',
        'Accept': '*/*'
    }
    headers["Authorization"] = token

    data = f'username={NIFI_USER}&password={urllib.parse.quote(NIFI_PASSWORD, safe="")}'

    response = requests.get(f'{NIFI_IP}/nifi-api/flow/process-groups/root', headers=headers,
                            data=data, verify=False)
    root = json.loads(response.text)
    root_canvas_id = root["processGroupFlow"]["id"]

    return root_canvas_id