'''发送邮件功能模块  '''
import smtplib, socks, logging,time
from email.header import Header
from email.mime.text import MIMEText

class SendMail():
    def __init__(self, mail_host, mail_user, mail_pass, sender, to_receivers, cc_receivers,mail_content):
        logging.basicConfig(filename=time.strftime('%Y%m%d', time.localtime(time.time())) + '.log', level=logging.DEBUG)
        self.mail_host = mail_host
        self.mail_user = mail_user
        self.mail_pass = mail_pass
        self.sender = sender
        self.to_receivers = to_receivers
        self.cc_receivers = cc_receivers

        # 邮件正文内容
        self.mail_content = '<p>以下为运行状态良好的各主机状态</p>' + mail_content + \
                    '<div style="margin: 10.0px;position: static;">' \
                    '<span style="color: rgb(0,0,0);font-family: Verdana , 微软雅黑 , 宋体 , sans-serif;font-size: 10.0pt;">祝安康<br></span>' \
                    '<span style="color: rgb(0,0,0);font-family: Verdana , 微软雅黑 , 宋体 , sans-serif;font-size: 10.0pt;">业务支持中心-信息管理室</span>' \
                    '<span style="color: rgb(0,0,0);font-family: Verdana , 微软雅黑 , 宋体 , sans-serif;font-size: 10.0pt;"><br>' \
                    '<br>IT工作台：支撑单记录小组--》<br>' \
                    '邮箱地址：<a href="mailto:gyyzzxyw@gd.chinamobile.com" target="_blank">gyyzzxyw@gd.chinamobile.com</a><br>' \
                    '服务热线：13929648834转1<br>' \
                    '以上内容由python脚本自动采集并发送。</div></div></div>'
        # 三个参数：
        # 第一个为文本内容
        # 第二个 plain 设置文本格式，如果需要HTML格式，修改成 html 即可，正文中的内容需要写成html代码的格式
        # 第三个 utf-8 设置编码格式
        # message = MIMEText(text, 'plain', 'utf-8')
        self.message = MIMEText(self.mail_content, 'html', 'utf-8')

        self.message['From'] = Header(self.sender, 'utf-8')  # 这一项显示为发件人的内容
        # message['To'] = Header(str(receivers), 'utf-8')  # 这一项显示为收件人的内容
        self.message['To'] = ','.join(self.to_receivers)
        self.message['Cc'] = ','.join(self.cc_receivers)  # 这一项显示为抄送收件人的内容，下面的发送记得将抄送名单也加进去
        subject = '测试python邮件发送功能'
        self.message['Subject'] = Header(subject, 'utf-8')

    def send(self,proxy_url, proxy_port):
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

