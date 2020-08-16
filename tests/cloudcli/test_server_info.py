import pytest
from ..common import DEFAULT_FIXTURE_SERVER


def assert_server_info(res, session_server_powered_on, session_server_powered_off=None):
    assert len(res) == (2 if session_server_powered_off else 1)
    assert set(res[0].keys()) == {"id", "datacenter", "cpu", "name", "ram", "power", "diskSizes", "networks", "billing",
                                  "traffic", "managed", "backup", "priceMonthlyOn", "priceHourlyOn", "priceHourlyOff"}
    server = res[0]
    assert len(server["id"]) > 10
    assert server["datacenter"] == DEFAULT_FIXTURE_SERVER["datacenter"]
    assert server["cpu"] == DEFAULT_FIXTURE_SERVER["cpu"]
    if session_server_powered_off:
        assert server["name"] in [session_server_powered_on["name"], session_server_powered_off["name"]]
    else:
        assert server["name"] == session_server_powered_on["name"]
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


def get_server_id_cloudcli(cloudcli, server):
    res = cloudcli("server", "info", "--name", server["name"], parse=True)
    assert len(res) == 1
    return res[0]["id"]


def test_server_info(cloudcli, session_server_powered_on, session_server_powered_off):
    assert_server_info(
        cloudcli("server", "info", "--name", "%s|%s" % (session_server_powered_on["name"], session_server_powered_off["name"]), "--format", "json"),
        session_server_powered_on, session_server_powered_off
    )
    assert_server_info(
        cloudcli("server", "info", "--name", "%s|%s" % (session_server_powered_on["name"], session_server_powered_off["name"]), "--format", "yaml"),
        session_server_powered_on, session_server_powered_off
    )


def test_server_info_by_id(cloudcli, session_server_powered_on):
    assert_server_info(
        cloudcli("server", "info", "--id", get_server_id_cloudcli(cloudcli, session_server_powered_on), "--format", "json"),
        session_server_powered_on
    )
    assert_server_info(
        cloudcli("server", "info", "--id", get_server_id_cloudcli(cloudcli, session_server_powered_on), "--format", "yaml"),
        session_server_powered_on
    )


def test_server_info_no_servers(cloudcli):
    with pytest.raises(Exception, match="No servers found"):
        cloudcli("server", "info", "--name", "__non_existent_server_name__")
