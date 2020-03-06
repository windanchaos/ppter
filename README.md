# ppter概述
## 为什么叫ppter
任性，没有意义，听着挺好听，嗯就这样。
## 可用场景
多地办公，没有固定IP，需办公区对办公区建立VPN，办公区和阿里云建立VPN的场景。

能节省的费用就是两条固定IP的费用。拒我了解的一个固定IP的电信一年30万左右，移动的要10来万。对于小公司来说，一年还是能节约不少钱了。

市面上的其他解决方案，我并不太清楚，如果有更优的免费方案，欢迎告知。
## 文件说明
- aliapi.py 阿里云部分产品api的封装
- ConfigProvider.py 配置相关，读取config.ini转成需要的数据类型 
- Jobs.py 运行的进程 
- Dockerfile docker image镜像构建文件 
- requirement 项目依赖
- config.ini 配置相关
- getDnsInfo.py 获取域名解析信息工具 
- ppter_vpn.py vpn相关代码
- ppter_vps.py vps相关代码
- ppter_dns.py dns解析相关
## 工作原理
使用独立于办公区内部环境的阿里云（或其他共有云），部署redis作为ip交换媒介。
![clip_image001](.\pic\clip_image001.png)
# 前置动作
- 修改正确的config.ini
- 修改正确vpn配置

具体参考[下文](#启动前需要修改的配置)。

# 容器安装
## docker的安装和配置优化
其中user是可以操作docker的普通账户，换成自己的即可
```shell script
bash installDocker.sh user
```
## 监控程序启动操作
```shell
# 镜像打包
docker build -t dns_monitor .
# 启动容器进程
docker run -it -d -v `pwd`/config.ini:/root/config.ini --name monitor dns_monitor
```

# 直接安装
使用的python3。
## 依赖安装
```shell
sudo pip3 install redis request configparser base64
```

## 执行

**不同环境**独立执行：

```python
nohup python3 Jobs.py > log.log &
```

程序会做以下动作：

- 5分钟定时获取一次外网IP地址，并同步到redis上
- 对比IP地址是否有变化，有就执行dns解析、阿里云ipes、本地路由vpn配置变更。ip地址包括本地ip变化和连接端的ip变动。A和B的IP任意变动都会触发本地路由vpn配置。

# 启动前需要修改的配置

config.ini的文件内容，大部分顾名思义。

## Credentials

需要配置具有阿里云vps 、dns操作权限的id和secret。

## 域名解析的配置

[dns] 下的domain设置

- 一个｛'RecordId':'xxx','RR':'record'｝就是一条记录

- 用’|’符号作分隔符。多条记录：｛'RecordId':'4154842768102400','RR':'recordA'｝|｛'RecordId':'4154842768102400','RR':'recordB'｝
  
  其中RR标识map.baidu.com 中的map。
- 按规则添加即可，删除也是

如何获取domain的recordId和RR（主机记录）？

```python
python3 getDnsInfo.py
```

执行后会打印‘baidu.com’的所有解析信息。复制粘贴到json在线解析，找到需要的解析信息。

如果要换域名就修改getDnsInfo.py的内容。

## vpn的设置

前三个参数是路由器的登录地址和账户密码。

redisLocalVpnName 是redis中IP地址的本地标识。

redisRemoteVpnName 是vpn连接远端的标识。

A、B环境的名字需要互换。

A环境的配置：

```python
redisLocalVpnName = A
redisRemoteVpnName = B
```

B环境的配置：

```python
redisLocalVpnName = B
redisRemoteVpnName = A
```
vpn 的配置数据这里没有做到配置文件中，在updata_vpn.py中修改vpn_data，默认vpn-config[0]是对阿里云的vpn设置。vpn-config[1:]之后的是本地对本地的设置。
这类数据可能不同路由器，值是不一样的。需要自己去抓包了解一下了。





## VPS设置

不同环境名字区别开即可。

详细的配置在update_vps.py中，主要修改CreateVpnConnection参数。

```python
CreateVpnConnection = {'Action': 'CreateVpnConnection', 'RegionId': 'cn-hangzhou',
                       'VpnGatewayId': 'XXXXXXX', \
                       'LocalSubnet': '172.16.128.0/20', 'RemoteSubnet': '10.189.51.0/24',
                       'IpsecConfig':str({'IpsecAuthAlg':'sha1'}),
                       'IkeConfig': str({'Psk': 'XXXXXXX','IkeAuthAlg': 'sha1'}), 'CustomerGatewayId': '', 'Name': ''}

```

网关的名字是设置的name取第二个字符（不含）之后的字符，比如现在name为tohzh，则对应网关名hzh。

Psk 要设置成自己定义的值。

特别注意，用户网关如果没有和ipsce关联，就不要提前设置，否则无法新建。



