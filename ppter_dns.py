# -*- coding: utf-8 -*-
import requests, time, logging
from aliapi import APIURL,ConfigFactory

dns_api_url = ConfigFactory('dns').get_config()['url']


def update_domain_record(record):
    dns_parameters = ConfigFactory('dns').get_config()['parameters']
    response = requests.get(APIURL(dns_api_url,dns_parameters,record).get_url(), verify=False,timeout=2)
    logging.info("dns config response:"+response.text)
    return response


def get_domains():
    dns_parameters = ConfigFactory('dns').get_config()['parameters']
    record={'Action': 'DescribeDomains'}
    response = requests.get(APIURL(dns_api_url,dns_parameters,record).get_url(), verify=False,timeout=2)
    print(response.text)


def get_domain_records(domain):
    dns_parameters = ConfigFactory('dns').get_config()['parameters']
    record={'Action': 'DescribeDomainRecords','DomainName':domain}
    response = requests.get(APIURL(dns_api_url,dns_parameters,record).get_url(), verify=False,timeout=2)
    print(response.text)


