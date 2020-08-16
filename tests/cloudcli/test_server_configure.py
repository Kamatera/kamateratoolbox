import pytest


def test_server_configure_errors(cloudcli, session_server_powered_on, session_server_powered_off):
    with pytest.raises(Exception, match="Please choose a configuration flag"):
        cloudcli(
            "server", "configure",
            "--name", "__non_existent_server__"
        )
    with pytest.raises(Exception, match="--name flag did not match any servers"):
        cloudcli(
            "server", "configure",
            "--name", "__non_existent_server__", "--cpu", "AA"
        )
    with pytest.raises(Exception, match="Please choose only 1 configuration flag at a time"):
        cloudcli(
            "server", "configure",
            "--name", "__non_existent_server__", "--cpu", "AA", "--ram", "BB"
        )
    with pytest.raises(Exception, match="Please choose --id or --name flags"):
        cloudcli(
            "server", "configure",
            "--name", "__non_existent_server__", "--id", "__non_existent_server_id__", "--cpu", "AA"
        )
    with pytest.raises(Exception, match="--name flag must match a single server"):
        cloudcli(
            "server", "configure",
            "--name", "%s|%s" % (session_server_powered_on["name"], session_server_powered_off["name"]), "--cpu", "AA"
        )


def test_server_configure(cloudcli, temp_server):
    print("Configuring server CPU")
    res = cloudcli("server", "info", "--name", temp_server["name"], "--format", "json")
    assert len(res) == 1
    assert res[0]["cpu"] == "1A"
    cloudcli("server", "configure", "--name", temp_server["name"], "--cpu", "2A", "--wait")
    res = cloudcli("server", "info", "--name", temp_server["name"], "--format", "json")
    assert len(res) == 1
    assert res[0]["cpu"] == "2A"
    print("Configuring server RAM")
    assert res[0]["ram"] == 1024
    cloudcli("server", "configure", "--name", temp_server["name"], "--ram", "2048", "--wait")
    res = cloudcli("server", "info", "--name", temp_server["name"], "--format", "json")
    assert len(res) == 1
    assert res[0]["ram"] == 2048
    print("Configuring server dailybackup")
    assert res[0]["backup"] == "0"
    cloudcli("server", "configure", "--name", temp_server["name"], "--dailybackup", "yes", "--wait")
    res = cloudcli("server", "info", "--name", temp_server["name"], "--format", "json")
    assert len(res) == 1
    assert res[0]["backup"] == "1"
    print("Configuring server managed")
    assert res[0]["managed"] == "0"
    cloudcli("server", "configure", "--name", temp_server["name"], "--managed", "yes", "--wait")
    res = cloudcli("server", "info", "--name", temp_server["name"], "--format", "json")
    assert len(res) == 1
    assert res[0]["managed"] == "1"
    print("Configuring server billingcycle")
    assert res[0]["billing"] == "hourly"
    cloudcli("server", "configure", "--name", temp_server["name"], "--billingcycle", "monthly", "--monthlypackage", "t5000", "--wait")
    res = cloudcli("server", "info", "--name", temp_server["name"], "--format", "json")
    assert len(res) == 1
    assert res[0]["billing"] == "monthly"
