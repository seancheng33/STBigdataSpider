import configparser,requests,json

class CollectionZabbix():
    def __init__(self):
        # 读取配置文件 config.ini
        self.config = configparser.ConfigParser()
        self.config_file = open("config.ini", 'r')
        self.config.read_file(self.config_file)

        self.headers = {'Content-Type': 'application/json-rpc'}
        self.server_ip = self.config.get('zabbix','server_ip')

        self.url = 'http://%s/zabbix/api_jsonrpc.php' % self.server_ip
        self.username = self.config.get('zabbix','username')
        self.passwd = self.config.get('zabbix','password')

        self.group_name = self.config.get('zabbix','group_name')


    # 获取token,后面的获取资料基本上都需要使用到这个token作为登陆用。
    def getToken(self):
        username = self.username
        passwd = self.passwd
        data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": username,
                "password": passwd
            },
            "id": 0

        }

        request = requests.post(url=self.url, headers=self.headers, data=json.dumps(data))
        dict = json.loads(request.text)
        return dict['result']

    def get_group_id(self):
        #需要获取id的主机群组名
        name = self.group_name.strip(',').split(',')
        data = {
                "jsonrpc": "2.0",
                "method": "hostgroup.get",
                "params": {
                    "output": "extend",
                    "filter": {
                        "name": name
                    }
                },
                "auth": self.getToken(),
                "id": 1
            }
        #通讯zabbix的API，得到结果
        output = requests.post(url=self.url, headers=self.headers, data=json.dumps(data))
        # 将返回的结果集是json格式，需要做处理
        dict = json.loads(output.text)
        #取出result中的值，这个才是需要的结果
        results = dict['result']
        #先建立一个数组来存放需要的群组id
        groupid = []
        #遍历结果，取groupid的值
        for result in results:
            groupid.append(result['groupid'])
        return groupid

    def get_group_one(self):
        #获取主机ID
        groupid = self.get_group_id()
        data = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": ["hostid","name"],
                "groupids":groupid,
            },
            "auth": self.getToken(),
            "id": 1
        }
        output = requests.post(url=self.url, headers=self.headers, data=json.dumps(data))
        dict = json.loads(output.text)
        # 取出result中的值，这个才是需要的结果
        results = dict['result']
        # 先建立一个数组来存放需要的群组id
        hostid = []
        # 遍历结果，取groupid的值
        for result in results:
            hostid.append(result['hostid'])
        return hostid

    # def get_host_graph(self,auth):
    #     data = {
    #         "jsonrpc": "2.0",
    #         "method": "graph.get",
    #         "params": {
    #             "output": ["graphid","name"],
    #             "hostids": "10084",
    #         },
    #         "auth": auth,
    #         "id": 1
    #     }
    #     output = requests.post(url=self.url, headers=self.headers, data=json.dumps(data))
    #     dict = json.loads(output.text)
    #     return dict['result']

    def get_host_itemsid(self):
        #hostid = self.get_group_one()
        data = {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": ["itemhid","name","key_"],
                "hostids": "10084",
                "sortfield": "name",
                #用key_的值作为搜索的条件，比用name更精准
                "search":{
                    "name":"Free disk space on $1"
                    #"key_":"vfs.fs.size[/,free]",
                },
            },
            "auth": self.getToken(),
            "id": 1
        }
        output = requests.post(url=self.url, headers=self.headers, data=json.dumps(data))
        dict = json.loads(output.text)
        return dict['result']

    def get_host_history(self):
        data = {
            "jsonrpc": "2.0",
            "method": "history.get",
            "params": {
                "output": "extend",
                "history": 3,
                #根据zabbix的api，history有5个值，默认值是3，
                # 其他的分别是0 - numeric float; 1 - character; 2 - log; 3 - numeric unsigned; 4 - text.
                "itemids": "25973",
                "limit": 10
            },
            "auth": self.getToken(),
            "id": 1
        }
        output = requests.post(url=self.url, headers=self.headers, data=json.dumps(data))
        dict = json.loads(output.text)
        return dict['result']

    def dict_name(self):
        #计较常用的一些需要获取的信息对应的“key_"的值
        dict = ["vm.memory.size[available]",#可用内存
                "system.cpu.load[percpu,avg1]",#CPU使用率，1分钟
                "system.cpu.load[percpu,avg5]",#CPU使用率，5分钟
                "system.cpu.load[percpu,avg15]",#CPU使用率，15分钟
                "vfs.fs.size[/,free]",# 根目录的剩余空间，数值除以1024得到的单位是KB,要得到GB为单位的话，需要除以3次1024
                "vfs.fs.size[/,used]",# 根目录的已用空间，要得到GB为单位的话，需要除以3次1024
                "net.if.in[eth0]",#网卡1的网络接收
                "net.if.in[eth1]",#网卡2的网络接收
                "net.if.in[eth2]",#网卡3的网络接收
                "net.if.in[eth3]",#网卡4的网络接收
                "net.if.out[eth0]",#网卡1的网络发送
                "net.if.out[eth1]",#网卡2的网络发送
                "net.if.out[eth2]",#网卡3的网络发送
                "net.if.out[eth3]",#网卡4的网络发送
                ]
        return dict



zabbix = CollectionZabbix()

print(zabbix.get_group_id())
print(zabbix.get_group_one())
#print(get_host_graph(auth))
print(zabbix.get_host_itemsid())
print(zabbix.get_host_history())