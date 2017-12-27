import pickle

class Pickle_Util:
    #将一些常用的字典封装成一个plk的文件，适用于一些常量的保存

    #储存方法
    def dump_data(self,data,filename='zabbixdata.pkl'):
        with open(filename, 'wb') as pickle_file:
            pickle.dump(data, pickle_file)

    #读取方法
    def load_data(self,filename):
        with open(filename, 'rb') as pickle_file:
            unpickle_data = pickle.load(pickle_file)
        return unpickle_data


#即可自己运行又可以被别人调用运行
if __name__ == '__main__':

    # CDH的状态字典，根据分析css得出
    # status = {'cm-icon-status-unknown': '未知',
    #           'cm-icon-status-history-not-available': '历史记录不可用',
    #           'cm-icon-status-down': '停止',
    #           'cm-icon-status-stopping': '正在停止',
    #           'cm-icon-status-starting': '正在启动',
    #           'cm-icon-status-disabled-health': '已禁用的运行状况',
    #           'cm-icon-status-stopped': '已停止',
    #           'cm-icon-status-none': '无',
    #           'cm-icon-status-unknown-health': '未知运行状况',
    #           'cm-icon-status-bad-health': '运行状况不良',
    #           'cm-icon-status-good-health': '运行状态良好',
    #           'cm-icon-status-concerning-health': '存在隐患的运行状况'}

    #zabbix需要的状态字典
    info = {
        'Processor load (1 min average per core)': 'CPU负载（1分钟）',
        'Processor load (5 min average per core)': 'CPU负载（5分钟）',
        'Processor load (15 min average per core)': 'CPU负载（15分钟）',
        'Free disk space on': '可用磁盘空间',
        'Total disk space on': '总磁盘空间',
        'Used disk space on': '已用磁盘空间',
        'Available memory': '可用物理内存',
        'Total memory': '总物理内存',
        'Incoming network traffic on eth0': '网卡1接收',
        'Incoming network traffic on eth1': '网卡2接收',
        'Incoming network traffic on eth2': '网卡3接收',
        'Incoming network traffic on eth3': '网卡4接收',
        'Outgoing network traffic on eth0': '网卡1发送',
        'Outgoing network traffic on eth1': '网卡2发送',
        'Outgoing network traffic on eth2': '网卡3发送',
        'Outgoing network traffic on eth3': '网卡4发送',
        'Incoming network traffic on em1': '网卡1接收',
        'Incoming network traffic on em2': '网卡2接收',
        'Incoming network traffic on em3': '网卡3接收',
        'Incoming network traffic on em4': '网卡4接收',
        'Outgoing network traffic on em1': '网卡1发送',
        'Outgoing network traffic on em2': '网卡2发送',
        'Outgoing network traffic on em3': '网卡3发送',
        'Outgoing network traffic on em4': '网卡4发送',
    }


    pu = Pickle_Util()
    pu.dump_data(info)
    print(pu.load_data('zabbixdata.pkl').get('Processor load (1 min average per core)'))