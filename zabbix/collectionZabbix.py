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

        all_list = []
        for line in tr_list[1:]:
            # 第一行的表头行不要
            ldata = line.findAll('td')
            status_list = []
            if len(ldata) == 4:
                # 该行是四列的话，是显示主机名和监控项目名的行，否则是显示项目详情的行
                host_name = []
                for i in ldata:
                    if len(i.text) > 0:
                        host_name.append(i.text.strip('\n'))
            else:
                # 遍历项目详情行，得到需要的内容
                status_list = []
                for i in ldata:
                    if len(i.text) > 0:
                        status_list.append(i.text.strip('\n'))
            all_list.append(host_name + status_list)

        tmp_list = []
        for item in all_list:
            if len(item) == 2:
                tmp_list.append(item[0])

        host_info = {}
        for i in tmp_list:
            tmp_l = []
            for item in all_list:
                if i in item:
                    for j in self.check_data():
                        if j in item[1]:
                            in_value = item[2:-1]  # [:-1]去掉最后一个值，改值是‘图形’，不需要
                            if len(in_value):  # in_value有值，就是返回True 就添加到列表中
                                for k in self.check_content():
                                    if k in in_value[0]:
                                        tmp_l.append(in_value)
            host_info[i] = tmp_l

        for item in host_info:
            name = item
            print(name, ':')
            name_list = host_info[item]
            for i in name_list:
                if len(i) == 4:
                    del i[3]
                if 'percentage' in i[0]:
                    # 含percentage是百分比的，可以不要
                    continue
                if '/boot' in i[0]:
                    # /boot的空间查看可以不要
                    continue
                del i[1]
                print(i)

    def check_data(self):
        data = ['CPU', 'Filesystems', 'Memory', 'Network interfaces']
        return data

    def check_content(self):
        data = ['Processor load', 'disk space', 'memory', 'Incoming', 'Outgoing']
        return data


if __name__ == '__main__':

    config = configparser.ConfigParser()
    config_file = open("config.ini", 'r')
    config.read_file(config_file)
    guibrowser = config.get('zabbix', 'guibrowser')
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
        # 要设定浏览器的大小，不然被认为是收集的浏览页面大小，会后面报错找不到输入框。原因未知，待测试排查。
        browser.set_window_size(1366, 768)
    try:
        zabbix = CollectionZabbix(browser)
        zabbix.openurl_and_login(url, username, password)
        zabbix.get_latest_data()
    finally:
        browser.quit()
