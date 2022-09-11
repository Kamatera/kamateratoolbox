import datetime

from .common import kamatera_api_request, get_server_id_by_name


STAT_CATEGORIES = {
    'network': {'lanTr', 'netRc0', 'lanRc', 'netTotal0', 'netTrTotal', 'netRcTotal', 'netTr0', 'wanRc', 'wanTr'},
    'ram': {'ram'},
    'cpu': {'cpuAvg', 'cpu0'},
    'disksIops': {'diskWrite0', 'diskWriteTotal',
                  'diskReadTotal', 'diskRead0', 'diskCmdTotal', 'diskCmd0'},
    'disksTransfer': {'diskWriteMB0', 'diskReadMB0', 'diskWriteMBTotal', 'diskReadMBTotal'},
}


def assert_stat_series_data(name, data):
    for ts, value in data:
        dt = datetime.datetime.fromtimestamp(ts / 1000)
        assert (datetime.datetime.utcnow() - datetime.timedelta(days=2)) <= dt <= (
                    datetime.datetime.utcnow() + datetime.timedelta(
                days=2)), f"invalid timestamp: {name} {ts} {value}"
        assert isinstance(value, (float, int)), f"invalid value: {name} {ts} {value}"


def test(session_server_powered_on):
    server_id = get_server_id_by_name(session_server_powered_on["name"])
    dt_from = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S") + '.000Z'
    dt_to = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") + '.000Z'
    print(f'from: {dt_from}, to: {dt_to}')
    for category, stat_names in STAT_CATEGORIES.items():
        series = {}
        for data in kamatera_api_request(f'/svc/server/{server_id}/statistics?category={category}&dtFrom={dt_from}&dtTo={dt_to}'):
            if data['series'] == 'interval':
                assert data == {'series': 'interval', 'data': 1}
            else:
                assert data['series'] not in series
                series[data['series']] = data['data']
        assert set(series.keys()) == stat_names
        for name, data in series.items():
            assert_stat_series_data(name, data)
