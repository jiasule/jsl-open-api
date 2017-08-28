#!/usr/bin/env python
# coding: utf-8

import datetime
import hmac
import hashlib
import sys
import traceback
import urllib2
import urllib
from base64 import b64encode


API_KEYS = {
    '51e4c1a18d2a7d10c4841c57': 'JruWq5T7FKq1g1VayLhtIqFWiCdiLKfopnAfpNOMi6evGaxxmgO6azgMhqqi6Im2',
}

domain = 'test.com'
host = '@'
isp = '0'
time = datetime.datetime.now().strftime('%s')
param_dict = {
    "upsert": [
        ("domain", domain),
        ("host", host),
        ("ip", "1.2.3.4"),
        ("isp", isp),
        ("email", "test@test.com"),
        ("use_cdn", "true"),
        ("cdn.waf", "true"),
        ("cdn.static", "true"),
        ("cdn.html", "true"),
        ("cdn.index", "false"),
        ("cdn.directory", "true"),
        ("time", time),
    ],
    "list": [
        #("domain", domain),
        #("host", host),
        ("time", time),
    ],
    "del": [
        ("domain", domain),
        ("host", host),
        ("isp", isp),
        ("time", time),
    ],
    "purge": [
        ("domain", domain),
        ("host", host),
        ("time", time),
    ],
}
url = "https://www.yunaq.com/api/site/%s/"


def init_header(user, token):
    header = {}
    b64string = b64encode('%s:%s' % (user, token))
    header['AUTHORIZATION'] = 'Basic %s' % b64string
    return header


def make_signature(secret_key, data):
    hashed = hmac.new(secret_key, data, hashlib.sha1)
    return hashed.hexdigest()


def make_sorted_param_string(param):
    ''' 将参数排序并序列化为字符串
    '''
    if isinstance(param, dict):
        param = param.items()
    param.sort(key=lambda x: x[0])
    data = urllib.urlencode(param)
    return urllib.unquote(data)


def main(url, user, secret_key, param):
    ''' 发送POST请求主函数
    '''
    data = make_sorted_param_string(param)
    signature = make_signature(secret_key, data)
    header = init_header(user, signature)
    print data
    req = urllib2.Request(url, data, headers=header)
    try:
        res = urllib2.urlopen(req)
        print res.read()
    except urllib2.HTTPError as e:
        traceback.print_exc()
        print e.read()


if "__main__" == __name__:
    action = sys.argv[1]
    if action not in param_dict:
        print 'first arg should be one of ', param_dict.keys()
        sys.exit(1)
    post_url = url % action
    user = API_KEYS.keys()[0]
    secret_key = API_KEYS[user]
    param = param_dict[action]
    main(post_url, user, secret_key, param)
