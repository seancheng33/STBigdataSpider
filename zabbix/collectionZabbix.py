import requests
import json

headers = {'Content-Type': 'application/json-rpc'}
server_ip = '10.245.254.109'

url = 'http://%s/zabbix/api_jsonrpc.php' % server_ip


# 获取token,后面的获取资料基本上都需要使用到这个token作为登陆用。
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

def get_group_id(auth):
    data = {
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {
                "output": "extend",
                "filter": {
                    "name": [
                        "Zabbix servers",
                        "linux servers"
                    ]
                }
            },
            "auth": auth,
            "id": 1
        }

    output = requests.post(url=url, headers=headers, data=json.dumps(data))
    dict = json.loads(output.text)
    return dict['result']

def get_group_one(auth):
    data = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["hostid","name"],
            "groupids":["2","4"],
        },
        "auth": auth,
        "id": 1
    }
    output = requests.post(url=url, headers=headers, data=json.dumps(data))
    dict = json.loads(output.text)
    return dict['result']

def get_host_graph(auth):
    data = {
        "jsonrpc": "2.0",
        "method": "graph.get",
        "params": {
            "output": ["graphid","name"],
            "hostids": "10084",
        },
        "auth": auth,
        "id": 1
    }
    output = requests.post(url=url, headers=headers, data=json.dumps(data))
    dict = json.loads(output.text)
    return dict['result']

def get_host_itemsid(auth):
    data = {
        "jsonrpc": "2.0",
        "method": "item.get",
        "params": {
            "output": ["itemhid","name"],
            "hostids": "10084",
            "sortfield": "name"
        },
        "auth": auth,
        "id": 1
    }
    output = requests.post(url=url, headers=headers, data=json.dumps(data))
    dict = json.loads(output.text)
    return dict['result']

def get_host_history(auth):
    data = {
        "jsonrpc": "2.0",
        "method": "history.get",
        "params": {
            "output": "extend",
            "history": 3,
            "itemids": "23316",
            "limit": 10
        },
        "auth": auth,
        "id": 1
    }
    output = requests.post(url=url, headers=headers, data=json.dumps(data))
    dict = json.loads(output.text)
    return dict['result']

auth = getToken('admin','zabbix')
#print(get_group_id(auth))
#print(get_group_one(auth))
#print(get_host_graph(auth))
#print(get_host_itemsid(auth))
print(get_host_history(auth))