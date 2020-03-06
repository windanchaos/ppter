# -*- coding: utf-8 -*-
from aliapi import APIURL, ConfigFactory
import requests, logging, time
import ConfigProvider

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
""""操作阿里云的vpn,调用create_vpn_connection即可完成删、加功能"""

"""用api的Action命名请求"""

vpn_connection_name = ConfigProvider.get_vps_cnf().get('name')
gatewayname = vpn_connection_name[2:]

DescribeVpnConnections = {'Action': 'DescribeVpnConnections', 'RegionId': 'cn-hangzhou'}
DeleteVpnConnection = {'Action': 'DeleteVpnConnection', 'RegionId': 'cn-hangzhou', 'VpnConnectionId': ''}
DeleteCustomerGateway = {'Action': 'DeleteCustomerGateway', 'RegionId': 'cn-hangzhou', 'CustomerGatewayId': ''}
CreateCustomerGateway = {'Action': 'CreateCustomerGateway', 'RegionId': 'cn-hangzhou', 'IpAddress': '',
                         'Name': gatewayname}
CreateVpnConnection = {'Action': 'CreateVpnConnection', 'RegionId': 'cn-hangzhou',
                       'VpnGatewayId': 'XXXXXXXXXX', \
                       'LocalSubnet': '172.16.128.0/20', 'RemoteSubnet': '10.189.51.0/24',
                       'IpsecConfig': str({'IpsecAuthAlg': 'sha1'}),
                       'IkeConfig': str({'Psk': 'XXXXXXXXX', 'IkeAuthAlg': 'sha1'}), 'CustomerGatewayId': '',
                       'Name': ''}


def create_vpn_connection(ip):
    """先删除原来的，再新增"""
    logging.info("ali vpn connection config: ip:" + ip + ". vpn_connection_name:" + vpn_connection_name)
    del_ali_vpn(vpn_connection_name)
    CustomerGatewayId = create_customer_gateway(ip)
    CreateVpnConnection['CustomerGatewayId'] = CustomerGatewayId
    CreateVpnConnection['Name'] = vpn_connection_name
    # 等待gateway完成创建（也可以用其他方式阻塞直到获取到gateway创建完成）
    time.sleep(5)
    vps_api_url = ConfigFactory('vps').get_config()['url']
    vps_parameters = ConfigFactory('vps').get_config()['parameters']
    url = APIURL(vps_api_url, vps_parameters, CreateVpnConnection).get_url()
    response = requests.get(url, verify=False, timeout=2)
    data = response.json()
    logging.info("CreateVpnConnection,the response:")
    logging.info(data)
    if str(response).find('VpnConnectionId') != -1:
        logging.info(response.headers)
    del url, response, CustomerGatewayId


def create_customer_gateway(ip):
    """:return CustomerGatewayId"""
    vps_api_url = ConfigFactory('vps').get_config()['url']
    vps_parameters = ConfigFactory('vps').get_config()['parameters']
    CreateCustomerGateway['IpAddress'] = ip
    url = APIURL(vps_api_url, vps_parameters, CreateCustomerGateway).get_url()
    response = requests.get(url, verify=False, timeout=2)
    logging.info("CreateCustomerGateway,the response:")
    logging.info(response.text)
    if response.text.find('CustomerGatewayId') != -1:
        return response.json()['CustomerGatewayId']
    else:
        return None


def del_ali_vpn(name):
    info_dict = get_vpn_connection_info(name)
    if len(info_dict) != 0:
        """删除IPsec实例"""
        vps_api_url = ConfigFactory('vps').get_config()['url']
        vps_parameters = ConfigFactory('vps').get_config()['parameters']
        DeleteVpnConnection['VpnConnectionId'] = info_dict['VpnConnectionId']
        url = APIURL(vps_api_url, vps_parameters, DeleteVpnConnection).get_url()
        response = requests.get(url, verify=False, timeout=2).json()
        logging.info("DeleteVpnConnection,the response:")
        logging.info(response)
        """删除用户网关"""
        vps_api_url2 = ConfigFactory('vps').get_config()['url']
        vps_parameters2 = ConfigFactory('vps').get_config()['parameters']
        DeleteCustomerGateway['CustomerGatewayId'] = info_dict['CustomerGatewayId']
        url = APIURL(vps_api_url2, vps_parameters2, DeleteCustomerGateway).get_url()
        response = requests.get(url, verify=False, timeout=2).json()
        logging.info("DeleteCustomerGateway,the response:")
        logging.info(response)
        del url, response


def get_vpn_connection_info(name):
    """获取VpnConnectionId and CustomerGatewayId as a dict"""
    info_dict = {}
    vps_api_url = ConfigFactory('vps').get_config()['url']
    vps_parameters = ConfigFactory('vps').get_config()['parameters']
    url = APIURL(vps_api_url, vps_parameters, DescribeVpnConnections).get_url()
    response = requests.get(url, verify=False, timeout=2)
    if response.text.find('VpnConnections') != -1:
        data = response.json()
        VpnConnections = data['VpnConnections']['VpnConnection']
        for VpnConnection in VpnConnections:
            if VpnConnection['Name'] == name:
                info_dict['VpnConnectionId'] = VpnConnection['VpnConnectionId']
                info_dict['CustomerGatewayId'] = VpnConnection['CustomerGatewayId']
    del url, data, VpnConnections
    logging.info("get " + name + " vpn connection dict info :" + str(info_dict))
    return info_dict

create_vpn_connection('125.119.233.176')