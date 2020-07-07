import pytest


def test_server_options_without_options_should_fail(cloudcli):
    with pytest.raises(Exception, match="Not implemented yet, please choose an option"):
        cloudcli("server", "options")


def test_server_options(cloudcli):
    for option in ["billing", "cpu", "datacenter", "disk", "image", "network", "traffic"]:
        cloudcli("server", "options", "--cache", "--%s" % option)
        cloudcli("server", "options", "--cache", "--%s" % option, "--format", "json")
        cloudcli("server", "options", "--cache", "--%s" % option, "--format", "yaml")
