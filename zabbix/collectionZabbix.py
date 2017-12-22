import configparser, logging, time
import selenium
from bs4 import BeautifulSoup
from selenium import webdriver

class CollectionZabbix:
    def __init__(self, browser):
        self.browser = browser
        logging.basicConfig(filename='logs/' + time.strftime('%Y%m%d', time.localtime(time.time())) + '.log',
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            level=logging.DEBUG)

        # 读取配置文件 config.ini
        self.config = configparser.ConfigParser()
        self.config_file = open("config.ini", 'r')
        self.config.read_file(self.config_file)

    def openurl_and_login(self, url, username, password):

        self.browser.get(url)
        logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 打开网址成功。')

        try:
            self.browser.find_element_by_id("name").send_keys(username)
            self.browser.find_element_by_id("password").send_keys(password)
            self.browser.find_element_by_id("enter").click()

        except selenium.common.exceptions.NoSuchElementException:
            # 如果报错说没有找到页面元素，刷新浏览器后再重新执行登陆
            logging.warning(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 页面获取元素失败，刷新页面。')
            self.browser.refresh()
            self.login_to(username, password)

        logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 登陆成功。')
        # 停3秒，让页面可以读取数据完整
        time.sleep(3)
        # return browser

    def get_latest_data(self):
        self.browser.find_element_by_link_text('最新数据').click()
        time.sleep(5)

        data = self.browser.find_element_by_class_name('list-table')
        soup = BeautifulSoup(data.get_attribute('innerHTML'), 'lxml')
        tr_list = soup.findAll('tr')

        for line in tr_list:
            ldata = line.findAll('td')
            if len(ldata) == 4:
                for i in ldata:
                    if len(i.text) > 0:
                        print('主机：',i.text.strip('\n'))
            else:
                for i in ldata:
                    if len(i.text) > 0:
                        print(i.text.strip('\n'))
            print('-----------------')

if __name__ == '__main__':

    config = configparser.ConfigParser()
    config_file = open("config.ini", 'r')
    config.read_file(config_file)
    guibrowser = config.get('zabbix','guibrowser')
    url = config.get('zabbix', 'url')
    username = config.get('zabbix', 'username')
    password = config.get('zabbix', 'password')
    if guibrowser == str(True):
        browser = webdriver.Chrome(executable_path='../lib/chromedriver.exe')
    else:
        cap = webdriver.DesiredCapabilities.PHANTOMJS
        cap["phantomjs.page.settings.resourceTimeout"] = 100
        cap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        browser = webdriver.PhantomJS(executable_path='../lib/phantomjs.exe', desired_capabilities=cap)
        #要设定浏览器的大小，不然被认为是收集的浏览页面大小，会后面报错找不到输入框。原因未知，待测试排查。
        browser.set_window_size(1366,768)
    try:
        zabbix = CollectionZabbix(browser)
        zabbix.openurl_and_login(url,username,password)
        zabbix.get_latest_data()
    finally:
        browser.quit()
