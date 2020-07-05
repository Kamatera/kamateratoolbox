import pytest
from ..common import cloudcli_server_request, DEFAULT_FIXTURE_SERVER


def test_server_info(session_server_powered_on, session_server_powered_off):
    res = cloudcli_server_request("/service/server/info", method="POST", json={
        "name": "%s|%s" % (session_server_powered_on["name"], session_server_powered_off["name"])
    })
    assert len(res) == 2
    assert set(res[0].keys()) == {"id", "datacenter", "cpu", "name", "ram", "power", "diskSizes", "networks", "billing",
                                  "traffic", "managed", "backup", "priceMonthlyOn", "priceHourlyOn", "priceHourlyOff"}
    server = res[0]
    assert len(server["id"]) > 10
    assert server["datacenter"] == DEFAULT_FIXTURE_SERVER["datacenter"]
    assert server["cpu"] == DEFAULT_FIXTURE_SERVER["cpu"]
    assert server["name"] in [session_server_powered_on["name"], session_server_powered_off["name"]]
    assert int(server["ram"]) == int(DEFAULT_FIXTURE_SERVER["ram"])
    assert server["diskSizes"] == [10]
    assert len(server["networks"]) == 1
    assert server["networks"][0]["network"] == "wan-il"
    assert len(server["networks"][0]["ips"]) == 1
    assert server["billing"] == DEFAULT_FIXTURE_SERVER["billingcycle"]
    assert server["traffic"] == "t5000"
    assert server["managed"] == "0"
    assert server["backup"] == "0"
    assert float(server["priceMonthlyOn"]) > 0.0
    assert float(server["priceHourlyOn"]) > 0.0
    assert float(server["priceHourlyOff"]) > 0.0


def test_server_info_no_servers():
    with pytest.raises(Exception, match="No servers found"):
        cloudcli_server_request("/service/server/info", method="POST", json={
            "name": "__non_existent_server_name__",
        })
    res = cloudcli_server_request("/service/server/info", method="POST", json={
        "name": "__non_existent_server_name__",
        "allow-no-servers": "yes"
    })
    assert len(res) == 0
