import configparser, ftplib

import os


class Ftp_Util():
    def __init__(self):
        config = configparser.ConfigParser()
        with open('config.ini', 'r', encoding='utf-8') as config_file:
            config.read_file(config_file)

        self.host = config.get('ftp', 'host')
        self.username = config.get('ftp', 'username')
        self.password = config.get('ftp', 'password')

        self.type_list = config.get('ftp', 'upload_file_type').split(',')  # 对上传到服务器的文件做了类型限定，按逗号分隔为一个列表

        self.server_path = config.get('ftp', 'server_path')  # 服务器端的路径
        self.local_path = config.get('ftp', 'local_path')  # 下载到本地的路径
        self.src_path = config.get('ftp', 'src_path')  # 需要上传到服务器的路径

        self.ftp = ftplib.FTP()
        self.ftp.connect(self.host)
        self.ftp.encoding = 'utf-8'
        self.ftp.set_debuglevel(1)

    def login_ftp(self):
        try:
            self.ftp.login(self.username, self.password)
            # print("登陆成功")
        except Exception as error:
            print(str(error))

    def close_ftp(self):
        self.ftp.close()

    def to_server_path(self):
        self.login_ftp()

        folder_list = []  # 存储远程文件夹里面的文件的列表
        self.ftp.dir('', folder_list.append)  # 读取文件夹根目录下的内容

        if self.has_folder(folder_list):
            # 文件夹存在，切换到该文件夹
            self.ftp.cwd(self.server_path)

        else:
            # 上面的判断，文件夹不存在，则创建文件夹
            self.ftp.mkd(self.server_path)
            self.ftp.cwd(self.server_path)


        # self.upload_file_to()
        self.download_file_from()

        # print(self.ftp.dir())

        self.close_ftp()

    def upload_file_to(self):
        # 上传文件到指定文件夹
        file_list = []
        for files in os.walk(self.src_path):
            file_list.append(files)

        for item in file_list[0][-1]:
            type = os.path.splitext(item)  # 分离出文件的后缀名，后面做判断和上传隔离
            type_list = self.type_list  # 将配置的后缀名读取为列表
            for t in type_list:
                if t in type[1]:
                    # 列表中的文件分离出来的后缀名匹配配置文件中的后缀名，就上传改文件
                    with open(os.path.join(os.path.abspath(self.src_path), item), 'rb') as file:  # 一定要二进制模式打开，不然有各种报错。
                        self.ftp.storbinary('STOR %s' % item, file)#没有前面的‘STOR空格’，会报错，报未知命令错误

    def download_file_from(self):
        file_list = []
        self.ftp.dir('./', file_list.append)  # 获取当前的文件夹内容
        for item in file_list:
            if item[0] == '-':
                # 字符串的第一个是-的话，就是文件，规则同在linux中用ls -l查询出来的结果，如果是基于win版的ftp服务器，效果未知，未测试
                # 不是用有没有后缀，而是用这种办法来判断是否文件，可以将是文件而没有后缀名的文件也一起判断出来
                # 单纯判断后缀名，就可能把没有后缀名的文件判断为文件夹，这个办法更正确

                filename = item.split(' ')[-1]# 整个字符串按空格分隔，最后一个元素就是文件名和后缀名
                with open(os.path.join(os.path.abspath(self.local_path), filename), 'wb') as file:
                    self.ftp.retrbinary('RETR %s' % filename, file.write) #没有前面的‘RETR空格’，会报错，报未知命令错误

    def has_folder(self, docs_list):
        # 根据文件夹的路径传入，判断该文件夹是否存在
        for item in docs_list:
            if item[0] == 'd':
                name = item.split(' ')[-1]
                if name == self.server_path:
                    return True
        return False


if __name__ == '__main__':
    Ftp_Util().to_server_path()
