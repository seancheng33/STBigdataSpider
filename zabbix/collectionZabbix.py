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
        return dict['result']

    def get_group_one(self,groupid):
        #获取主机ID
        #groupid = self.get_group_id()
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
        return dict['result'] # 返回result中的值，这个才是需要的结果

    def get_host_itemsid(self,hostid,filtername,filtervalue):
        #hostid = self.get_group_one()
        data = {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": ["itemhid","name","key_"],
                "hostids": hostid,
                "sortfield": "name",
                #用key_的值作为搜索的条件，比用name更精准
                "search":{
                    filtername:filtervalue,
                },
            },
            "auth": self.getToken(),
            "id": 1
        }
        output = requests.post(url=self.url, headers=self.headers, data=json.dumps(data))
        dict = json.loads(output.text)
        return dict['result']

    def get_cpuload_history(self,itemids):
        # CPU的数据是float，history返回的对象需要是float，所以独立一个函数
        data = {
            "jsonrpc": "2.0",
            "method": "history.get",
            "params": {
                "output": "extend",
                "history": 0, #CPU的数据是float，这个需要改成0
                #根据zabbix的api，history有5个值，默认值是3，
                # 其他的分别是0 - numeric float; 1 - character; 2 - log; 3 - numeric unsigned; 4 - text.
                "itemids": itemids,
                "limit": 1
            },
            "auth": self.getToken(),
            "id": 1
        }
        output = requests.post(url=self.url, headers=self.headers, data=json.dumps(data))
        dict = json.loads(output.text)
        result = dict['result']
        return result[0]['value']

    def get_memory_history(self,itemids):
        #获取内存和磁盘空间等的历史数据。返回类型是int
        data = {
            "jsonrpc": "2.0",
            "method": "history.get",
            "params": {
                "output": "extend",
                "history": 3, #CPU的数据是float，这个需要改成0
                #根据zabbix的api，history有5个值，默认值是3，
                # 其他的分别是0 - numeric float; 1 - character; 2 - log; 3 - numeric unsigned; 4 - text.
                "itemids": itemids,
                "limit": 1
            },
            "auth": self.getToken(),
            "id": 1
        }
        output = requests.post(url=self.url, headers=self.headers, data=json.dumps(data))
        dict = json.loads(output.text)
        values = []
        # 遍历结果，取值
        for result in dict['result']:
            value = int(result['value'])/1024/1024/1024 #得到GB单位的数值
            values.append(float('%.2f' % value))
        return values

    def get_eth_history(self,itemids):

        #获取内存和磁盘空间等的历史数据。返回类型是int
        data = {
            "jsonrpc": "2.0",
            "method": "history.get",
            "params": {
                "output": "extend",
                "history": 3, #CPU的数据是float，这个需要改成0
                #根据zabbix的api，history有5个值，默认值是3，
                # 其他的分别是0 - numeric float; 1 - character; 2 - log; 3 - numeric unsigned; 4 - text.
                "itemids": itemids ,
                "limit": 1
            },
            "auth": self.getToken(),
            "id": 1
        }
        output = requests.post(url=self.url, headers=self.headers, data=json.dumps(data))
        dict = json.loads(output.text)
        values = []
        # 遍历结果，取值
        for result in dict['result']:
            #value = int(result['value'])/1000/1000 #得到Mbps单位的数值
            value = int(result['value'])
            print(value)
            values.append(float('%.2f' % value))
        return values

    def get_host_free_disk_space_itemid(self, hostid):
        # 获取可用磁盘空间的itemid，因为这里需要比较复杂的差集计算，去掉一些不需要的内容，并且磁盘可用是多个的，独立出来另外计算id
        # 但是会调用到获取get_host_itemsid
        fds = zabbix.get_host_itemsid(hostid, "name", "Free disk space on $1")
        fds2 = zabbix.get_host_itemsid(hostid, "name", "Free disk space on $1 (percentage)")

        fds3 = [item for item in fds if item not in fds2]
        for fd in fds3:
            if fd['key_'] == 'vfs.fs.size[/boot,free]':
                fds3.remove(fd)
        fdsid = []
        for fd in fds3:
            fdsid.append(fd['itemid'])

        return fdsid


    def change_to_itemid(self,results):
        itemids = []
        for result in results:
            itemids.append(result['itemid'])
        return itemids


zabbix = CollectionZabbix()

group_list = zabbix.get_group_id()

for group in group_list:
    groupid = group['groupid']
    groupname = group['name']
    print("主机群组："+groupname)
    host_list = zabbix.get_group_one(groupid)
    #print(host_list)
    for host in host_list:
        hostid = host['hostid']
        hostname = host['name']
        memory_itemsid = zabbix.get_host_itemsid(hostid,'key_','vm.memory.size[available]')
        memory_itemsid = zabbix.change_to_itemid(memory_itemsid)
        cpu1_itemsid = zabbix.get_host_itemsid(hostid, 'key_', 'system.cpu.load[percpu,avg1]')
        cpu1_itemsid = zabbix.change_to_itemid(cpu1_itemsid)
        cpu5_itemsid = zabbix.get_host_itemsid(hostid, 'key_', 'system.cpu.load[percpu,avg5]')
        cpu5_itemsid = zabbix.change_to_itemid(cpu5_itemsid)
        cpu15_itemsid = zabbix.get_host_itemsid(hostid, 'key_', 'system.cpu.load[percpu,avg15]')
        cpu15_itemsid = zabbix.change_to_itemid(cpu15_itemsid)
        free_disk_space_itemsid = zabbix.get_host_free_disk_space_itemid(hostid)

        memory = zabbix.get_memory_history(memory_itemsid)
        cpu1 = zabbix.get_cpuload_history(cpu1_itemsid)
        cpu5 = zabbix.get_cpuload_history(cpu5_itemsid)
        cpu15 = zabbix.get_cpuload_history(cpu15_itemsid)
        ethio = zabbix.get_eth_history(hostid)
        free_disk_spaces = ''
        for i in free_disk_space_itemsid:
            free_disk_space = zabbix.get_memory_history(i)
            free_disk_spaces += str(free_disk_space) +" GB "

        eth_in_itemsid = zabbix.get_host_itemsid(hostid,'key_','net.if.in[e')
        eth_in_itemsid = zabbix.change_to_itemid(eth_in_itemsid)

        eth_out_itemsid = zabbix.get_host_itemsid(hostid, 'key_', 'net.if.out[e')
        eth_out_itemsid = zabbix.change_to_itemid(eth_out_itemsid)

        eth_in = zabbix.get_eth_history(eth_in_itemsid)
        eth_out = zabbix.get_eth_history(eth_out_itemsid)
        print('eth_in:'+str(eth_in))
        print('eth_out:' + str(eth_out))

        text = '''主机名：HOSTNAME;可用物理内存：MEMORY GB; CPU平均负载（1分钟 5分钟 15分钟）：CPU1% CPU5% CPU15%;
        可用磁盘空间：FDS;网络传输： 发送：ETHOUT Mbps 接收：ETHIN Mbps'''
        text = text.replace('HOSTNAME',str(hostname))
        text = text.replace('MEMORY', str(memory))
        text = text.replace('CPU1', str(cpu1))
        text = text.replace('CPU5', str(cpu5))
        text = text.replace('CPU15', str(cpu15))
        text = text.replace('FDS', str(free_disk_spaces))
        text = text.replace('ETHOUT', str(eth_out))
        text = text.replace('ETHIN', str(eth_in))

        print(text)



        # print("主机名："+str(hostname)+";可用物理内存："+str(memory)+
        #       "GB;CPU平均负载（1分钟 5分钟 15分钟）："+str(cpu1)+"% "+str(cpu5)+"% "+str(cpu15)+
        #       "%;可用磁盘空间："+str(free_disk_spaces)+
        #       ";网络传输： 发送："+str(eth_out)+ "Mbps 接收："+str(eth_in)+"Mbps")
