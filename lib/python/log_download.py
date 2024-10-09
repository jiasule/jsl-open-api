# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import base64
import hashlib
import hmac
import os
import time
import json
import traceback
from urllib.parse import unquote, urlencode

import requests

YUNAQ_DOMAIN = 'https://defense.yunaq.com'  # API地址
API_PATH = '/api/v4/open_api/log_download'  # API路径

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


def log_download(domain, log_type, date, date_type):
    """
    日志下载
    1. 正确的结果是一个与域名相关的压缩文件，如example.com-access-20240320.log.gz
       或example.com-attack-20240320.log.gz
    2. 三种日志类型都可以选择按天下载或按小时下载。
       按天只能下载最近7天的日志，当天除外。如当天是3月21号，则可以下载3月14号到3月20号之间的日志；
       按小时可以下载当前时间减去两小时的24小时内的日志。如现在是3月21号15点，可以下载3月20号14点到3月21号13点的日志

    :param domain: 域名
    :param log_type: 需要下载的日志类型，可选值：access(访问日志)/attack(攻击日志)/anticc(CC日志)
    :param date: 时间，格式：yyyymmdd/yyyymmddhh
    :param date_type: 时间单位，可选值：day/hour
    """
    url = YUNAQ_DOMAIN + API_PATH
    params = {
        'time': int(time.time()),
        'domain': domain.strip(),
        'type': log_type.strip(),
        'date_type': date_type.strip(),
        'date': date.strip()
    }
    headers = get_headers(params)
    try:
        # 默认会自动跳转，阻止后提取地址
        response = requests.get(url, headers=headers, params=params,
                                timeout=60, allow_redirects=False)
        if response.status_code != 301:
            print('日志下载链接获取失败，当前状态码为: %s, 返回内容为: %s' % (
                response.status_code, json.loads(response.content)))
            return json.loads(response.content)
        else:
            log_download_url = response.headers['location']
            print('日志下载链接获取成功，当前状态码为: %s, 下载链接为: %s' % (
                response.status_code, log_download_url))

        # 下载并写入至脚本所在目录
        response = requests.get(log_download_url, headers=headers, timeout=60)
        log_name = response.headers['Content-Disposition'].split(
            ';')[1].split('"')[1]
        log_file = open('{}/{}'.format(os.getcwd(), log_name), 'wb+')
        log_file.write(response.content)
        log_file.close()

        print('日志下载成功，已保存至{}'.format(log_name))
    except Exception as error:
        print(error)
        raise Exception(traceback.format_exc())


if __name__ == '__main__':
    log_download('example.com', 'access', '20240320', 'day')
