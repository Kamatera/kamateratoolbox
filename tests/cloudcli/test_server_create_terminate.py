from ..common import get_server_name, get_server_password


def test_server_create(cloudcli):
    name = get_server_name()
    password = get_server_password()
    try:
        cloudcli("server", "create", "--image", "ubuntu_server_18.04_64-bit", "--datacenter", "IL", "--name", name, "--password", password, "--wait")
        cloudcli("server", "terminate", "--force", "--name", name)
    except Exception:
        cloudcli("server", "terminate", "--force", "--name", name)
        raise
