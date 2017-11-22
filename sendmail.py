'''发送邮件功能模块  '''
import smtplib, socks, logging, time
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class SendMail():
    def __init__(self, mail_host, mail_user, mail_pass, sender, to_receivers, cc_receivers):
        logging.basicConfig(filename=time.strftime('%Y%m%d', time.localtime(time.time())) + '.log', level=logging.DEBUG)
        self.mail_host = mail_host
        self.mail_user = mail_user
        self.mail_pass = mail_pass
        self.sender = sender
        self.to_receivers = to_receivers
        self.cc_receivers = cc_receivers

        # 邮件正文内容
        self.mail_content = MIMEText('<p>附件为运行状态不良的各主机状态,本邮件内容由python脚本自动采集并发送。</p>','html', 'utf-8')
        # 三个参数：
        # 第一个为文本内容
        # 第二个 plain 设置文本格式，如果需要HTML格式，修改成 html 即可，正文中的内容需要写成html代码的格式
        # 第三个 utf-8 设置编码格式
        # message = MIMEText(text, 'plain', 'utf-8')
        #self.message = MIMEText(self.mail_content, 'html', 'utf-8')

        self.message = MIMEMultipart()

        self.message['From'] = Header(self.sender, 'utf-8')  # 这一项显示为发件人的内容
        # message['To'] = Header(str(receivers), 'utf-8')  # 这一项显示为收件人的内容
        self.message['To'] = ','.join(self.to_receivers)
        self.message['Cc'] = ','.join(self.cc_receivers)  # 这一项显示为抄送收件人的内容，下面的发送记得将抄送名单也加进去
        subject = '自动化运维邮件'
        self.message['Subject'] = Header(subject, 'utf-8')
        self.message.attach(self.mail_content)

        #self.att1 = MIMEText(open('data/status.txt','rb').read(),'base64','utf-8')
        self.att1 = MIMEApplication(open('data/status.txt','rb').read())
        self.att1['Content-Type'] = 'application/octet-stream'
        self.att1['Content-Disposition'] = 'attachment;filename="status.txt"'
        self.message.attach(self.att1)

    def send(self, proxy_url, proxy_port):

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
            logging.warning(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + " -->> Error: 无法发送邮件")
