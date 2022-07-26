from ..common import cloudcli_server_request, assert_str_int

import json


def assert_create_network(test_network):
    create_network_response = cloudcli_server_request("/service/network/create", method="POST", json={
        'datacenter': test_network['datacenter'],
        'name': test_network['network_name'],
        'subnetIp': test_network['subnetIp'],
        'subnetBit': test_network['subnetBit'],
        'gateway': test_network['gateway'],
        'dns1': test_network['dns1'],
        'dns2': test_network['dns2'],
        'subnetDescription': test_network['subnetDescription']
    })
    assert set(create_network_response.keys()) == {'message', 'res'}
    assert create_network_response['message'] == 'Network created successfully'
    assert_str_int(json.loads(create_network_response['res'])['networkId'])
    assert_str_int(json.loads(create_network_response['res'])['subnetId'])
    status_code, res = cloudcli_server_request("/service/network/create", method="POST", ignore_errors=True, json={
        'datacenter': test_network['datacenter'],
        'name': test_network['network_name'],
        'subnetIp': test_network['subnetIp'],
        'subnetBit': test_network['subnetBit'],
        'gateway': test_network['gateway'],
        'dns1': test_network['dns1'],
        'dns2': test_network['dns2'],
        'subnetDescription': test_network['subnetDescription']
    })
    assert status_code == 500
    assert set(res.keys()) == {'message'}
    assert json.loads(res['message']) == {
        'errors': [{'code': 115, 'info': 'error occurred', 'category': 'General Error'}]
    }


def assert_list_networks(test_network):
    networks = cloudcli_server_request(f"/service/networks?datacenter={test_network['datacenter']}")
    network = [network for network in networks if network['names'][0].endswith(test_network['network_name'])][0]
    assert network['datacenter'] == test_network['datacenter']
    assert len(network['ids']) == 1
    network_id = assert_str_int(network['ids'][0])
    assert len(network['names']) == 1
    lan, number, *name = network['names'][0].split('-')
    assert lan == 'lan'
    assert_str_int(number)
    assert '-'.join(name) == test_network['network_name']
    vlan_id = assert_str_int(network['vlanId'])
    return network_id, vlan_id


def assert_delete_network_with_subnets(test_network):
    status_code, res = cloudcli_server_request(
        "/service/network/delete", method="POST", ignore_errors=True, json={
            'datacenter': test_network['datacenter'],
            'id': test_network['network_id'],
        }
    )
    assert status_code == 500
    assert set(res.keys()) == {'message'}
    assert json.loads(res['message']) == {
        'errors': [{'code': 20, 'info': 'error occurred', 'category': 'General Error'}]
    }


def assert_list_subnets(test_network):
    subnets = cloudcli_server_request(
        f"/service/network/subnets?datacenter={test_network['datacenter']}&vlanId={test_network['vlan_id']}"
    )
    assert len(subnets) == 1
    subnet = subnets[0]
    assert subnet['dns1'] == test_network['dns1']
    assert subnet['dns2'] == test_network['dns2']
    assert subnet['endRange'] == test_network['endRange']
    assert subnet['gateway'] == test_network['gateway']
    assert assert_str_int(subnet['inUse']) in [0, 1]
    assert subnet['startRange'] == test_network['startRange']
    assert assert_str_int(subnet['subnetBit']) == int(test_network['subnetBit'])
    assert subnet['subnetDescription'] == test_network['subnetDescription']
    subnet_id = assert_str_int(subnet['subnetId'])
    assert subnet['subnetIp'] == test_network['subnetIp']
    assert subnet['subnetMask'] == test_network['subnetMask']
    assert assert_str_int(subnet['total']) == test_network['totalIps']
    return subnet_id


def assert_create_subnet2(test_network):
    create_subnet2_res = cloudcli_server_request(
        '/service/network/subnet/create',
        method='POST',
        json={
            'datacenter': test_network['datacenter'],
            'vlanId': test_network['vlan_id'],
            'subnetIp': test_network['subnet2']['subnetIp'],
            'subnetBit': test_network['subnet2']['subnetBit'],
            'gateway': test_network['subnet2']['gateway'],
            'dns1': test_network['subnet2']['dns1'],
            'dns2': test_network['subnet2']['dns2'],
            'subnetDescription': test_network['subnet2']['subnetDescription']
        }
    )
    assert set(create_subnet2_res.keys()) == {'message', 'res'}
    assert create_subnet2_res['message'] == 'Subnet created successfully'
    assert_str_int(json.loads(create_subnet2_res['res'])['subnetId'])
    status_code, res = cloudcli_server_request(
        '/service/network/subnet/create',
        method='POST',
        ignore_errors=True,
        json={
            'datacenter': test_network['datacenter'],
            'vlanId': test_network['vlan_id'],
            'subnetIp': test_network['subnet2']['subnetIp'],
            'subnetBit': test_network['subnet2']['subnetBit'],
            'gateway': test_network['subnet2']['gateway'],
            'dns1': test_network['subnet2']['dns1'],
            'dns2': test_network['subnet2']['dns2'],
            'subnetDescription': test_network['subnet2']['subnetDescription']
        }
    )
    assert status_code == 500
    assert set(res.keys()) == {'message'}
    assert json.loads(res['message']) == {
        'errors': [{'code': 102, 'info': 'error occurred', 'category': 'General Error'}]
    }


def assert_list_subnets2(test_network):
    subnets = cloudcli_server_request(
        f"/service/network/subnets?datacenter={test_network['datacenter']}&vlanId={test_network['vlan_id']}"
    )
    assert len(subnets) == 2
    got_subnet1, got_subnet2, subnet1_id, subnet2_id = False, False, None, None
    for subnet in subnets:
        if subnet['subnetDescription'] == test_network['subnet2']['subnetDescription']:
            assert not got_subnet2
            got_subnet2 = True
            assert subnet['subnetIp'] == test_network['subnet2']['subnetIp']
            subnet2_id = assert_str_int(subnet['subnetId'])
        elif subnet['subnetDescription'] == test_network['subnetDescription']:
            assert not got_subnet1
            got_subnet1 = True
            assert subnet['subnetIp'] == test_network['subnetIp']
            subnet1_id = assert_str_int(subnet['subnetId'])
        else:
            raise Exception("Invalid subnet: {}".format(subnet))
    assert got_subnet1 and got_subnet2
    return subnet1_id, subnet2_id


def assert_edit_subnet(test_network, gateway):
    res = cloudcli_server_request(
        '/service/network/subnet/edit',
        method='POST',
        json={
            'datacenter': test_network['datacenter'],
            'vlanId': test_network['vlan_id'],
            'subnetId': test_network['subnet_id'],
            'subnetIp': test_network['subnetIp'],
            'subnetBit': test_network['subnetBit'],
            'gateway': gateway,
            'dns1': test_network['dns1'],
            'dns2': test_network['dns2'],
            'subnetDescription': test_network['subnetDescription']
        }
    )
    assert set(res.keys()) == {'message', 'res'}
    assert res['message'] == 'Subnet updated successfully'
    res = json.loads(res['res'])
    assert set(res.keys()) == {'subnetId', 'subnetIp', 'subnetBit', 'subnetMask', 'gateway',
                               'gateway', 'startRange', 'endRange', 'inUse', 'total', 'edit',
                               'dns1', 'dns2', 'subnetDescription'}
    assert_str_int(res['subnetId'])


def assert_subnet_gateway(test_network, subnetDescription, gateway):
    for subnet in cloudcli_server_request(
        f"/service/network/subnets?datacenter={test_network['datacenter']}&vlanId={test_network['vlan_id']}"
    ):
        if subnet['subnetDescription'] == subnetDescription:
            assert subnet['gateway'] == gateway
            return
    raise Exception("Did not find subnet")


def assert_delete_subnet(subnet_id):
    assert cloudcli_server_request(
        '/service/network/subnet/delete', method='POST', json={'subnetId': subnet_id}
    ) == {'message': 'Subnet deleted successfully', 'res': '[]'}
    status_code, res = cloudcli_server_request(
        '/service/network/subnet/delete', method='POST', json={'subnetId': subnet_id},
        ignore_errors=True
    )
    assert status_code == 500
    assert set(res.keys()) == {'message'}
    assert json.loads(res['message']) == {
        'errors': [{'code': 1, 'info': 'Forbidden', 'category': 'General Error'}]
    }


def assert_delete_network(test_network):
    assert cloudcli_server_request(
        '/service/network/delete', method='POST', json={
            'datacenter': test_network['datacenter'],
            'id': test_network['network_id']
        }
    ) == {'message': 'Network deleted successfully', 'res': '[]'}
    status_code, res = cloudcli_server_request(
        '/service/network/delete', method='POST', json={
            'datacenter': test_network['datacenter'],
            'id': test_network['network_id']
        },
        ignore_errors=True
    )
    assert status_code == 500
    assert set(res.keys()) == {'message'}
    assert json.loads(res['message']) == {
        'errors': [{'code': 11, 'info': 'Network not found.', 'category': 'Network Error'}]
    }


def test_networks():
    test_network = dict(
        datacenter='IL-TA',
        network_name='ktbk-test-networks',
        gateway='172.16.0.100',
        dns1='1.2.3.4',
        dns2='1.2.3.4',
        subnetDescription='testing 1 2 3',
        subnetBit='23',
        subnetIp='172.16.0.0',
        startRange='172.16.0.1',
        endRange='172.16.1.254',
        subnetMask='255.255.254.0',
        totalIps=510
    )
    assert_create_network(test_network)
    test_network['network_id'], test_network['vlan_id'] = assert_list_networks(test_network)
    assert_delete_network_with_subnets(test_network)
    test_network['subnet_id'] = assert_list_subnets(test_network)
    test_network['subnet2'] = dict(
        gateway='192.168.0.1',
        dns1='6.6.6.6',
        dns2='7.7.7.7',
        subnetDescription='2nd subnet',
        subnetBit='26',
        subnetIp='192.168.0.0',
    )
    assert_create_subnet2(test_network)
    test_network['subnet_id'], test_network['subnet2']['subnet_id'] = assert_list_subnets2(test_network)
    assert_edit_subnet(test_network, '172.16.0.2')
    assert_subnet_gateway(test_network, test_network['subnetDescription'], '172.16.0.2')
    assert_delete_subnet(test_network['subnet_id'])
    assert_delete_subnet(test_network['subnet2']['subnet_id'])
    assert_delete_network(test_network)
