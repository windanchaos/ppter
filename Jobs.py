# -*- coding: utf-8 -*-
import threading, time, requests

import ConfigProvider
import ppter_vpn, json, urllib3
import logging, redis
import ppter_dns
import ppter_vps

""""
代码原理：
两地vpn联通，是各自在本地定时上报本地外网IP到阿里云上的redis。
侦测到任何一方的IP变动，则做vnp更新设置
"""
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
urllib3.disable_warnings()
ding_msg_url = ConfigProvider.get_ding_cnf()
global IP
IP = {'new': '183.156.98.254', 'old': '183.156.98.254'}


def get_new_ip_thread():
    """"get new ip every 5 minutes"""
    while True:
        try:
            response = requests.get('http://ip.42.pl/raw', timeout=5)
            if response.status_code == 200:
                IP['new'] = response.text
                logging.info('get new ip is:' + IP['new'])
        except:
            logging.info('获取本地外网IP异常')
            continue
            pass
        # 无论有变更与否都更新redis
        put_ip_to_redis(IP['new'])
        del response
        time.sleep(300)


def monitor_thread():
    logging.info("monitor_thread start")
    warn_time = 0
    while True:
        r = redis.Redis(host=ConfigProvider.get_redis_cnf().get('host'),
                        port=ConfigProvider.get_redis_cnf().get('port'),
                        password=ConfigProvider.get_redis_cnf().get('password'), db=0, socket_timeout=4,
                        socket_connect_timeout=4, retry_on_timeout=True)
        try:
            # 取Peer
            response = r.get(ConfigProvider.get_vpn_cnf().get('redisRemoteVpnName'))
            if response is None and warn_time < 1:
                send_ding_msg("无法从redis获取本地外网IP^.^")
                warn_time = 1
                raise UserWarning("无法从redis获取本地外网IP")
            new_dest_ip = str(response, encoding='utf-8')
            old_dest_ip = ppter_vpn.vpn_data['data']['apply']['vpn-config'][1]['dest']
            logging.info("get Peer IP from redis is: " + new_dest_ip + " . The old Peer IP is: " + old_dest_ip)
            logging.info("The new local IP is: " + IP['new'] + " . The old local IP is: " + IP['old'])

            # 远端Peer IP 变动后，仅做vpn设置
            if new_dest_ip != old_dest_ip:
                try:
                    change_vpn(new_dest_ip)
                    send_ding_msg("两地外网IP有变动，已自动修改本地vpn设置。" + ConfigProvider.get_vpn_cnf().get('redisLocalVpnName') +
                                  "新的本地外网IP为：" + IP['new'] + "。远端Peer IP：" + new_dest_ip)
                except BaseException:
                    pass
            # 本地IP变动后，同时设置dns和vpn
            if IP['new'] != IP['old']:
                try:
                    change_vpn(new_dest_ip)
                    change_dns_vps()
                    # 设置完后更新old值
                    IP['old'] = IP['new']
                    send_ding_msg(ConfigProvider.get_vpn_cnf().get('redisLocalVpnName') + "本地外网IP变动为:" + IP['new'] +
                                  "已自动设置DNS解析和阿里云IPsec连接设置。")
                except BaseException:
                    pass
        except:
            time.sleep(30)
            continue
            pass
        finally:
            r.close()
        del r
        time.sleep(280)


# 更新vpn的函数供线程调用
def change_vpn(new_dest_ip):
    logging.info("Change vpn config now")
    # 构造数据
    ppter_vpn.vpn_data['data']['apply']['vpn-config'][0]['src'] = IP['new']
    for config in ppter_vpn.vpn_data['data']['apply']['vpn-config'][1:]:
        config['dest'] = new_dest_ip
        config['src'] = IP['new']
    warn_time = 0
    # 执行vpn解析变更动作(登录并更新数据到路由）
    try:
        ppter_vpn.update_vpn()
        logging.info("change vpn config ,new local IP: " + IP['new'])
    except BaseException:
        send_ding_msg("自动更新内网的VPN配置发生异常")


def change_dns_vps():
    logging.info("Change dns config now")
    try:
        # dns解析
        for rep in ConfigProvider.get_dns_cnfs():
            # 本地新IP赋值
            rep['Value'] = IP['new']
            # 调用api更新
            ppter_dns.update_domain_record(rep)
        # 执行阿里云vps变更动作
        ppter_vps.create_vpn_connection(IP['new'])
        IP['old'] = IP['new']
    except BaseException:
        send_ding_msg("自动DNS配置发生异常")


def send_ding_msg(msg):
    ding_msg = {
        "msgtype": "text",
        "text": {
            "content": "自动更新本地内网的VPN配置发生异常^.^"
        }
    }
    ding_msg['text']['content'] = msg
    try:
        r = requests.post(ding_msg_url, data=json.dumps(ding_msg), verify=False,
                                 headers={'Content-Type': 'application/json'}, timeout=2)
    except:
        logging.info('send dingding message error')
        pass
    del r


def put_ip_to_redis(ip):
    r = redis.Redis(host=ConfigProvider.get_redis_cnf().get('host'), port=ConfigProvider.get_redis_cnf().get('port'),
                    password=ConfigProvider.get_redis_cnf().get('password'), db=0, socket_timeout=4,
                    socket_connect_timeout=4, retry_on_timeout=True)
    try:
        r.set(ConfigProvider.get_vpn_cnf().get('redisLocalVpnName'), ip, ex=6000)
        logging.info('update ip to redis:' + ip)
    except:
        logging.info('ERROR update ip to redis')
        pass
    finally:
        r.close()
        del r


if __name__ == '__main__':
    t1 = threading.Thread(target=get_new_ip_thread)
    t2 = threading.Thread(target=monitor_thread)
    t1.start()
    time.sleep(2)
    t2.start()
    t1.join()
    t2.join()
