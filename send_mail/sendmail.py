'''发送邮件功能模块  '''
import configparser
import smtplib, socks, logging, time,sys,os
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class SendMail:
    def __init__(self):
        logging.basicConfig(filename='logs/' + time.strftime('%Y%m%d', time.localtime(time.time())) + '.log',
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            level=logging.DEBUG)

        # 读取配置文件 config.ini
        self.config = configparser.ConfigParser()
        self.config_file = open("config.ini", 'r')
        self.config.read_file(self.config_file)

        self.mail_host = self.config.get('mail', 'mail_host')# 服务器
        self.mail_user = self.config.get('mail', 'mail_name') # 用户名
        self.mail_pass = self.config.get('mail', 'mail_password')# 密码
        self.sender = self.config.get('mail', 'sender') # 发送邮件的邮箱地址
        self.to_receivers = self.config.get('mail', 'to_receivers').split(',')  # 发送名单，转成数组
        self.cc_receivers = self.config.get('mail', 'cc_receivers').split(',')  # 抄送名单，转成数组

        # 邮件正文内容
        self.mail_content = MIMEText(self.read_to_content(), 'html', 'utf-8')
        # 三个参数：
        # 第一个为文本内容
        # 第二个 plain 设置文本格式，如果需要HTML格式，修改成 html 即可，正文中的内容需要写成html代码的格式
        # 第三个 utf-8 设置编码格式
        # message = MIMEText(text, 'plain', 'utf-8')
        # self.message = MIMEText(self.mail_content, 'html', 'utf-8')

        self.message = MIMEMultipart()

        self.message['From'] = Header(self.sender, 'utf-8')  # 这一项显示为发件人的内容
        # message['To'] = Header(str(receivers), 'utf-8')  # 这一项显示为收件人的内容
        self.message['To'] = ','.join(self.to_receivers)
        self.message['Cc'] = ','.join(self.cc_receivers)  # 这一项显示为抄送收件人的内容，下面的发送记得将抄送名单也加进去
        subject = '自动化运维邮件'
        self.message['Subject'] = Header(subject, 'utf-8')
        self.message.attach(self.mail_content)

        self.add_attach_file = 0 #增加了多少个附件，这个属性如果为零，也是判断为不用发信
        self.reset_count = False #需要重新计数的布尔值

        self.add_attach()
        # self.att1 = MIMEText(open('data/status.txt','rb').read(),'base64','utf-8')
        # attach_file = self.config.get('attach','attach1')
        # if attach_file != '':
        #     self.att1 = MIMEApplication(open(attach_file, 'rb').read())
        #     self.att1['Content-Type'] = 'application/octet-stream'
        #     self.att1['Content-Disposition'] = 'attachment;filename="status.txt"'
        #     self.message.attach(self.att1)

    def send(self):

        proxy_url = self.config.get('proxy', 'url')
        proxy_port = int(self.config.get('proxy', 'port'))  # 取出来的值是字符串，记得转成整数类型，不然会报错

        if self.can_send(): #能发信和文件有变动，才会执行发信的操作
            if proxy_url != '' and proxy_port != '':
                # 判断如果代理的地址和端口不为空，即有填写代理服务器的信息，需要使用代理，如果两项都为空即是不需要使用代理服务器
                # 需要使用代理访问网络才可以发送邮件。
                socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, proxy_url, proxy_port)
                socks.wrapmodule(smtplib)

            try:
                smtpObj = smtplib.SMTP(self.mail_host, 25)
                # 登录邮箱
                smtpObj.login(self.mail_user, self.mail_pass)
                smtpObj.sendmail(self.sender, self.to_receivers + self.cc_receivers, self.message.as_string())
                smtpObj.quit()  # 关闭连接
                logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + "  -->> 邮件发送成功")
            except smtplib.SMTPException as error:
                logging.error(
                    time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + " -->> Error: 无法发送邮件" + str(
                        error))

        else:
            logging.info(
                time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) +
                "  -->> 时间或次数未达到发信条件，不发信，退出系统")
            sys.exit(0)


    def can_send(self):
        #如果这次邮件需要添加的附件数为0，也就是说明全部的附件文件都是没有异常的文件，也就表示不用发信，返回不能发信的False
        if self.add_attach_file == 0:
            logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + "  -->> 无异常状态附件添加，邮件不发送")
            return False
        # 获取文件的修改时间
        mtime = time.strftime('%Y%m%d', time.localtime(os.path.getmtime('count')))
        #获取当前时间
        ntime = time.strftime('%Y%m%d', time.localtime(time.time()))

        mtime2 = os.path.getmtime('count')#文件修改时间
        ntime2 = time.time()#现在时间
        #修改时间和现在时间相差不超过设定的秒数，即是距离上次发邮件间隔达不到设定的秒数，返回不能发信的False
        if (ntime2-mtime2) < int(self.config.get('mail', 'resend_time')):
            logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + "  -->> 时间间隔未到，邮件不发送")
            return False
        else:
            if mtime != ntime or self.reset_count:
                # 如果修改时间不是当天，直接赋值为0，内容归零，重新计数
                # 这个时候改写文件的话，会导致文件的修改时间被改变，结果是每天的第一次发信会变成间隔时间未到，无法发信
                # 需要重新计数的条件等于true的时候，也是需要重设计数的值是0
                num = 0
            else:
                with open('count', 'r') as f:
                    num = f.read()
            if int(num) > int(self.config.get('mail', 'max_send')):
                # 如果计数文件中的内容大于设定的次数，表示已经发送过设定的次数的邮件，返回不能发信的False
                logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) +
                             "  -->> 当前发信次数"+num+"，已经达到每天邮件发送的最大次数，邮件不再发送")
                return False
            else:
                attach_num = int(self.config.get('attach', 'attach_num'))

                #在这里将附件的内容写进临时文件
                for i in range(1, attach_num + 1):
                    attach_file = self.config.get('attach', 'attach' + str(i))
                    filename = os.path.basename(attach_file)  # 提取文件名后面用于判断是否需要保存该文件的内容到临时文件

                    if not self.file_diff(attach_file):
                        continue
                    else:
                        with open(attach_file, 'r', encoding='utf-8') as attach_txt:
                            lines = attach_txt.readlines()
                        # 将列表中的内容写到一个临时文件中
                        with open('Sent_' + filename.split('.')[0], 'w', encoding='utf-8') as w:
                            for line in lines:
                                w.write(line)

                # 小于等于5，就是还在可以发信的范围，计数加1，次数写入文件中，返回可以发信的True
                num = int(num) + 1
                with open('count', 'w') as f:
                    f.write(str(num))
                return True

        #判断内容，如果内容和之前发信的内容相同，不发信

    def add_attach(self):
        attach_num = int(self.config.get('attach','attach_num'))
        last_time = self.get_attach_mtime()
        new_mtime = []
        for i in range(1,attach_num+1):
            attach_file = self.config.get('attach', 'attach'+str(i))
            attach_filename = os.path.basename(attach_file)

            if attach_file != '':
                mtime = str(os.path.getmtime(attach_file))
                new_mtime.append(mtime)
                # 取出文件中对应位置的最后修改时间，如果文件中没有对应的时间，列表下标越位，就将改数设为零，
                # 因为该附件是新添加的，未曾有最后修改时间
                try:
                    ltime = last_time[i-1]
                except:
                    ltime = '0'

                if ltime == mtime:
                    continue
                else:
                    with open(attach_file,'r',encoding='utf-8') as attach_txt:
                        lines = attach_txt.readlines()
                        #如果文件中的内容多于两行，就是有异常内容，根据爬虫的写入内容，第一行为爬取的时间，
                        # 如果没有异常，就只有第二行写入无异常，如果有异常内容，文件内容将是大于两行。
                        if len(lines) > 2 and self.file_diff(attach_file):
                            # 如果隐患的内容有变化。重新计数
                            # self.reset_count = True
                            #print(self.file_diff(attach_file))
                            self.att1 = MIMEApplication(open(attach_file, 'rb').read())
                            self.att1['Content-Type'] = 'application/octet-stream'
                            self.att1['Content-Disposition'] = 'attachment;filename='+attach_filename
                            self.message.attach(self.att1)
                            self.add_attach_file +=1
                        else:
                            continue
        with open('lastfile', 'w', encoding='utf-8') as ltimetxt:
            ltimetxt.write(','.join(new_mtime))

    def read_to_content(self):
        last_time = self.get_attach_mtime()
        new_mtime = []
        attach_num = int(self.config.get('attach', 'attach_num'))
        content = '<p>以下正文及附件为运行状态不良的各主机状态:<br /><br />'
        for i in range(1, attach_num + 1):
            attach_file = self.config.get('attach', 'attach' + str(i))
            if attach_file != '':
                mtime = str(os.path.getmtime(attach_file))
                new_mtime.append(mtime)

                try:
                    ltime = last_time[i - 1]
                except:
                    ltime = '0'

                if ltime == mtime:
                    continue
                else:
                    with open(attach_file,'r',encoding='utf-8') as attach_txt:
                        lines = attach_txt.readlines()
                        for line in lines:
                            content = content + line + '<br />'
                    content = content + '<br />'

        content = content + '<br /><br />本邮件内容由python脚本自动采集并发送。</p>'
        return content

    def file_diff(self,filename):
        #对比两个文件的差异，存在差异返回true，否则返回false
        name = os.path.basename(filename).split('.')[0]
        try:
            #打开临时文件
            with open('Sent_'+name, 'r', encoding='utf-8') as infile:
                inall = infile.readlines()
        except FileNotFoundError:
            #抛出文件没有找到异常，就将文件的内容赋值为空，这样就肯定可以得到文件内容有变化，在发信成功后就会添加这个临时文件
            # 这个处理是方便添加新的附件或者附件的文件名改名，导致找不到保存上次信件内容的临时文件
            inall = []
        # 打开需要校对和上传的文件
        with open(filename, 'r', encoding='utf-8') as infile2:
            inall2 = infile2.readlines()

        #处理文件1的内容为一行为一项的列表
        file1_list = []
        for item in inall[1:]:#第一行的时间这个内容不要检查
            item = item.replace("\n", "")
            if '#' in item:
                # 存在#的行数，是各主机状态的行，按照#分成3段内容的一个列表
                item = item.split('#')
                item.remove('')
                file1_list.append(item)
            else:
                file1_list.append(item)
        #处理文件2的内容为一行为一项的列表
        file2_list = []
        for item in inall2[1:]:
            item = item.replace("\n", "")
            if '#' in item:
                #存在#的行数，是各主机状态的行，按照#分成3段内容的一个列表
                item = item.split('#')
                item.remove('')
                file2_list.append(item)
            else:
                file2_list.append(item)

        file1_yellow = []#存放‘存在隐患’的内容
        file1_other = []#存放其他的内容
        for item in file1_list:
            if type(item) == list:#值
                for item2 in item:
                    if '存在隐患' in item2:
                        # print(item)
                        file1_yellow.append(item)
                    else:
                        file1_other.append(item)

        file2_yellow = []#存放‘存在隐患’的内容
        file2_other = []#存放其他的内容
        for item in file2_list:
            if type(item) == list:
                for item2 in item:
                    #将‘存在隐患’的内容存放到一个列表中，其他的内容存放到另外一个表
                    if '存在隐患' in item2:
                        # print(item)
                        file2_yellow.append(item)
                    else:
                        file2_other.append(item)

        #对比两个存放‘存在隐患’内容列表的不同项，保存为一个列表
        result1 = []
        for item in file1_yellow:
            if item not in file2_yellow:
                result1.append(item)
        #需要对比第二次，确保两个存放‘存在隐患’内容列表都没有内容不同
        result2 = []
        for item in file2_yellow:
            if item not in file1_yellow:
                result2.append(item)

        if len(file2_other) == 0:
            # 文件2也就是需要添加为附件的文件中，如果存在有其它的状态信息
            # 按照目前的设置，就是说明有比‘存在隐患’更加严重的告警，需要立刻发信
            # 所以只有这个项为空，才返回false，没有变化
            return False
        elif len(result1) == 0 and len(result2) == 0:
            #两次的对比结果只要有一次有差异，就是两个文件其中一个有变化。
            #  #判断差异项的列表，没有内容，即没有差异项，即两个文件没有变化，存在差异项则有变化
            return False
        else:
            if len(result1) or len(result2):
                #两个结果列表只要有之，就重置计数
                self.reset_count = True
            return True

    def get_attach_mtime(self):
        #如果文件不存在，赋值最后修改时间为空，后面在添加了附件后，会创建该文件并写入内容
        if not os.path.isfile('lastfile'):
            last_time = []
        else:
            #打开文件，获取附件的修改时间，保存为一个列表
            with open('lastfile', 'r', encoding='utf-8') as ltimetxt:
                last_time = ltimetxt.read().strip(',').split(',')
            #print(last_time)
        return last_time

if __name__ == '__main__':
    #执行程序发送邮件
    sendMail = SendMail()
    sendMail.send()
    #退出脚本
    sys.exit(0)