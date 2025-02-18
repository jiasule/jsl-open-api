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

def white_black_list_set(domain=None, host=None, keyword=None, values=None, acion=None):
    """
    设置黑白名单
    :param domain: 域名
    :param host: 主机名
    :param keyword: 需要设置的类型，可选值: ip_blacklist(ipv4黑名单)/ip_whitelist(ipv4白名单)/ipv6_blacklist(ipv6黑名单)/ipv6_whitelist(ipv6白名单)/url_blacklist(URL黑名单)/url_whitelist(URL白名单)
    :param values: 需要设置的值，格式: [['1.1.1.1', '黑名单1'], ['1.1.1.2', '黑名单2']], 具体可参考main函数中的测试数据
    """
    url = YUNAQ_DOMAIN + API_PATH_SET
    params = {
        'time': int(time.time()),
        'domain': domain,
        'host': host,
        'keyword': keyword,
        'action': acion,
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
    domain = 'example.com'
    host = 'www'
    # 黑白名单查询
    data = white_black_list_get(domain, host)
    """
    查询结果示例
        {
            'code': 0,
            'data': {
                'domain': 'example.com',
                'host': 'www',
                'ip_blacklist': [
                    ['1.1.1.2', '黑名单2'],
                    ['1.1.1.22-1.1.1.25', '黑名单3']
                ],
                'ip_whitelist': [
                    ['1.1.1.2', '黑名单2'],
                    ['1.1.1.22-1.1.1.25', '黑名单3']
                ],
                'ipv6_blacklist': [
                    ['2001:db8::2', '黑名单2'],
                    ['2001:db8::10-2001:db8::20', '黑名单3']
                ],
                'ipv6_whitelist': [
                    ['2001:db8::2', '黑名单2'],
                    ['2001:db8::10-2001:db8::20', '黑名单3']
                ],
                'url_blacklist': [
                    ['www.example2.com', '测试2'],
                    ['www.example3.com', '测试3', [80]]
                ],
                'url_blackwhitelist_nocase': 1,
                'url_whitelist': [
                    ['www.example2.com', '测试2'],
                    ['www.example3.com', '测试3', [80]]
                ]
            },
            'status': 'success'
        }
    """

    # ipv4黑名单设置: 新增
    ip_blacklist = [['1.1.1.1', '黑名单1'], ['1.1.1.10-1.1.1.20', '黑名单2']]
    action = 'add'
    white_black_list_set(domain=domain, host=host, keyword='ip_blacklist', values=ip_blacklist, acion=action)
    
    # ipv4黑名单设置: 删除
    ip_blacklist = ['1.1.1.1']
    action = 'delete'
    white_black_list_set(domain=domain, host=host, keyword='ip_blacklist', values=ip_blacklist, acion=action)
    
    # ipv4黑名单设置: 全量覆盖
    ip_blacklist = [['1.1.1.100', ''], ['1.1.1.100-1.1.1.200', '']]
    action = 'full'
    white_black_list_set(domain=domain, host=host, keyword='ip_blacklist', values=ip_blacklist, acion=action)

    # ipv4白名单设置: 新增
    ip_whitelist = [['2.2.2.2', '白名单1'], ['2.2.2.20-2.2.2.30', '白名单2']]
    action = 'add'
    white_black_list_set(domain=domain, host=host, keyword='ip_whitelist', values=ip_whitelist, acion=action)
    
    # ipv4白名单设置: 删除
    ip_whitelist = ['2.2.2.2']
    action = 'delete'
    white_black_list_set(domain=domain, host=host, keyword='ip_whitelist', values=ip_whitelist, acion=action)
    
    # ipv4白名单设置: 全量覆盖
    ip_whitelist = [['2.2.2.200', ''], ['2.2.2.200-2.2.2.220', '']]
    action = 'full'
    white_black_list_set(domain=domain, host=host, keyword='ip_whitelist', values=ip_whitelist, acion=action)
    
    # ipv6黑名单设置: 新增
    ipv6_blacklist = [['1000::1', 'IPv6黑名单1'], ['1000::10-1000::30', 'IPv6黑名单2']]
    action = 'add'
    white_black_list_set(domain=domain, host=host, keyword='ipv6_blacklist', values=ipv6_blacklist, acion=action)
    
    # ipv6黑名单设置: 删除
    ipv6_blacklist = ['1000::1']
    action = 'delete'
    white_black_list_set(domain=domain, host=host, keyword='ipv6_blacklist', values=ipv6_blacklist, acion=action)
    
    # ipv6黑名单设置: 全量覆盖
    ipv6_blacklist = [['1000::100', ''], ['1000::100-1000::200', '']]
    action = 'full'
    white_black_list_set(domain=domain, host=host, keyword='ipv6_blacklist', values=ipv6_blacklist, acion=action)
    
    # ipv6白名单设置: 新增
    ipv6_whitelist = [['2000::1', 'IPv6白名单1'], ['2000::20-2000::30', 'IPv6白名单2']]
    action = 'add'
    white_black_list_set(domain=domain, host=host, keyword='ipv6_whitelist', values=ipv6_whitelist, acion=action)
    
    # ipv6白名单设置: 删除
    ipv6_whitelist = ['2000::1']
    action = 'delete'
    white_black_list_set(domain=domain, host=host, keyword='ipv6_whitelist', values=ipv6_whitelist, acion=action)
    
    # ipv6白名单设置: 全量覆盖
    ipv6_whitelist = [['2000::100', ''], ['2000::100-2000::200', '']]
    action = 'full'
    white_black_list_set(domain=domain, host=host, keyword='ipv6_whitelist', values=ipv6_whitelist, acion=action)
    
    # url黑名单设置: 新增
    # 格式: ['URL', '备注', [端口]]，多个端口以','分开
    # 例如，全部端口: ['www1', 'URL黑名单1']，指定端口:  ['www2', 'URL黑名单2', [8080,8090]]
    url_blacklist = [['www1', 'URL黑名单1'], ['www2', 'URL黑名单2', [80]]]
    action = 'add'
    white_black_list_set(domain=domain, host=host, keyword='url_blacklist', values=url_blacklist, acion=action)
    
    # url黑名单设置: 新增+设置是否忽略URL大小写
    # 如需忽略URL大小写，设置url_blackwhitelist_nocase为1
    # url_blackwhitelist_nocase对url黑、白名单同时生效
    url_blacklist = {
        'values': [['www3', 'URL黑名单3'], ['www4', 'URL黑名单4', [80]]],
        'url_blackwhitelist_nocase': 1
    }
    action = 'add'
    white_black_list_set(domain=domain, host=host, keyword='url_blacklist', values=url_blacklist, acion=action)

    # url黑名单设置: 删除
    url_blacklist = ['www1']
    action = 'delete'
    white_black_list_set(domain=domain, host=host, keyword='url_blacklist', values=url_blacklist, acion=action)

    # url黑名单设置: 全量覆盖
    url_blacklist = [['www5', 'URL黑名单5'], ['www6', 'URL黑名单6', [80]]]
    action = 'full'
    white_black_list_set(domain=domain, host=host, keyword='url_blacklist', values=url_blacklist, acion=action)

    # url白名单设置: 新增
    # url_blackwhitelist_nocase设置同url黑名单，
    url_whitelist = [['www1', 'URL白名单1'], ['www2', 'URL白名单2', [80]]]
    action = 'add'
    white_black_list_set(domain=domain, host=host, keyword='url_whitelist', values=url_whitelist, acion=action)

    # url白名单设置: 删除  
    url_whitelist = ['www1']
    action = 'delete'
    white_black_list_set(domain=domain, host=host, keyword='url_whitelist', values=url_whitelist, acion=action)
    
    # url白名单设置: 全量覆盖 
    url_whitelist = [['www3', 'URL白名单3'], ['www4', 'URL白名单4', [80]]]
    action = 'full'
    white_black_list_set(domain=domain, host=host, keyword='url_whitelist', values=url_whitelist, acion=action)
