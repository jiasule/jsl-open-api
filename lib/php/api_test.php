<?php
function make_signiture($secret_key,$data) {
	$param_strings = http_build_query($data);
	$hash = hash_hmac('sha1', $param_strings, $secret_key);
	return $hash;
}

function make_header($user, $token) {
	$b64string = base64_encode($user.':'.$token);
	$header = array('Authorization: Basic ' . $b64string,);
	return $header;
}

function http_request($url, $postdata, $header) {
	$ch = curl_init();
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	curl_setopt($ch, CURLOPT_URL, $url);
	curl_setopt($ch, CURLOPT_POSTFIELDS, $postdata);
	curl_setopt($ch, CURLOPT_HTTPHEADER, $header);
	return curl_exec($ch);
}

function main($url, $user, $secret_key, $param) {
	//#加速乐开放API主函数
	ksort($param);
	$token = make_signiture($secret_key,$param);
	$header = make_header($user, $token);
	$postdata = http_build_query($param);
	$ret_cont = http_request($url, $postdata, $header);
	return $ret_cont;
}


//定义操作类型（对应$PARAM_ACTION中的动作，可用动作 list/upsert/purge/del).
$action = 'list'; 
//开放API主要信息，以下信息由加速乐提供.
$API_INFO = array(
		//API接口地址
        'url' => 'http://jiasule.baidu.com/api/site/'.$action.'/', 
		//认证用户名
        'user' => 'xxxxxxxxxxxxxxx', 
		//认证密钥
        'secret_key' => 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 
);

//定义操作域
$domain = 'example.com';
//定义主机头
$host = 'www';
//Web服务器线路
$isp = '0';
//时间戳必需定义
$time = time();

//以下内容值用户可根据情况进行修改.
$PARAM_ACTION = array(
		//列出当前用户指定的所有子域（如不指定域，则列出所有域的子域）
        'list' => array(
                'domain' => $domain,
                'time' => $time,
        ),
		//新增一个域名
        'upsert' => array(
				//域（例：jiasule.com）
                'domain' => $domain,
				//域名主机头(例：www)
                'host' => $host,
				//网站服务器IP
                'ip' => '1.2.3.4',
                'isp' => $isp,
				//联系邮箱
                'email' => 'test@jiasule.com',
				//是否开启加速
                'use_cdn' => 'true', 
				//是否开启Web防火墙
                'cdn.waf' =>'true',
				//是否开启静态资源加速/缓存
                'cdn.static' => 'true',
				//是否开启静态页面加速/缓存
                'cdn.html' => 'true',
				//是否开启首页加速/缓存
                'cdn.index' => 'false',
				//是否开启目录加速/缓存
                'cdn.directory' => 'true',
                'time' => $time,
        ),
		//删除一个域名
        'del' => array(
                'domain' => $domain,
                'host' => $host,
                'isp' => $isp,
                'time' => $time,
        ),
		//刷新某个域名的缓存
        'purge' => array(
                'domain' => $domain,
                'host' => $host,
                'time' => $time,
        ),
);

/* 调用主函数
	函数结构：
	main(API接口地址, 认证用户名, 认证密钥, 操作参数)
*/
$result = main($API_INFO['url'], $API_INFO['user'], $API_INFO['secret_key'], $PARAM_ACTION[$action]);

//显示操作结果
echo $result;
?>
