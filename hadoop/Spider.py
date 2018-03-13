import configparser, logging, sys, time

import selenium
from selenium import webdriver
from hadoop.collection import Collection
from hadoop.collectionCDH import CollectionCDH

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
# 配置文件读出来的值都是字符串类型，要做其他类型使用，需要做类型转化
guibrowser = config.get('spider', 'guibrowser')
# 判断是使用什么浏览器插件，True是有gui的chrome，False是无gui的phantomjs
if guibrowser == str(True):
    browser = webdriver.Chrome(executable_path='../lib/chromedriver.exe')
else:
    cap = webdriver.DesiredCapabilities.PHANTOMJS
    cap["phantomjs.page.settings.resourceTimeout"] = 100
    cap["phantomjs.page.settings.userAgent"] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    browser = webdriver.PhantomJS(executable_path='../lib/phantomjs.exe', desired_capabilities=cap)
    # 要设定浏览器的大小，不然被认为是收集的浏览页面大小，会后面报错找不到输入框。原因未知，待测试排查。
    browser.set_window_size(1366, 768)
#设置页面加载超时的时间，下面会捕捉超时异常进行处理
browser.set_page_load_timeout(100)

try:
    spiderbrowser = Collection(browser)
    spiderbrowser2 = CollectionCDH(browser)
    spiderbrowser.openurl_and_login(url, username, password)
    statusDict = spiderbrowser.getHomeStatus()
    home_info = spiderbrowser2.home_info()
    statusList = spiderbrowser.statusDetials(statusDict, config.get('spider', 'checkstatus'))

    host_info = spiderbrowser2.all_host_info()
    average = spiderbrowser2.average_to_file()
    context = home_info + host_info
    context.append(average)

    logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 进入数据写入文件流程')
    spiderbrowser2.writer_to_file(context)
    logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> CDH主机运行信息数据写入文件流程')
    # 需要发信的同时才将数据写到文件中
    spiderbrowser.status_writer_to_file(statusList)
    logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> CDH异常状态数据写入文件流程')
except selenium.common.exceptions.TimeoutException as error:
    #打开页面超时的异常捕捉。
    logging.error(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 网络连接超时:\n' + str(error))
    #形成不能访问页面的状态词典，状态设定为立即发信的存在隐患的状况级别，方便后面的发信程序调用该附件时，判断为需要立即发信的级别。
    error_status = {'web访问错误告警':
                    [{'运行状态': '存在隐患的运行状况',
                     '事件类型': 'web页面连接超时，无法访问',
                     '建议': '请确保与目的主机的网络通畅，确保web服务是否可以正常访问'
                     }]
                    }
    #将错误的状态写入到文件中
    spiderbrowser.status_writer_to_file(error_status)
except Exception as error:
    logging.error(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 脚本异常:\n' + str(error))
finally:
    # 确保浏览器有被退出，避免浏览器因为脚本的异常退出而残留系统消耗资源
    browser.quit()
    logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 退出浏览器')
    # 加个退出，确保脚本有被退出，避免脚本残留系统消耗资源
    sys.exit(0)
