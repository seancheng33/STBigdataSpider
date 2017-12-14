import configparser, ftplib, logging, os, time


class Ftp_Util():
    def __init__(self):
        # 读取配置文件
        config = configparser.ConfigParser()
        with open('config.ini', 'r', encoding='utf-8') as config_file:
            config.read_file(config_file)
        # 配置日志文件格式
        logging.basicConfig(filename='logs/' + time.strftime('%Y%m%d', time.localtime(time.time())) + '.log',
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            level=logging.DEBUG)

        self.host = config.get('ftp', 'host')
        self.port = int(config.get('ftp', 'port'))  # 端口号必须是int类型，直接用配置文件里面的值，是str类型，会报错
        self.username = config.get('ftp', 'username')
        self.password = config.get('ftp', 'password')

        self.type_list = config.get('ftp', 'upload_file_type').split(',')  # 对上传到服务器的文件做了类型限定，按逗号分隔为一个列表

        self.server_path = config.get('ftp', 'server_path')  # 服务器端的路径
        self.local_path = config.get('ftp', 'local_path')  # 下载到本地的路径
        # self.local_path = config.get('ftp', 'src_path')  # 需要上传到服务器的路径

        self.ftp = ftplib.FTP()
        self.ftp.connect(self.host, self.port)
        self.ftp.encoding = 'utf-8'
        self.ftp.set_debuglevel(1)

    def login_ftp(self):
        # 登陆ftp
        try:
            logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + "  -->> 发起登陆请求")
            self.ftp.login(self.username, self.password)
            logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + "  -->> 登陆成功")
        except Exception as error:
            logging.error(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + "  -->> 登陆异常：:" + str(error))

    def close_ftp(self):
        # 关闭ftp
        self.ftp.close()
        logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + "  -->> 退出登陆")

    def to_server_path(self):
        # 切换在ftp服务器中的目录，并判断是否有文件夹，没有则创建，有则切换到该目录下

        folder_list = []  # 存储远程文件夹里面的文件的列表
        self.ftp.dir('', folder_list.append)  # 读取文件夹根目录下的内容

        if self.has_folder(folder_list):
            # 文件夹存在，切换到该文件夹
            self.ftp.cwd(self.server_path)
            logging.info(time.strftime('%Y%m%d-%H:%M:%S',
                                       time.localtime(time.time())) + "  -->> 切换到目录 ‘" + self.server_path + "’ 成功。")
        else:
            # 上面的判断，文件夹不存在，则创建文件夹
            logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(
                time.time())) + "  -->> 服务器目录‘" + self.server_path + "’不存在。即将创建文件夹")
            try:  # 创建文件夹
                self.ftp.mkd(self.server_path)
                logging.info(time.strftime('%Y%m%d-%H:%M:%S',
                                           time.localtime(time.time())) + "  -->> 创建目录 ‘" + self.server_path + "’ 成功。")
            except ftplib.error_perm:
                logging.error(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + "  -->> 创建目录失败： " + str(
                    ftplib.error_perm))

            try:  # 切换目录
                self.ftp.cwd(self.server_path)
                logging.info(time.strftime('%Y%m%d-%H:%M:%S',
                                           time.localtime(time.time())) + "  -->> 切换到目录 ‘" + self.server_path + "’ 成功。")
            except ftplib.error_perm:
                logging.error(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + "  -->> 切换目录失败： " + str(
                    ftplib.error_perm))
        # self.ftp.retrlines('LIST') # 效果同ftp.dir()

    def upload_file_to(self):
        # 上传文件到指定文件夹，需切换到该文件夹中
        file_list = []
        for files in os.walk(self.local_path):
            # 获取本地文件夹的内容，将内容追加到列表中,取最后面的一个值就可以了，就是文件名的列表
            file_list = files[-1]
        #
        sfile_list_tmp = []
        sfile_list = []
        self.ftp.dir(sfile_list_tmp.append)  # 追加内容到临时列表
        for sfile in sfile_list_tmp:
            if sfile[0] == '-':  # 判断是否为文件，是则执行下面的内容
                sfile_list.append(sfile.split(' ')[-1])  # 处理后的值添加到列表

        # 两个列表对比，不在服务器列表的，添加到不用确认的列表，在服务器的，添加到需要确认的列表
        need_confirm_list = []  # 需要确认的列表
        unneeded_confirm_list = []  # 不用确认的列表
        for item in file_list:
            print(item)
            if item not in sfile_list:
                unneeded_confirm_list.append(item)
            else:
                need_confirm_list.append(item)

        # 直接上传的部分
        for item in unneeded_confirm_list:
            type = os.path.splitext(item)  # 分离出文件的后缀名，后面做判断和上传隔离
            type_list = self.type_list  # 将配置的后缀名读取为列表
            for t in type_list:
                if t in type[1]:
                    # 列表中的文件分离出来的后缀名匹配配置文件中的后缀名，就上传改文件
                    with open(os.path.join(os.path.abspath(self.local_path), item),
                              'rb') as file:  # 一定要二进制模式打开，不然有各种报错。
                        self.ftp.storbinary('STOR %s' % item, file)  # 没有前面的‘STOR空格’，会报错，报未知命令错误
                    logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) +
                                 "  -->> 上传文件 ‘" + item + "’ 本地路径：" + os.path.abspath(
                        self.local_path) + " >>-->>  服务器路径：" + self.server_path)

        # 循环确定重复文件是否要覆盖的部分
        for item in need_confirm_list:
            operation = input(item + "存在同名文件，是否需要覆盖该文件？（y=覆盖；n=不覆盖且不上传)：")
            loop = True
            while loop:
                if operation == 'y':
                    loop = False
                    with open(os.path.join(os.path.abspath(self.local_path), item),
                              'rb') as file:  # 一定要二进制模式打开，不然有各种报错。
                        self.ftp.storbinary('STOR %s' % item, file)  # 没有前面的‘STOR空格’，会报错，报未知命令错误
                        logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) +
                                     "  -->> 上传文件 ‘" + item + "’ 本地路径：" + os.path.abspath(
                            self.local_path) + " >>-->>  服务器路径：" + self.server_path)
                elif operation == 'n':
                    loop = False
                    print('不覆盖且不上传')
                    logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) +
                                 "  -->> 选择不覆盖且不上传，文件 ‘" + item + "’ 的上传任务被取消。")
                else:
                    print('无效的输入,必须是y/n的其中一种。')
                    operation = input(item + "存在同名文件，是否需要覆盖该文件？（y=覆盖；n=不覆盖且不上传）：")

    def download_file_from(self):
        # 下载功能，需提前切换到需要工作的路径中
        file_list = []
        # self.ftp.retrlines('LIST', file_list.append)#使用这个获取文件夹内容，可以不用指定路径，就是在当前的路径中查找
        self.ftp.dir(file_list.append)  # 获取当前的文件夹内容
        for item in file_list:
            if item[0] == '-':
                # 字符串的第一个是-的话，就是文件，规则同在linux中用ls -l查询出来的结果，如果是基于win版的ftp服务器，效果未知，未测试
                # 不是用有没有后缀，而是用这种办法来判断是否文件，可以将是文件而没有后缀名的文件也一起判断出来
                # 单纯判断后缀名，就可能把没有后缀名的文件判断为文件夹，这个办法更正确
                filename = item.split(' ')[-1]  # 整个字符串按空格分隔，最后一个元素就是文件名和后缀名
                # 查找本地是否存在文件，如果存在，需要用户确认是否覆盖已有文件，是 执行下载，否 不下载，（重命名 在文件名后加上时间后再下载？（是否需要此功能））
                if not os.path.isfile(os.path.join(os.path.abspath(self.local_path), filename)):
                    with open(os.path.join(os.path.abspath(self.local_path), filename), 'wb') as file:
                        self.ftp.retrbinary('RETR %s' % filename, file.write)  # 没有前面的‘RETR空格’，会报错，报未知命令错误
                        logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) +
                                     "  -->> 下载文件 ‘" + filename + "’ 服务器路径：" + self.server_path +
                                     " >>-->>  本地路径：" + os.path.abspath(self.local_path))
                else:
                    operation = input(filename + "存在同名文件，是否需要覆盖该文件？（y=覆盖；n=不覆盖且不下载；r=下载并重命名)：")
                    loop = True
                    while loop:
                        if operation == 'y':
                            loop = False
                            with open(os.path.join(os.path.abspath(self.local_path), filename), 'wb') as file:
                                self.ftp.retrbinary('RETR %s' % filename, file.write)  # 没有前面的‘RETR空格’，会报错，报未知命令错误
                                logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) +
                                             "  -->> 下载文件 ‘" + filename + "’ 服务器路径：" + self.server_path +
                                             " >>-->>  本地路径：" + os.path.abspath(self.local_path))
                        elif operation == 'n':
                            loop = False
                            print('不覆盖且不下载')
                            logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) +
                                         "  -->> 选择不覆盖且不下载，文件 ‘" + filename + "’ 的下载任务被取消。")
                        elif operation == 'r':
                            # 当选择了需要重命名下载文件时，会在原文件名的前面加上年月日
                            loop = False
                            with open(os.path.join(os.path.abspath(self.local_path),
                                                   time.strftime('%Y%m%d%H%M%S',
                                                                 time.localtime(time.time())) + filename),
                                      'wb') as file:
                                self.ftp.retrbinary('RETR %s' % filename, file.write)  # 没有前面的‘RETR空格’，会报错，报未知命令错误
                                logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) +
                                             "  -->> 下载并重命名文件，下载文件 ‘" + filename + "’ 服务器路径：" + self.server_path +
                                             " >>-->>  本地路径：" + os.path.abspath(self.local_path) +
                                             "文件被重命名为：" + time.strftime('%Y%m%d%H%M%S',
                                                                        time.localtime(time.time())) + filename)
                        else:
                            print('无效的输入,必须是y/n/r的其中一种。')
                            operation = input(filename + "存在同名文件，是否需要覆盖该文件？（y=覆盖；n=不覆盖且不下载；r=下载并重命名)：")

    def has_folder(self, docs_list):
        # 根据文件夹的路径传入，判断该文件夹是否存在，适用于服务器端
        for item in docs_list:
            if item[0] == 'd':
                name = item.split(' ')[-1]
                if name == self.server_path:
                    return True
        return False

    def run(self):
        # 运行本程序
        self.login_ftp()
        self.to_server_path()
        self.download_file_from()
        self.upload_file_to()
        self.close_ftp()


if __name__ == '__main__':
    Ftp_Util().run()
