from ..common import cloudcli_server_request


def test_server_options(test_network):
    res = cloudcli_server_request("/service/server")
    assert set(res.keys()) == {"billing", "cpu", "datacenters", "disk", "diskImages", "networks", "ram", "traffic"}
    assert set(res["billing"]) == {"monthly", "hourly"}
    assert len(res["cpu"]) > 5
    assert "2B" in res["cpu"]
    assert "IL" in res["datacenters"]
    assert res["datacenters"]["IL"] == "IL: Israel"
    assert len(res["disk"]) > 5
    assert 20 in res["disk"]
    assert len(res["diskImages"]) == len(res["datacenters"])
    assert len(res["diskImages"]["IL"]) > 5
    assert set(res["diskImages"]["IL"][0]) == {"description", "id", "sizeGB", "usageInfo", "guestDescription", "freeTextOne", "freeTextTwo", "additionalDisks"}
    assert len(res["networks"]) == len(res["datacenters"])
    networks = [network for network in res["networks"]["IL"] if network["name"] == test_network["name"]]
    assert len(networks) == 1
    network = networks[0]
    assert set(network.keys()) == {"name", "ips"}
    assert len(network["ips"]) > 0
