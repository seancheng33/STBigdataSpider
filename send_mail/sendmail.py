'''发送邮件功能模块  '''
import configparser
import smtplib, socks, logging, time,sys,os
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class SendMail():
    def __init__(self):
        logging.basicConfig(filename='logs/' + time.strftime('%Y%m%d', time.localtime(time.time())) + '.log',
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            level=logging.DEBUG)

        # 读取配置文件 config.ini
        self.config = configparser.ConfigParser()
        config_file = open("config.ini", 'r')
        self.config.read_file(config_file)

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

        if not self.can_send():
            logging.info(
                time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) +
                "  -->> 时间或次数未达到发信条件，不发信，退出系统")
            sys.exit(0)
        if proxy_url != '' and proxy_port != '':
            # 判断如果代理的地址和端口不为空，即有填写代理服务器的信息，需要使用代理，如果两项都为空即是不需要使用代理服务器
            # 需要使用代理访问网络才可以发送邮件。
            socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, proxy_url, proxy_port)
            socks.wrapmodule(smtplib)

        # 发送邮件，捕捉异常
        try:
            smtpObj = smtplib.SMTP(self.mail_host, 25)
            # 登录邮箱
            smtpObj.login(self.mail_user, self.mail_pass)
            smtpObj.sendmail(self.sender, self.to_receivers + self.cc_receivers, self.message.as_string())
            smtpObj.quit()  # 关闭连接
            logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + "  -->> 邮件发送成功")
        except smtplib.SMTPException:
            logging.error(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + " -->> Error: 无法发送邮件")

    def can_send(self):
        # 获取文件的修改时间
        mtime = time.strftime('%Y%m%d', time.localtime(os.path.getmtime('count')))
        #获取当前时间
        ntime = time.strftime('%Y%m%d', time.localtime(time.time()))
        #如果是修改时间不是当天，内容归零，重新计数
        if mtime != ntime:
            with open('count', 'w') as f:
                f.write('0')
        #修改时间和现在时间相差不超过15分钟(900秒），即是距离上次发邮件间隔不到15分钟，还不能发信
        mtime2 = os.path.getmtime('count')
        ntime2 = time.time()
        if (ntime2-mtime2) < int(self.config.get('mail', 'resend_time')):
            logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + "  -->> 时间间隔未到，邮件不发送")
            return False
        else:
            with open('count', 'r') as f:
                num = f.read()
            if int(num) > int(self.config.get('mail', 'max_send')):
                # 如果计数文件中的内容大于5，表示已经发送过5次邮件，返回不能发信的False
                logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) +
                             "  -->> 当前发信次数"+num+"，已经达到每天邮件发送的最大次数，邮件不再发送")
                return False
            else:
                # 小于等于5，就是还在可以发信的范围，计数加1，次数写入文件中，返回可以发信的True
                num = int(num) + 1
                with open('count', 'w') as f:
                    f.write(str(num))
                return True

    def add_attach(self):
        attach_num = int(self.config.get('attach','attach_num'))
        for i in range(1,attach_num+1):
            attach_file = self.config.get('attach', 'attach'+str(i))
            if attach_file != '':
                self.att1 = MIMEApplication(open(attach_file, 'rb').read())
                self.att1['Content-Type'] = 'application/octet-stream'
                self.att1['Content-Disposition'] = 'attachment;filename="status.txt"'
                self.message.attach(self.att1)

    def read_to_content(self):
        attach_num = int(self.config.get('attach', 'attach_num'))
        content = '<p>以下正文及附件为运行状态不良的各主机状态:<br /><br />'
        for i in range(1, attach_num + 1):
            attach_file = self.config.get('attach', 'attach' + str(i))
            if attach_file != '':
                with open(attach_file,'r',encoding='utf-8') as attach_txt:
                    lines = attach_txt.readlines()
                    for line in lines:
                        content = content + line + '<br />'
                content = content + '<br />'
            content = content + '<br /><br />本邮件内容由python脚本自动采集并发送。</p>'
        return content


#执行程序发送邮件
sendMail = SendMail()
sendMail.send()

#退出脚本
sys.exit(0)