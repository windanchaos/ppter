# -*- coding: utf-8 -*-
import ast
import os
import configparser


""""
代码使用的配置提供程序
"""

config = configparser.ConfigParser()
config.read(os.getcwd() + '/config.ini', encoding='utf-8')


def get_ali_cnf():
    configmap = {'accesskeyid': config.get('Credentials', 'accesskeyid'),
                 'accesskeysecret': config.get('Credentials', 'accesskeysecret')}
    return configmap
    # redis的配置


def get_redis_cnf():
    configmap = {'host': config.get('redis', 'host'), 'port': config.get('redis', 'port'),
                 'password': config.get('redis', 'password')}
    return configmap
    # vpn路由器的配置


def get_vpn_cnf():
    configmap = {'url': config.get('vpn', 'url'), 'username': config.get('vpn', 'username'),
                 'password': config.get('vpn', 'password'), 'redisLocalVpnName': config.get('vpn', 'redisLocalVpnName'),
                 'redisRemoteVpnName': config.get('vpn', 'redisRemoteVpnName')}
    return configmap
    # dns配置，支持多个，返回list


def get_dns_cnfs():
    mylist = list()
    domain = config.get('dns', 'domain')
    m = domain.split('|')
    for i in m:
        configmap = dict()
        configmap['Action'] = 'UpdateDomainRecord'
        configmap['RecordId'] = ast.literal_eval(i).get('RecordId')
        configmap['RR'] = ast.literal_eval(i).get('RR')
        configmap['Type'] = 'A'
        configmap['Value'] = ''
        mylist.append(configmap)
    return mylist


def get_ding_cnf():
    return config.get('dingTalk', 'ding_msg_url')


def get_vps_cnf():
    configmap = {'name': config.get('vps', 'name')}
    return configmap


def test():
    print(get_redis_cnf().get('host'))
    print(get_redis_cnf().get('port'))
    print(get_redis_cnf().get('password'))

    print(get_ding_cnf())
    print(get_vpn_cnf().get('url'))
    print(get_vpn_cnf().get('username'))
    print(get_vpn_cnf().get('password'))
    print('########')
    print(get_vpn_cnf().get('localVpnName'))
    print(get_vpn_cnf().get('remoteVpnName'))
    print(type(get_vpn_cnf().get('aliVpnIP')))
    if get_vpn_cnf().get('aliVpnIP') == '':
        print("没有设置IP")
    print('########')
    print(get_dns_cnfs()[0].get('RecordId'))
    print(get_dns_cnfs()[0].get('RR'))
    print(get_ali_cnf().get('accesskeyid'))
    print(get_ali_cnf().get('accesskeysecret'))

