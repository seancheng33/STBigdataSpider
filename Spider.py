import time, sys, configparser, logging
from selenium import webdriver
from collection import Collection
from sendmail import SendMail

logging.basicConfig(filename='logs/' + time.strftime('%Y%m%d', time.localtime(time.time())) + '.log',
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    level=logging.DEBUG)

# 读取配置文件 config.ini
config = configparser.ConfigParser()
config_file = open("config.ini", 'r')
config.read_file(config_file)

url = config.get('spider', 'url')
username = config.get('spider', 'username')
password = config.get('spider', 'password')

cap = webdriver.DesiredCapabilities.PHANTOMJS
cap["phantomjs.page.settings.resourceTimeout"] = 100
cap["phantomjs.page.settings.userAgent"] = (
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
browser = webdriver.PhantomJS(executable_path='phantomjs.exe',desired_capabilities=cap)

# browser = webdriver.Chrome(executable_path='chromedriver.exe')

spiderbrowser = Collection(browser)
spiderbrowser.openurl_and_login(url, username, password)
statusDict = spiderbrowser.getHomeStatus()
statusList = spiderbrowser.statusDetials(statusDict, config.get('spider', 'checkstatus'))
mail_statustable = spiderbrowser.status_table(statusList)
# 用有GUI的浏览器时，才需要用到这个休眠，测试时可以看退出前是否是已经浏览到正确的页面
time.sleep(1)
browser.quit()
logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 退出浏览器，结束脚本')

# 读取发送邮件的各项配置
mail_host = config.get('mail', 'mail_host')  # 服务器
mail_user = config.get('mail', 'mail_name')  # 用户名
mail_pass = config.get('mail', 'mail_password')  # 密码
sender = config.get('mail', 'sender')  # 发送邮件的邮箱地址
to_receivers = config.get('mail', 'to_receivers').split(',')  # 发送名单，转成数组
cc_receivers = config.get('mail', 'cc_receivers').split(',')  # 抄送名单，转成数组
proxy_url = config.get('proxy', 'url')
proxy_port = int(config.get('proxy', 'port'))  # 取出来的值是字符串，记得转成整数类型，不然会报错

sendMail = SendMail(mail_host, mail_user, mail_pass, sender, to_receivers, cc_receivers, mail_statustable)
sendMail.send(proxy_url, proxy_port)

sys.exit(0)
