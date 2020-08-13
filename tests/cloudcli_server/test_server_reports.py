from ..common import cloudcli_server_request, assert_only_one_server, assert_no_matching_servers


def test_server_reports_only_one_server(session_server_powered_on, session_server_powered_off):
    assert_only_one_server([session_server_powered_on, session_server_powered_off], "/server/report")


def test_server_reports_no_matching_servers():
    assert_no_matching_servers("/server/report")


def test_server_reports(session_server_powered_on):
    res = cloudcli_server_request("/server/report", method="POST", json={
        "name": session_server_powered_on["name"]
    })
    assert len(res) > 0
    assert set(res[0].keys()) == {"year", "month", "cpu", "ram", "disk", "diskTraffic", "wanRcTraffic", "wanTrTraffic", "wanRcPer", "wanTrPer", "lanRcTraffic", "lanTrTraffic", "lanRcPer", "lanTrPer"}
