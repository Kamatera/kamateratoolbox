import json
import os
import requests

from .config import SERVER_BASE_URL


def kamatera_api_request(path, ignore_errors=False, **kwargs):
    url = "%s%s" % (SERVER_BASE_URL, path)
    method = kwargs.pop("method", "GET")
    print(url)
    print(method)
    print(kwargs)
    res = requests.request(method=method, url=url, headers={
        "AuthClientId": os.environ["KAMATERA_API_CLIENT_ID"],
        "AuthSecret": os.environ["KAMATERA_API_SECRET"],
        "Content-Type": "application/json",
        "Accept": "application/json"
    }, **kwargs)
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
