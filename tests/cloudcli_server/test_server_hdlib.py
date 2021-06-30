import secrets
from ..common import cloudcli_server_request, assert_only_one_server, assert_no_matching_servers, wait_command


def test_server_hdlib_only_one_server(session_server_powered_on, session_server_powered_off):
    assert_only_one_server([session_server_powered_on, session_server_powered_off], "/server/hdlib")


def test_server_hdlib_no_matching_servers():
    assert_no_matching_servers("/server/hdlib")


def test_server_hdlib(temp_server):
    # list the hard disks available for cloning on the temp server
    res = cloudcli_server_request("/server/hdlib", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 1
    # get the first hard disk uuid
    hduuid = res[0]['uuid']
    assert len(hduuid) > 10
    # power off the server
    res = cloudcli_server_request("/service/server/poweroff", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 1
    wait_command(res[0])
    # create the snapshot
    res = cloudcli_server_request("/server/hdlib", method="POST", json={
        "name": temp_server["name"],
        "clone": hduuid,
        "image_name": "clone_of_".format(temp_server["name"])
    })
    wait_command(res)
