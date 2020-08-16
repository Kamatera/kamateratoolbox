def _test_server_attach(attach_args, cloudcli_pexpect):
    child = cloudcli_pexpect('server', *attach_args)
    child.sendline("pwd")
    child.expect("/root")
    child.sendline("uname -ops")
    child.expect("Linux x86_64 GNU/Linux")
    child.sendline("echo test123 > foo")
    child.kill(0)
    child = cloudcli_pexpect('server', *attach_args)
    child.sendline("cat foo")
    child.expect("test123")
    child.kill(0)


def test_server_attach(cloudcli_pexpect, session_server_powered_on):
    args = ['--name', session_server_powered_on["name"], '--password', session_server_powered_on["password"]]
    _test_server_attach(['attach', *args], cloudcli_pexpect)
    _test_server_attach(['connect', *args], cloudcli_pexpect)
    _test_server_attach(['ssh', *args], cloudcli_pexpect)


def test_server_sshkey_attach(cloudcli_pexpect, session_server_sshkey):
    args = ['--name', session_server_sshkey["name"], '--key', session_server_sshkey["private_sshkey_path"]]
    _test_server_attach(['attach', *args], cloudcli_pexpect)
    _test_server_attach(['connect', *args], cloudcli_pexpect)
    _test_server_attach(['ssh', *args], cloudcli_pexpect)
