# -*- coding: utf-8 -*-
import requests, json, urllib3
import logging
import ConfigProvider

urllib3.disable_warnings()
""""操作本地路由器"""
""""要分开执行Jobs.py，因为ip变动以后，两地网络不通。单独设置vpn_data中json数据内容"""
# 本地路由vpn的配置数据
vpn_data = {"data": {
    "scenario": ".Vpn2",
    "action": "apply",
    "apply": {
        "afne": "enable",
        "vpn-config": [
            {
                "dest": "XXXXXXX",
                "description": "toaliyun",
                "src": "XXXXXX",
                "encryption": "aes128",
                "hash": "sha1",
                "dh-group": "2",
                "pw": "XXXXXXXX",
                "srcsub": "10.189.51.0/24",
                "destsub": "172.16.128.0/20"
            },
            {
                "dest": "XXXXXX",
                "description": "tochd",
                "src": "XXXXX",
                "encryption": "aes128",
                "hash": "sha1",
                "dh-group": "14",
                "pw": "Mitu521!",
                "srcsub": "10.189.32.0/19",
                "destsub": "10.188.32.0/19"
            }
        ],
        "subnets-config": [
            {
                "srcsub": "10.189.51.0/24",
                "destsub": "172.16.128.0/20"
            },
            {
                "srcsub": "10.189.32.0/19",
                "destsub": "10.188.32.0/19"
            }]}}}
vpn_url = ConfigProvider.get_vpn_cnf().get('url')
vpn_username = ConfigProvider.get_vpn_cnf().get('username')
vpn_password = ConfigProvider.get_vpn_cnf().get('password')
vpn_api = vpn_url + 'api/edge/feature.json'
aliVpnIP = ConfigProvider.get_vpn_cnf().get('aliVpnIP')

headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
# 通过字典方式定义请求body
formData = {'username': vpn_username, 'password': vpn_password}


def update_vpn():
    """"update ip of vpn config"""
    # headers_json使用过程中会加入cookies的值
    headers_json = {'Content-Type': 'application/json;charset=utf-8'}
    # 创建连接
    connection = requests.session()
    # 登录
    connection.post(url=vpn_url, data=formData, headers=headers, verify=False, timeout=5)
    cookies_login = connection.cookies.get_dict();
    headers_json.update(cookies_login)
    response = connection.post(vpn_api, verify=False, headers=headers_json, data=json.dumps(vpn_data), timeout=30)
    print(response.text)
    if response.text.find("\"success\": true") == -1:
        logging.info("new ip update failed ####### ")
        raise Exception("vnp update failed")
    else:
        logging.info("Local VPN config update  ok")
    del headers_json, connection, cookies_login, response
