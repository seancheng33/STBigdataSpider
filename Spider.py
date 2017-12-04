import configparser,logging,sys,time
from selenium import webdriver
from collection import Collection
from collectionCDH import CollectionCDH

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
#配置文件读出来的值都是字符串类型，要做其他类型使用，需要做类型转化
guibrowser = config.get('spider', 'guibrowser')
#判断是使用什么浏览器插件，True是有gui的chrome，False是无gui的phantomjs
if guibrowser == str(True):
    browser = webdriver.Chrome(executable_path='chromedriver.exe')
else:
    cap = webdriver.DesiredCapabilities.PHANTOMJS
    cap["phantomjs.page.settings.resourceTimeout"] = 100
    cap["phantomjs.page.settings.userAgent"] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    browser = webdriver.PhantomJS(executable_path='phantomjs.exe', desired_capabilities=cap)
    #要设定浏览器的大小，不然被认为是收集的浏览页面大小，会后面报错找不到输入框。原因未知，待测试排查。
    browser.set_window_size(1366,768)

try:
    spiderbrowser = Collection(browser)
    spiderbrowser2 = CollectionCDH(browser)
    spiderbrowser.openurl_and_login(url, username, password)
    statusDict = spiderbrowser.getHomeStatus()
    home_info = spiderbrowser2.home_info()
    statusList = spiderbrowser.statusDetials(statusDict, config.get('spider', 'checkstatus'))

    host_info = spiderbrowser2.all_host_info()
    average = spiderbrowser2.average_to_file()
    context = home_info+host_info
    context.append(average)
    logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 进入数据写入文件流程')
    spiderbrowser2.writer_to_file(context)
    logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 主机运行信息数据写完成')

    #需要发信的同时才将数据写到文件中
    spiderbrowser.status_writer_to_file(statusList)
    logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 异常状态数据写完成')
    # 用有GUI的浏览器时，才需要用到这个休眠，测试时可以看退出前是否是已经浏览到正确的页面
except:
    logging.error(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 脚本未知异常，运行终止')
finally:
    # 浏览器的退出加在finally，确保浏览器始终会被退出，防止脚本异常导致浏览器没有退出，浪费系统资源
    browser.quit()
    logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 退出浏览器')
    logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 退出脚本运行')
    #加个退出，确保脚本有被退出，避免脚本残留系统消耗资源
    sys.exit(0)
