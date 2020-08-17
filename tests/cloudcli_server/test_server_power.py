from ..common import cloudcli_server_request, assert_no_matching_servers, wait_command, wait_for_res


def test_server_power_on_no_matching_servers():
    assert_no_matching_servers("/service/server/poweron")


def test_server_power_off_no_matching_servers():
    assert_no_matching_servers("/service/server/poweroff")


def test_server_power_reboot_no_matching_servers():
    assert_no_matching_servers("/service/server/reboot")


def test_server_power(temp_server):
    print("poweroff server")
    res = cloudcli_server_request("/service/server/poweroff", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 1
    wait_command(res[0])
    res = wait_for_res(
        lambda: cloudcli_server_request("/service/server/info", method="POST", json={"name": temp_server["name"]}),
        lambda res: len(res) > 0 and res[0]["power"] == "off"
    )
    assert len(res) == 1
    server_id = res[0]["id"]
    assert res[0]["power"] == "off"
    res = cloudcli_server_request("/service/server/poweron", method="POST", json={
        "id": server_id
    })
    assert len(res) == 1
    wait_command(res[0])
    res = wait_for_res(
        lambda: cloudcli_server_request("/service/server/info", method="POST", json={"id": server_id}),
        lambda res: len(res) > 0 and res[0]["power"] == "on"
    )
    assert len(res) == 1
    assert res[0]["power"] == "on"
    res = cloudcli_server_request("/service/server/reboot", method="POST", json={
        "id": server_id
    })
    assert len(res) == 1
    wait_command(res[0])
    res = wait_for_res(
        lambda: cloudcli_server_request("/service/server/info", method="POST", json={"id": server_id}),
        lambda res: len(res) > 0 and res[0]["power"] == "on"
    )
    assert len(res) == 1
    assert res[0]["power"] == "on"


def test_multiple_servers_power(temp_servers_factory):
    server1 = temp_servers_factory("create")
    server2 = temp_servers_factory("create")
    temp_servers_factory("wait")
    print("Powering off servers")
    res = cloudcli_server_request("/service/server/poweroff", method="POST", json={
        "name": "%s|%s" % (server1["name"], server2["name"])
    })
    assert len(res) == 2
    for command_id in res:
        wait_command(command_id)
    res = wait_for_res(
        lambda: cloudcli_server_request("/service/server/info", method="POST", json={"name": "%s|%s" % (server1["name"], server2["name"])}),
        lambda res: len(res) > 1 and res[0]["power"] == "off" and res[1]["power"] == "off"
    )
    assert len(res) == 2
    assert res[0]["power"] == "off"
    assert res[1]["power"] == "off"
