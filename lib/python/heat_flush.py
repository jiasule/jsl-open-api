# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import base64
import hashlib
import hmac
import time
import json
import traceback
from urllib.parse import unquote, urlencode

import requests

YUNAQ_DOMAIN = 'https://defense.yunaq.com'  # API地址
API_PATH = '/api/v4/open_api/cache_heat'  # API路径

API_USER = '6661305xxxxb0ed56e54e'  # 用户API ID
API_KEY = '6a52e2cbxxxxx99d3484f7eca64b5'  # 用户API KEY


def make_signature(secret_key, data):
    """
    生成签名
    :param secret_key: 生成签名所需的key
    :param data: 要签名的数据
    """
    return hmac.new(secret_key.encode('utf-8'),
                    data.encode('utf-8'),
                    hashlib.sha1).hexdigest()


def make_sorted_param_string(param):
    """
    将请求参数排序并序列化为字符串
    :param param: API参数
    """
    keys = param.keys()
    values = param.values()
    params_list = [(key, val) for key, val in zip(keys, values)]
    params_list = sorted(params_list, key=lambda x: x[0])
    params_str = urlencode(params_list)
    return unquote(params_str)


def get_basic_auth_header(username, password):
    """
    获取basic认证请求头
    """
    dst_bytes = '%s:%s' % (username, password)
    sign = base64.b64encode(dst_bytes.encode('utf-8'))
    return {'AUTHORIZATION': 'Basic %s' % sign.decode()}


def get_headers(params):
    """
    获取带认证信息的请求头
    :param params: 请求参数
    """
    headers = {"User-Agent": ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; '
                              'rv:94.0) Gecko/20100101 Firefox/94.0'),
               "Content-Type": 'application/json'}
    # 将参数排序后签名
    sorted_params = make_sorted_param_string(params)
    signature = make_signature(API_KEY, sorted_params)

    headers.update(get_basic_auth_header(API_USER, signature))
    return headers


def heat_flush(domain, urls):
    """
    缓存预热
    :param domain: 域名
    :param urls: 需要缓存的url
    """
    url = YUNAQ_DOMAIN + API_PATH
    params = {
        'time': int(time.time()),
        'domain': domain.strip(),
        'urls': json.dumps(urls)
    }
    headers = get_headers(params)
    try:
        response = requests.post(url, data=json.dumps(params), headers=headers)
        data = json.loads(response.content)
        if response.status_code != 200 or data['status'] == 'error':
            print('缓存预热错误，当前状态码为: %s, 返回值为: %s' % (
                response.status_code, data))
        else:
            print('缓存预热成功，当前状态码为: %s, 返回值为: %s' % (
                response.status_code, data))
        return data
    except Exception as error:
        print(error)
        raise Exception(traceback.format_exc())


if __name__ == '__main__':
    heat_flush('example.com', ['http://www.example.com/index.html'])
