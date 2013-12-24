#加速乐开放API

api域名： `jiasule.baidu.com`

## 认证
使用`BASIC AUTH`认证。

加速乐将提供APP_ID以及用于生成密码的SECRET_KEY。

密码产生方式：

* 每次请求的密码均需要重新生成。
* 密码由HMAC签名方式产生，hash方法为sha1，密钥由加速乐提供。
	* 每个用户指定一个密钥，请严密保管。
* 所有POST参数均需要添加时间戳字段，单位为秒。 `"time": "1386800023"`
* 生成签名的信息体为本次请求的全部POST数据，是所有key按照按照a-z的顺序排列的，以&符号连接的url参数字符串，**而不是json或其他格式**。

所有的api的请求都要带上认证信息。

### 请求样例:

```bash
	curl -u <user_id>:<signature> -d '<data>' <url>
	# 字段解释：
	# user_id: 加速乐所提供给用户的API用户id，为24位长度的uuid
	# signature: 通过加速乐提供的密钥(64位长度)将当次发送的data进行签名获得的结果(40位长度)
	# data: 当次发送的全部post数据
	# url: 各个API接口对因url地址
```
示例:

假设用户名为 `51e4c1a18d2a7d10c4841c57`

密钥为 `JruWq5T7FKq1g1VayLhtIqFWiCdiLKfopnAfpNOMi6evGaxxmgO6azgMhqqi6Im2`

需要post的数据为:
```
cdn.directory=true&cdn.html=true&cdn.index=false&cdn.static=true&cdn.waf=true&domain=notsobad.me&email=test@jiasule.com&host=@&ip=1.2.3.4&isp=0&time=1387430886&use_cdn=true
```

计算后的签名为: `8b7ca20e07374c8b5df5913f76e5097b8bbc3832`

目的是更新站点， 即url为 `http://jiasule.baidu.com/api/site/upsert`

用curl操作如下：
```bash
curl -u 51e4c1a18d2a7d10c4841c57:8b7ca20e07374c8b5df5913f76e5097b8bbc3832 \
	-d 'cdn.directory=true&cdn.html=true&cdn.index=false&cdn.static=true&cdn.waf=true&domain=notsobad.me&email=test@jiasule.com&host=@&ip=1.2.3.4&isp=0&time=1387430886&use_cdn=true'  \
	http://jiasule.baidu.com/api/site/upsert/
```

如果一切正常，将返回如下结构的数据
```javascript
	{
		"status": "ok",
		"code": 0,
		"msg": "added",
		"ret": {
			"cname": "9ece8c8f521f6aac.cdn.jiashule.com.",
			"site": "@.jiasule.com",
			"isp": 0
		}
	}
```
如验证失败，将会返回code为401的response，正文中会附带失败原因，包括如下几种：

	'Request without Basic Auth.'				# http头中没有包含basic_auth
	'Basic Auth information is invalid.'		# basic_auth 字段错误
	'Invalid Identity.'							# 用户不存在
	'Account is not permited to connect API.'	# 没有为此用户创建API密钥或不允许此用户连接
	'Timestamp outdated.'						# 时间戳超时
	'Autherize failed.'							# 签名错误，签名匹配失败
	'API Error: uncatched error.'				# 未捕获错误

如请求失败，将会返回如下结构的json数据
```javascript
	{
		"status": "fail",
		"msg": "Upsert Error: The same sub-domain scan only add five single isp line records.",
		"code": 1,
		"error_code": 81002
	}
```

其中code取值为：

 * 1: 提交数据校验失败
   * 此时msg为英文提示，专门提供error_code作为API用户二次开发时的映射key。
 * 2-N: 提交数据与现有数据冲突，各功能自有校验器校验失败
   * 此时msg为中文提示，error_code取值为0

error_code目前取值范围以及代表信息如下:
```javascript
ERROR_CODE = {
		81001: 'Upsert Error: Please add default isp line first.',
		81002: 'Upsert Error: The same sub-domain can only add five single isp line records.',
		81003: 'Upsert Error: System Error, Please try again.',
		82001: 'Delete Error: Invalid isp code.',
		82002: 'Delete Error: Requires valid domain.',
		82003: 'Delete Error: No such host.',
		82004: 'Delete Error: No such isp.',
		83001: 'List Error: No site found under current conditions.',
		84001: 'Purge Error: Requires domain.',
		84002: 'Purge Error: You do not have site in this domain.',
		84003: 'Purge Error: No such host.'
		}
```

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
```javascript
	{
		'status': 'ok',
		'code' : 0,
		'msg' : 'added',
		'ret' : {
			'site' : 'www.notsobad.me',
			'cname' : '28d4198464a841e6.cdn.jiashule.com',
		}
	}
```	
	

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
```javascript	
	{
		"code" : 0,
		"status" : "ok",
		"msg": "",
	}
```
## 网站列表
* api地址: `/api/site/list/`
* method : `post`

请求参数：

* domain （可以为空）
* host (可以为空)
* time

请求样例: 

* `/api/site/list/`
* `/api/site/list/?domain=notsobad.me`
* `/api/site/list/?domain=notsobad.me&host=www`


响应样例
```javascript
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
```	

## 清除缓存
* api地址: `/api/site/purge/`
* method : `post`
* data : json格式数据

请求参数：

* domain
* host (可以为空,为空时则清空整域缓存)
* time


请求数据样例
	
	domain=notsobad.me&host=www
	
	
响应数据样例
```javascript	
	{
		"code" : 0,
		"msg" : "ok"
	}
```
