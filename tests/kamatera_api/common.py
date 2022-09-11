import os
import json

import requests

from .config import SERVER_BASE_URL, KAMATERA_API_DEBUG


def kamatera_api_request(path, ignore_errors=False, **kwargs):
    url = "%s%s" % (SERVER_BASE_URL, path)
    method = kwargs.pop("method", "GET")
    headers = {
        "AuthClientId": os.environ["KAMATERA_API_CLIENT_ID"],
        "AuthSecret": os.environ["KAMATERA_API_SECRET"],
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    if KAMATERA_API_DEBUG:
        print(f'requests kwargs: {json.dumps(kwargs)}')
        print(f'headers: {json.dumps(headers)}')
        print(f'{method} {url}')
    res = requests.request(method=method, url=url, headers=headers, **kwargs)
    if KAMATERA_API_DEBUG:
        print(res.text)
    try:
        if res.text:
            res_json = res.json()
        else:
            res_json = {}
    except json.JSONDecodeError:
        raise Exception("Failed to parse response: {}".format(res.text))
    if ignore_errors:
        return res.status_code, res_json
    elif res.status_code != 200:
        raise Exception(res_json)
    else:
        return res_json


def assert_str_int(val):
    assert str(int(val)) == str(val)
    return int(val)


def get_server_id_by_name(name):
    for server in kamatera_api_request("/service/servers"):
        if server["name"] == name:
            return server["id"]
    raise Exception(f"Server not found: {name}")
