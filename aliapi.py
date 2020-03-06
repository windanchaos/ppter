# -*- coding: utf-8 -*-
import os, time, urllib, uuid, hmac
import configparser, base64
from hashlib import sha1

""""
已知阿里api各个产品线的签名有差异
:parameter api的签名字典，由于是全局变量，所以只能使用一次。
kwargs api请求参数字典
调用方式，传入对应参数和api的字典。调用get_url()获取url

"""


class ConfigFactory:
    """
    工厂方法获取配置
    """

    def __init__(self, api_name):
        self.api_name = api_name

    def get_config(self):
        if self.api_name == 'dns':
            return {'url': 'http://alidns.aliyuncs.com', 'parameters': { \
                'Format': 'JSON', \
                'Version': '2015-01-09', \
                'SignatureVersion': '1.0', \
                'SignatureMethod': 'HMAC-SHA1', \
                'Timestamp': '',
            }}
        if self.api_name == 'vps':
            return {'url': 'http://vpc.aliyuncs.com', 'parameters': { \
                'Format': 'JSON', \
                'Version': '2016-04-28', \
                'SignatureVersion': '1.0', \
                'SignatureMethod': 'HMAC-SHA1', \
                'Timestamp': '',
            }}
        if self.api_name == 'cdn':
            return {'url': 'https://cdn.aliyuncs.com', 'parameters': { \
                'Format': 'JSON', \
                'Version': '2018-05-10', \
                'SignatureVersion': '1.0', \
                'SignatureMethod': 'HMAC-SHA1', \
                'Timestamp': '',
            }}


class APIURL():
    api_address = ''
    CONFIGFILE = os.getcwd() + '/config.ini'
    parameters = {}

    def __init__(self, url, parameters, kwargs):
        config = configparser.ConfigParser()
        self.parameters = parameters
        self.api_address = url
        self.kwargs = kwargs
        try:
            config.read(self.CONFIGFILE, encoding='utf-8')
            self.parameters['AccessKeyId'] = config.get('Credentials', 'accesskeyid')
            self.parameters['accesskeysecret'] = config.get('Credentials', 'accesskeysecret')
            for key, value in self.kwargs.items():
                self.parameters[key.strip()] = value
        except:
            raise self.CONFIGFILE.__str__() + 'not exist'

    def get_url(self):
        """return the url """
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.parameters['SignatureNonce'] = str(uuid.uuid1())
        if 'Timestamp' in self.parameters:
            self.parameters['Timestamp'] = timestamp
        if 'TimeStamp' in self.parameters:
            self.parameters['TimeStamp'] = timestamp
        # 签名
        signature = self.compute_signature()
        self.parameters['Signature'] = signature
        if self.api_address.lower().startswith('http') and self.api_address is not None:
            url = self.api_address + "/?" + urllib.parse.urlencode(self.parameters)
        else:
            print("url should start with http or https ,yours is not right,check your url")
        return url

    def url_encode(self, url):
        # url 编码
        res = urllib.parse.quote(url.encode('utf8'), '')
        res = res.replace('+', '%20')
        res = res.replace('*', '%2A')
        res = res.replace('%7E', '~')
        return res

    def compute_signature(self):
        access_key_secret = self.parameters['accesskeysecret']
        # 排序时选择的元素是key
        sortedParameters = sorted(self.parameters.items(), key=lambda parameters: parameters[0])
        # 构参
        canonicalizedQueryString = ''
        for (k, v) in sortedParameters:
            canonicalizedQueryString += '&' + self.url_encode(k) + '=' + self.url_encode(v)
        # %2F 为 /
        stringToSign = 'GET&%2F&' + self.url_encode(canonicalizedQueryString[1:])
        # 哈希算法 This returns a string containing 8-bit data
        h = hmac.new((access_key_secret + "&").encode('utf-8'), stringToSign.encode('utf-8'), sha1)
        # 编码
        # signature = base64.b64decode(base64.b64encode(h.digest())).strip()
        signature = base64.encodebytes(h.digest()).strip()
        del access_key_secret, sortedParameters, canonicalizedQueryString, h, stringToSign
        return signature
