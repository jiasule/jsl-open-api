#coding=utf8
import hmac
import hashlib
import urllib
import datetime
import urllib2
import base64

param_dict = { 
	# 假设参数
	'param_a': 'a',
	'param_b': 'b',
	'time': datetime.datetime.now().strftime('%s'), # 均需要添加时间戳
}  

def get_sorted_param_string(param_dict):
	''' 输入： 参数字典
		输出： 排序后的参数字符串
	'''
	item_list = param_dict.items()
	item_list.sort(key=lambda x:x[0])
	param_string = urllib.urlencode(item_list)
	return param_string

def make_signiture_token(secret_key, param_dict):
	param_string = get_sorted_param_string(param_dict)
	hashed = hmac.new(secret_key, param_string, hashlib.sha1)
	return hashed.hexdigest()

if __name__ == '__main__':
	user_id = '111111111111'
	secret_key = 'XXXXXXXXXXXXXXXXXXXX'   # secret_key 由加速乐提供
	token = make_signiture_token(secret_key, param_dict)
	print token
