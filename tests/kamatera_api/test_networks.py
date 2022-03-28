from .common import kamatera_api_request
from ..common import assert_str_int


def post_create_network(datacenter, name, subnetIp, subnetBit, gateway, dns1, dns2, subnetDescription):
    path = f'/svc/networks/{datacenter.upper()}/create'
    return kamatera_api_request(path, method='POST', json={
        "name": name,
        "subnetIp": subnetIp,
        "subnetBit": int(subnetBit),
        "gateway": gateway,
        "dns1": dns1,
        "dns2": dns2,
        "subnetDescription": subnetDescription
    })


def get_list_networks(datacenter):
    path = f'/svc/networks/{datacenter.upper()}/networks'
    return kamatera_api_request(path)


def delete_network(datacenter, id, ignore_errors=False):
    assert_str_int(id)
    path = f'/svc/networks/{datacenter.upper()}/{id}/delete'
    return kamatera_api_request(path, ignore_errors=ignore_errors, method='DELETE')


def get_list_subnets(datacenter, vlan_id):
    assert_str_int(vlan_id)
    path = f'/svc/networks/subnets?datacenter={datacenter.upper()}&vlanId={vlan_id}&filter='
    return kamatera_api_request(path)


def delete_subnet(subnet_id):
    assert_str_int(subnet_id)
    path = f'/svc/networks/subnets/subnet/{subnet_id}/delete'
    return kamatera_api_request(path, method='DELETE')


def post_create_subnet(datacenter, vlan_id, subnetIp, subnetBit, gateway, dns1, dns2, subnetDescription):
    assert_str_int(vlan_id)
    path = f'/svc/networks/{datacenter.upper()}/{vlan_id}/create'
    return kamatera_api_request(path, method='POST', json={
        "subnetIp": subnetIp,
        "subnetBit": assert_str_int(subnetBit),
        "gateway": gateway,
        "dns1": dns1,
        "dns2": dns2,
        "subnetDescription": subnetDescription
    })


def put_edit_subnet(datacenter, vlan_id, subnet_id, subnetIp, subnetBit, gateway, dns1, dns2, subnetDescription):
    assert_str_int(subnet_id)
    path = f'/svc/networks/subnets/subnet/{subnet_id}/edit'
    return kamatera_api_request(path, method='PUT', json={
        "datacenter": datacenter.upper(),
        "vlanId": assert_str_int(vlan_id),
        "subnetIp": subnetIp,
        "subnetBit": assert_str_int(subnetBit),
        "gateway": gateway,
        "dns1": dns1,
        "dns2": dns2,
        "subnetDescription": subnetDescription
    })


def get_list_ips(subnetId, networkId, datacenter):
    assert_str_int(subnetId)
    assert_str_int(networkId)
    path = f'/svc/networks/ips?subnetId={subnetId}&networkId={networkId}&datacenter={datacenter.upper()}'
    return kamatera_api_request(path)


def test_create_network():
    datacenter = 'IL-TA'
    network_name = 'ktbk-test-networks'
    gateway = '172.16.0.100'
    dns1 = '1.2.3.4'
    dns2 = '1.2.3.4'
    subnetDescription = 'testing 1 2 3'
    subnetBit = '23'
    subnetIp = '172.16.0.0'
    assert post_create_network(
        datacenter, network_name,
        subnetIp=subnetIp, subnetBit=subnetBit, gateway=gateway,
        dns1=dns1, dns2=dns2, subnetDescription=subnetDescription
    ) == {}
    networks_list = get_list_networks(datacenter)
    assert_str_int(networks_list['size'])
    assert assert_str_int(networks_list['total']) > 0
    network = networks_list['items'][0]
    assert len(network['ids']) == 1
    network_id = network['ids'][0]
    assert_str_int(network_id)
    assert len(network['names']) == 1
    lan, number, *name = network['names'][0].split('-')
    assert lan == 'lan'
    assert_str_int(number)
    assert '-'.join(name) == network_name
    vlan_id = assert_str_int(network['vlanId'])
    status_code, res = delete_network(datacenter, network_id, ignore_errors=True)
    assert status_code == 500
    assert len(res['errors']) == 1
    assert res['errors'][0]['code'] == 20
    assert res['errors'][0]['info'] == 'error occurred'
    assert res['errors'][0]['category'] == 'General Error'
    subnets = get_list_subnets(datacenter, vlan_id)
    assert len(subnets['subnets']) == 1
    subnet = subnets['subnets'][0]
    assert subnet['dns1'] == dns1
    assert subnet['dns2'] == dns2
    assert subnet['endRange'] == '172.16.1.254'
    assert subnet['gateway'] == gateway
    assert assert_str_int(subnet['inUse']) in [0, 1]
    assert subnet['startRange'] == '172.16.0.1'
    assert assert_str_int(subnet['subnetBit']) == int(subnetBit)
    assert subnet['subnetDescription'] == subnetDescription
    subnet_id = assert_str_int(subnet['subnetId'])
    assert subnet['subnetIp'] == subnetIp
    assert subnet['subnetMask'] == '255.255.254.0'
    assert assert_str_int(subnet['total']) == 510
    subnet2_gateway = '192.168.0.1'
    subnet2_dns1 = '6.6.6.6'
    subnet2_dns2 = '7.7.7.7'
    subnet2_subnetDescription = '2nd subnet'
    subnet2_subnetBit = '26'
    subnet2_subnetIp = '192.168.0.0'
    assert post_create_subnet(datacenter, vlan_id, subnet2_subnetIp, subnet2_subnetBit,
                              subnet2_gateway, subnet2_dns1, subnet2_dns2, subnet2_subnetDescription) == {}
    subnets = get_list_subnets(datacenter, vlan_id)
    assert len(subnets['subnets']) == 2
    got_subnet1, got_subnet2, subnet2_id = False, False, None
    for subnet in subnets['subnets']:
        if subnet['subnetDescription'] == subnet2_subnetDescription:
            assert not got_subnet2
            got_subnet2 = True
            assert subnet['subnetIp'] == subnet2_subnetIp
            subnet2_id = assert_str_int(subnet['subnetId'])
        elif subnet['subnetDescription'] == subnetDescription:
            assert not got_subnet1
            got_subnet1 = True
            assert subnet['subnetIp'] == subnetIp
        else:
            raise Exception("Invalid subnet: {}".format(subnet))
    assert got_subnet1 and got_subnet2
    put_edit_subnet(datacenter, vlan_id, subnet_id, subnetIp, subnetBit, '172.16.0.2',
                    dns1, dns2, subnetDescription)
    subnets = get_list_subnets(datacenter, vlan_id)
    assert len(subnets['subnets']) == 2
    got_subnet = False
    for subnet in subnets['subnets']:
        if subnet['subnetDescription'] == subnetDescription:
            assert subnet['gateway'] ==  '172.16.0.2'
            got_subnet = True
    assert got_subnet
    ips = get_list_ips(subnet_id, vlan_id, datacenter)
    assert len(ips) == 510
    ip = ips[0]
    assert ip['clearIsEnable'] in [True, False]
    assert ip['ip'].startswith('172.16.0.')
    assert delete_subnet(subnet_id) == {}
    assert delete_subnet(subnet2_id) == {}
    assert delete_network(datacenter, network_id) == {}
