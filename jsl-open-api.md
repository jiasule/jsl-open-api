#加速乐开放API

api域名： `jiasule.baidu.com`

## 认证
使用`BASIC AUTH`认证。

加速乐将提供帐号以及用于生成密码的随机字符串密钥。

密码产生方式：

* 每次请求的密码均需要重新生成。
* 密码由HMAC签名方式产生，hash方法为sha1，密钥由加速乐提供。
	* 每个用户指定一个密钥，请严密保管。
* 所有POST参数均需要添加时间戳字段，单位为秒。 `"time": "1386800023"`
* 生成签名的信息体为本次请求的全部POST数据，是所有key按照按照a-z的顺序排列的，以&符号连接的url参数字符串，**而不是json或其他格式**。

所有的api的请求都要带上认证信息。

### Basic Auth密码生成样例（`Python`）

	import hmac
	import hashlib
	import urllib
	import datetime
	
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
		hashed = hamc.new(secret_key, param_string, hashlib.sha1)
		return hashed.hexdigest()

	secret_key = 'XXXXXXXXXXXXXXXXXXXX'   # secret_key 由加速乐提供
	token = make_signiture_token(secret_key, param_dict)

### Basic Auth使用示例（`Python`）

	import urllib2
	import base64

	def get_header(username, token):
		""" Basic Auth请求头
		header 格式为: {'AUTHORIZATION': 'BASIC ' + base64.b64encode('username:token')}
		"""
		header = {}
		b64string = b64encode('%s:%s' % (user, token))
		header['AUTHORIZATION'] = 'Basic %s' % b64string
		return header

	url = "http://xxxxxxxxxxxxx" # 加速乐API地址
	header = get_header(username, token) #此处username为加速乐提供，token即为上方样例所生成
	req = urllib2.Request(url, data, headers=header)
	result = urllib2.urlopen(req).read()


## 添加、修改网站配置
* api地址：`/api/site/upsert/`
* method : `post`
* data : 请求参数

如果网站尚未添加，则会自动添加，否则修改对应记录。

* doamin
	* 根域
* host
	* 子域名
* ip
	* 源站ip
* isp
	* 使用的isp线路
	* 取值范围 `[0, 1, 2, 3] #0: 默认, 1: 联通, 2: 电信, 3:移动`
* time
	* 当前时间戳
* email
* use_cdn
	* false，不使用cdn
	* true, 使用cdn
* cdn.waf 
	* 是否开启waf，true/false
* cdn.static
	* 是否开启静态资源缓存，true/false
* cdn.html
	* 是否开启html文件缓存, true/false
* cdn.index
	* 是否开启首页缓存
* cdn.directory
	* 是否开启目录缓存
	
请求数据样例

	cdn.directory=true&cdn.html=true&cdn.index=false&cdn.static=true&cdn.waf=true&domain=notsobad.me&email=root%40notsobad.me&host=www&ip=124.2.3.4&isp=0&time=1386903539&uniq_id=1234&use_cdn=true

响应样例
	
	{
		'status': 'ok',
		'code' : 0,
		'msg' : 'added',
		'ret' : {
			'site' : 'www.notsobad.me',
			'cname' : '28d4198464a841e6.cdn.jiashule.com',
		}
	}
	
	

## 删除网站配置
* api地址：`/api/site/del/`
* method : `post`
* data : 请求参数

请求参数说明：

* domain
	* 根域	
* host（可选）
	* 待删除的子域名
* isp（可选）
	* 待删除的isp节点
	* 取值范围 `[0, 1, 2, 3] #0: 默认, 1: 联通, 2: 电信, 3:移动`
* time
	* 时间戳

注意：当参数中无isp时会删除当前host下所有配置。同理，参数中无host时，则会删除整个domain下所有配置

请求数据样例

	domain=notsobad.me&host=www&isp=0&time=1386904356

响应数据样例
	
	{
		"code" : 0,
		"status" : "ok",
		"msg": "",
	}

## 网站列表
* api地址: `/api/site/list/`
* method : `post`

请求参数：

* domain （可以为空）
* host (可以为空)

请求样例: 

* `/api/site/list/`
* `/api/site/list/?domain=notsobad.me`
* `/api/site/list/?domain=notsobad.me&host=www`


响应样例

	{
		"code" : 0,
		"status" : "ok",
		"ret" : [
			{
				'domain' : 'notsobad.me',
				'host' : 'www',
				'ip' : ['124.2.3.4'],
				'email' : 'root@notsobad.me',
				'use_cdn' : true,
				'uniq_id' : 1234,
				'cdn.waf' : true,
				'cdn.static' : true,
				'cdn.html' : true,
				'cdn.index' : false,
				'cdn.directory' : false
			},
			{
				'domain' : 'notsobad.me',
				'host' : 'bbs',
				'ip' : ['124.2.3.4'],
				'email' : 'root@notsobad.me',
				'use_cdn' : true,
				'uniq_id' : 1234,
				'cdn.waf' : true,
				'cdn.static' : true,
				'cdn.html' : true,
				'cdn.index' : false,
				'cdn.directory' : false
			}
		] 
	}
	

## 清除缓存
* api地址: `/api/site/purge/`
* method : `post`
* data : json格式数据

请求参数：

* domain
* host (可以为空,为空时则清空整域缓存)


请求数据样例
	
	domain=notsobad.me&host=www
	
	
响应数据样例
	
	{
		"code" : 0,
		"msg" : "ok"
	}
