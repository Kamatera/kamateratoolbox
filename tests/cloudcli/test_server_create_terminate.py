import os
import paramiko
from ..common import cloudcli_server_request, get_server_name


def test_server_create_terminate_sshkey_tags_script_userdata(cloudcli):
    name = get_server_name()
    print("Creating server with sshkey %s" % name)
    with open(os.environ["TESTING_SSHKEY_PATH"] + ".pub") as f:
        sshkey = f.read()
    try:
        cloudcli(
            "server", "create",
            "--name", name,
            "--password", "",
            "--ssh-key", sshkey,
            "--datacenter", "IL",
            "--image", "ubuntu_server_18.04_64-bit",
            "--cpu", "1A",
            "--ram", "1024",
            "--disk", "size=10",
            "--dailybackup", "no",
            "--managed", "no",
            "--network", "name=wan,ip=auto",
            "--quantity", 1,
            "--billingcycle", "hourly",
            "--monthlypackage", "",
            "--poweronaftercreate", "yes",
            "--script-file", "echo hello script file > /root/test.txt",
            "--userdata-file", "hello user data",
            "--tag", "foo bar",
            "--wait"
        )
        res = cloudcli_server_request("/service/server/ssh", method="POST", json={
            "name": name
        })
        assert len(res) == 1
        server_external_ip = res[0]["externalIp"]
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(server_external_ip, username="root", key_filename=os.environ["TESTING_SSHKEY_PATH"])
        assert ssh_client.exec_command("pwd")[1].read() == b'/root\n'
        assert ssh_client.exec_command("cat test.txt")[1].read() == b'hello script file\n'
        cloudcli("server", "terminate", "--name", name, "--force", "--wait")
    except Exception:
        try:
            cloudcli("server", "terminate", "--name", name, "--force", "--wait")
        except Exception:
            pass
        raise
