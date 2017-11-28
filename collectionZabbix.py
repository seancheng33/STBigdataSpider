import requests
import json

headers = {'Content-Type': 'application/json-rpc'}
server_ip = '10.245.254.109'

url = 'http://%s/zabbix/api_jsonrpc.php' % server_ip


# 获取token
def getToken(username, passwd):
    username = 'admin'
    passwd = 'zabbix'
    data = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": username,
            "password": passwd
        },
        "id": 0

    }

    request = requests.post(url=url, headers=headers, data=json.dumps(data))
    dict = json.loads(request.text)
    return dict['result']


# 从api获取主机信息，
def getHosts(token_num):
    data = {
        "jsonrpc": "2.0",
        "method": "dhost.get",
        "params": {
                    "output": "extend",
                    "selectDServices": "extend",
                    "druleids": "4"
        },
        "id": 2,
        "auth": token_num,

    }

    request = requests.post(url=url, headers=headers, data=json.dumps(data))
    dict = json.loads(request.content)
    # print (dict['result'])
    return dict['result']


# 整理信息,输出想要的信息，组合成字典，我这边提出ip。
def getProc(data):
    dict = {}
    list = data
    for i in list:
        host = i['extend']
        inter = i['interfaces']
        for j in inter:
            ip = j['extend']
            dict[host] = ip

    return dict


# 排序ip列表
def getData(dict):
    data = dict
    ip_list = []
    for key in data.keys():
        ip = data[key]
        ip_list.append(ip)
    ip_list = list(set(ip_list))
    ip_list.sort()
    return ip_list


# 整理输出ip
def getGroup(ip_list):
    ip_group = {}
    ips = ip_list
    for i in ips:
        print(i)


if __name__ == "__main__":
    # server_ip = '10.37.149.109'
    username = 'admin'
    passwd = 'zabbix'
    token_num = getToken(username, passwd)
    data = getHosts(token_num)
    print(data)

    hosts = getProc(data)
    ip_list = getData(hosts)
    getGroup(ip_list)