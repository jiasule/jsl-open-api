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

API_PATH_GET = '/api/v4/open_api/white_black_list_get'  # 设置黑白名单API路径
API_PATH_SET = '/api/v4/open_api/white_black_list_set'  # 获取黑白名单API路径

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

def white_black_list_set(sid=None, id=None, keyword=None, values=None):
    """
    设置黑白名单
    :param sid: 域名ID(从查询接口获取)
    :param id: 子域名ID(从查询接口获取)
    :param keyword: 需要设置的类型，可选值: ip_blacklist(ipv4黑名单)/ip_whitelist(ipv4白名单)/ipv6_blacklist(ipv6黑名单)/ipv6_whitelist(ipv6白名单)/url_blacklist(URL黑名单)/url_whitelist(URL白名单)
    :param values: 需要设置的值，格式: [['1.1.1.1', '黑名单1'], ['1.1.1.2', '黑名单2']], 具体可参考main函数中的测试数据
    """
    url = YUNAQ_DOMAIN + API_PATH_SET
    params = {
        'time': int(time.time()),
        'sid': sid,
        'id': id,
        'keyword': keyword,
        'values': json.dumps(values)
    }
    headers = get_headers(params)  
    try:
        response = requests.post(url, data=json.dumps(params), headers=headers)
        data = json.loads(response.content)
        if response.status_code != 200 or data['status'] == 'error':
            print('接口调用错误，当前状态码为: %s, 返回值为: %s' % (
                response.status_code, data))
        else:
            print('接口调用成功，当前状态码为: %s, 返回值为: %s' % (
                response.status_code, data))
        return data
    except Exception as error:
        print(error)
        raise Exception(traceback.format_exc()) 

def white_black_list_get(domain=None, host=None):
    """
    查询黑白名单信息
    :param domain: 域名
    :param host: 主机名
    """
    url = YUNAQ_DOMAIN + API_PATH_GET
    params = {'domain': domain.strip(), 'host': host.strip()} if domain else {}
    params.update({
        'time': str(int(time.time())),
    })
    headers = get_headers(params)
    try:
        response = requests.get(url, params=params, headers=headers)
        data = json.loads(response.content)
        if response.status_code != 200 or data['status'] == 'error':
            print('接口调用错误，当前状态码为: %s, 返回值为: %s' % (
                response.status_code, data))
        else:
            print('接口调用成功，当前状态码为: %s, 返回值为: %s' % (
                response.status_code, data))
        return data
    except Exception as error:
        print(error)
        raise Exception(traceback.format_exc())


if __name__ == '__main__':
    # 黑白名单查询
    # 返回结果示例子：{'code': 0, 'data': {'id': '6556d98d8c7f35000fc4b7b9', 'ip_blacklist': [], 'ip_whitelist': [['10.1.1.1', '']], 'ipv6_blacklist': [], 'ipv6_whitelist': [], 'sid': '6475918a39630f00292a6a15', 'url_blacklist': [], 'url_whitelist': []}, 'status': 'success'}
    data = white_black_list_get('example.com', 'www')
    id = data['data']['id']
    sid = data['data']['sid']
    
    # ipv4黑名单设置
    ip_blacklist = [['1.1.1.1-1.1.1.24', '黑名单1'],['1.1.1.2', '黑名单2']]
    white_black_list_set(sid=sid, id=id, keyword='ip_blacklist', values=ip_blacklist)
    
    # ipv4白名单设置
    ip_whitelist = [['2.2.2.1', '白名单1'],['2.2.2.2', '白名单2']]
    white_black_list_set(sid=sid, id=id, keyword='ip_whitelist', values=ip_whitelist)
    
    # ipv6黑名单设置
    ipv6_blacklist = [['1000::1-1000::3', 'IPv6黑名单1'],['1000::20', 'IPv6黑名单2']]
    white_black_list_set(sid=sid, id=id, keyword='ipv6_blacklist', values=ipv6_blacklist)
    
    # ipv6白名单设置
    ipv6_whitelist = [['2000::1', 'IPv6白名单1'],['2000::2', 'IPv6白名单2']]
    white_black_list_set(sid=sid, id=id, keyword='ipv6_whitelist', values=ipv6_whitelist)
    
    # url黑名单设置
    # 格式：['URL', '备注', [端口]]，多个端口以','分开
    # 例如，全部端口： ['www1', 'URL黑名单1']，指定端口： ['www2', 'URL黑名单2', [8080,8090]]
    url_blacklist = [['www1', 'URL黑名单1'],['www2', 'URL黑名单2', [80]]]
    # 如需忽略url大小写，则需要设置url_blackwhitelist_nocase为1
    # url_blacklist =  {
    #     "values": [["www3", "URL黑名单3"], ["www4", "URL黑名单4", [80]]], 
    #     "url_blackwhitelist_nocase": 1
    # 
    white_black_list_set(sid=sid, id=id, keyword='url_blacklist', values=url_blacklist)
    
    # url白名单设置
    url_whitelist = [['www1', 'URL白名单1'],['www2', 'URL白名单2', [80]]]
    white_black_list_set(sid=sid, id=id, keyword='url_whitelist', values=url_whitelist)
    