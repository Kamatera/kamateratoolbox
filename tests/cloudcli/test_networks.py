import json

import pytest

from ..common import assert_str_int
from ..conftest import CloudcliFailedException


def assert_create_network(cloudcli, test_network):
    assert cloudcli('network', 'create', extra_args_dict={
        'datacenter': test_network['datacenter'],
        'name': test_network['network_name'],
        'subnetIp': test_network['subnetIp'],
        'subnetBit': test_network['subnetBit'],
        'gateway': test_network['gateway'],
        'dns1': test_network['dns1'],
        'dns2': test_network['dns2'],
        'subnetDescription': test_network['subnetDescription']
    }) == 'Network created successfully\n'
    with pytest.raises(CloudcliFailedException, match='cloudcli failed exit code 2'):
        cloudcli('network', 'create', extra_args_dict={
            'datacenter': test_network['datacenter'],
            'name': test_network['network_name'],
            'subnetIp': test_network['subnetIp'],
            'subnetBit': test_network['subnetBit'],
            'gateway': test_network['gateway'],
            'dns1': test_network['dns1'],
            'dns2': test_network['dns2'],
            'subnetDescription': test_network['subnetDescription']
        })


def assert_list_networks(cloudcli, test_network):
    networks = cloudcli('network', 'list', '--datacenter', test_network['datacenter'], parse=True)
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


def assert_delete_network_with_subnets(cloudcli, test_network):
    with pytest.raises(CloudcliFailedException):
        cloudcli(
            'network', 'delete',
            '--datacenter', test_network['datacenter'],
            '--id', str(test_network['network_id'])
        )


def assert_list_subnets(cloudcli, test_network):
    subnets = cloudcli(
        'network', 'subnet_list',
        '--datacenter', test_network['datacenter'],
        '--vlanId', str(test_network['vlan_id']),
        parse=True
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


def assert_create_subnet2(cloudcli, test_network):
    assert cloudcli(
        'network', 'subnet_create',
        extra_args_dict={
            'datacenter': test_network['datacenter'],
            'vlanId': str(test_network['vlan_id']),
            'subnetIp': test_network['subnet2']['subnetIp'],
            'subnetBit': str(test_network['subnet2']['subnetBit']),
            'gateway': test_network['subnet2']['gateway'],
            'dns1': test_network['subnet2']['dns1'],
            'dns2': test_network['subnet2']['dns2'],
            'subnetDescription': test_network['subnet2']['subnetDescription']
        }
    ) == 'Subnet created successfully\n'
    with pytest.raises(CloudcliFailedException):
        cloudcli(
            'network', 'subnet_create',
            extra_args_dict={
                'datacenter': test_network['datacenter'],
                'vlanId': str(test_network['vlan_id']),
                'subnetIp': test_network['subnet2']['subnetIp'],
                'subnetBit': str(test_network['subnet2']['subnetBit']),
                'gateway': test_network['subnet2']['gateway'],
                'dns1': test_network['subnet2']['dns1'],
                'dns2': test_network['subnet2']['dns2'],
                'subnetDescription': test_network['subnet2']['subnetDescription']
            }
        )


def assert_list_subnets2(cloudcli, test_network):
    subnets = cloudcli(
        'network', 'subnet_list',
        '--datacenter', test_network['datacenter'],
        '--vlanId', str(test_network['vlan_id']),
        parse=True
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


def assert_edit_subnet(cloudcli, test_network, gateway):
    assert cloudcli(
        'network', 'subnet_edit',
        extra_args_dict={
            'datacenter': test_network['datacenter'],
            'vlanId': str(test_network['vlan_id']),
            'subnetId': str(test_network['subnet_id']),
            'subnetIp': test_network['subnetIp'],
            'subnetBit': str(test_network['subnetBit']),
            'gateway': gateway,
            'dns1': test_network['dns1'],
            'dns2': test_network['dns2'],
            'subnetDescription': test_network['subnetDescription']
        }
    ) == 'Subnet updated successfully\n'


def assert_subnet_gateway(cloudcli, test_network, subnetDescription, gateway):
    subnets = cloudcli(
        'network', 'subnet_list',
        '--datacenter', test_network['datacenter'], '--vlanId', str(test_network['vlan_id']),
        parse=True
    )
    for subnet in subnets:
        if subnet['subnetDescription'] == subnetDescription:
            assert subnet['gateway'] == gateway
            return
    raise Exception("Did not find subnet")


def assert_delete_subnet(cloudcli, subnet_id):
    assert cloudcli(
        'network', 'subnet_delete', '--subnetId', str(subnet_id)
    ) == 'Subnet deleted successfully\n'
    with pytest.raises(CloudcliFailedException):
        cloudcli(
            'network', 'subnet_delete', '--subnetId', str(subnet_id)
        )


def assert_delete_network(cloudcli, test_network):
    assert cloudcli(
        'network', 'delete',
        '--datacenter', test_network['datacenter'],
        '--id', str(test_network['network_id'])
    ) == 'Network deleted successfully\n'
    with pytest.raises(CloudcliFailedException):
        cloudcli(
            'network', 'delete',
            '--datacenter', test_network['datacenter'],
            '--id', str(test_network['network_id'])
        )


def test_networks(cloudcli):
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
    assert_create_network(cloudcli, test_network)
    test_network['network_id'], test_network['vlan_id'] = assert_list_networks(cloudcli, test_network)
    assert_delete_network_with_subnets(cloudcli, test_network)
    test_network['subnet_id'] = assert_list_subnets(cloudcli, test_network)
    test_network['subnet2'] = dict(
        gateway='192.168.0.1',
        dns1='6.6.6.6',
        dns2='7.7.7.7',
        subnetDescription='2nd subnet',
        subnetBit='26',
        subnetIp='192.168.0.0',
    )
    assert_create_subnet2(cloudcli, test_network)
    test_network['subnet_id'], test_network['subnet2']['subnet_id'] = assert_list_subnets2(cloudcli, test_network)
    assert_edit_subnet(cloudcli, test_network, '172.16.0.2')
    assert_subnet_gateway(cloudcli, test_network, test_network['subnetDescription'], '172.16.0.2')
    assert_delete_subnet(cloudcli, test_network['subnet_id'])
    assert_delete_subnet(cloudcli, test_network['subnet2']['subnet_id'])
    assert_delete_network(cloudcli, test_network)
