import pickle

class Pickle_Util():
    #将一些常用的字典封装成一个plk的文件，适用于一些常量的保存

    #储存方法
    def dump_data(self,data,filename='data.pkl'):
        with open(filename, 'wb') as pickle_file:
            pickle.dump(data, pickle_file)

    #读取方法
    def load_data(self,filename):
        with open(filename, 'rb') as pickle_file:
            unpickle_data = pickle.load(pickle_file)
        return unpickle_data


#即可自己运行又可以被别人调用运行
if __name__ == '__main__':
    status = {'cm-icon-status-unknown': '未知',
              'cm-icon-status-history-not-available': '历史记录不可用',
              'cm-icon-status-down': '停止',
              'cm-icon-status-stopping': '正在停止',
              'cm-icon-status-starting': '正在启动',
              'cm-icon-status-disabled-health': '已禁用的运行状况',
              'cm-icon-status-stopped': '已停止',
              'cm-icon-status-none': '无',
              'cm-icon-status-unknown-health': '未知运行状况',
              'cm-icon-status-bad-health': '运行状况不良',
              'cm-icon-status-good-health': '运行状态良好',
              'cm-icon-status-concerning-health': '存在隐患的运行状况'}
    pu = Pickle_Util()
    pu.dump_data(status)
    print(pu.load_data('data.pkl').get('cm-icon-status-disabled-health'))