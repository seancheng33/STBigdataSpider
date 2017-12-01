import configparser
import logging
import shutil
import time,sys

import os
import selenium
from bs4 import BeautifulSoup
from selenium import webdriver


class CollectionCHD():
    def __init__(self, browser):
        self.browser = browser

        logging.basicConfig(filename='logs/chd' + time.strftime('%Y%m%d', time.localtime(time.time())) + '.log',
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            level=logging.DEBUG)

        # 读取配置文件 config.ini
        self.config = configparser.ConfigParser()
        self.config_file = open("config.ini", 'r')
        self.config.read_file(self.config_file)

        self.cpuload_list = []
        self.disk_list = []
        self.memory_list = []

    def openurl_and_login(self, url, username, password):

        self.browser.get(url)
        logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 打开网址成功。')

        try:
            self.login_to(username, password)
        except selenium.common.exceptions.NoSuchElementException:
            # 如果报错说没有找到页面元素，刷新浏览器后再重新执行登陆
            logging.warning(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 页面获取元素失败，刷新页面。')
            self.browser.refresh()
            self.login_to(username, password)

        logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 登陆成功。')
        # 停3秒，让页面可以读取数据完整
        time.sleep(3)

    def login_to(self, username, password):
        # 登录到系统中
        self.browser.find_element_by_id("username").send_keys(username)
        self.browser.find_element_by_id("password").send_keys(password)
        self.browser.find_element_by_name("submit").click()

#获取一些首页的信息
    def home_info(self,browser):
        home_list = []
        text1 = browser.find_elements_by_xpath('//*[@id="charts-view-id"]/div[1]/div/div/div[5]')
        text2 = browser.find_elements_by_xpath('//*[@id="charts-view-id"]/div[2]/div/div/div[5]')
        text3 = browser.find_elements_by_xpath('//*[@id="charts-view-id"]/div[3]/div/div/div[5]')
        text4 = browser.find_elements_by_xpath('//*[@id="charts-view-id"]/div[4]/div/div/div[5]')

        home_list.append('群集 CPU')
        for d in text1:
            a = d.get_attribute('innerHTML')
            soup = BeautifulSoup(a,'lxml')
            b = soup.select('span')
            home_list.append(b[0]['title'])

        home_list.append('群集磁盘 IO')
        for d in text2:
            a = d.get_attribute('innerHTML')
            soup = BeautifulSoup(a,'lxml')
            b = soup.select('span')
            home_list.append(b[0]['title'])
            home_list.append(b[2]['title'])

        home_list.append('群集网络 IO')
        for d in text3:
            a = d.get_attribute('innerHTML')
            soup = BeautifulSoup(a,'lxml')
            b = soup.select('span')
            home_list.append(b[0]['title'])
            home_list.append(b[2]['title'])

        home_list.append('HDFS IO')
        for d in text4:
            a = d.get_attribute('innerHTML')
            soup = BeautifulSoup(a,'lxml')
            b = soup.select('span')
            home_list.append(b[0]['title'])
            home_list.append(b[2]['title'])
            home_list.append(b[4]['title'])
            home_list.append(b[6]['title'])
        logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 收集首页数据完成。')
        return home_list

    def all_host_info(self,browser):
        info_list = []
        # 点击最上面的菜单，主机->所有主机，进入到页面
        browser.find_element_by_link_text("主机").click()
        browser.find_element_by_link_text("所有主机").click()
        time.sleep(1)

        data = browser.find_elements_by_xpath('//*[@id="hostsForm"]/div/div[2]/div[3]/table/tbody/tr')

        for d in data[3:]:
            tr = d.get_attribute('innerHTML')
            soup = BeautifulSoup(tr,'lxml')

            lstats = soup.select('td')
            name = lstats[2].text  #  主机名称
            cpuload = lstats[6].text.split('\xa0\xa0')  # 平均负载,去掉两个空格，这里的空格是\xa0
            disk = lstats[7].text.split('/') # 磁盘使用情况
            memory = lstats[8].text.split('/') # 物理内存

            info_list.append('主机名称:'+name+'；CPU负载(15分钟):'+cpuload[2]+'；已用磁盘空间:'+disk[0].rstrip()+'；已用物理内存：'+memory[0].rstrip())
            #将数值添加到列表，后面拿这个来计算平均值
            self.cpuload_list.append(cpuload[2])
            self.disk_list.append(disk[0].strip().rstrip('GiB')) #删除空格和GiB字符，剩下字符串的数字
            self.memory_list.append(memory[0].strip().rstrip('GiB'))
        logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 收集所有主机数据完成。')
        return info_list

    def average(self,list):
        #取平均值，方法很多，先用最简单的方法，相加后求值,这样可用不用导入类似numpy之类的外部库
        sum = 0.0
        list_num = len(list)
        for num in list:
            sum = sum+float(num)
        average = sum / float('%.2f' % list_num)
        logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 计算平均值数据完成。')
        return float('%.2f' %average)

    def average_to_file(self):
        cpuload_average = self.average(self.cpuload_list)
        disk_average = self.average(self.disk_list)
        memory_average = self.average(self.memory_list)
        average = '群集CPU负载平均值:'+str(cpuload_average)+'%；群集已用磁盘空间平均值:'\
                  +str(disk_average)+' GiB；群集已用物理内存平均值:'+str(memory_average)+' GiB。'
        return average

    def writer_to_file(self, info_text):
        file_name = 'status2.txt'
        # 组合状态的数据，形成一份txt的文档，将其添加为邮件的附件
        with open(os.path.abspath('data/'+file_name),'w',encoding='utf-8') as stxt:
            stxt.write('数据采集时间：'+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))+'\n')
            for t in info_text:
                stxt.write(t+'\n')
            logging.info(
                    time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 数据写入文件完成')
        self.copy_file_to(file_name)

    def copy_file_to(self,filename):
        srcfile = os.path.abspath('data/'+filename)
        dstfile = self.config.get('spider', 'copy_to_path')+ filename
        if not os.path.isfile(srcfile):
            print ("%s not exist!"%(srcfile))
            logging.info(
                time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 源文件不存在。')
        else:
            fpath,fname=os.path.split(dstfile)    #分离文件名和路径
            if not os.path.exists(fpath):
                os.makedirs(fpath)                #创建路径
            shutil.copyfile(srcfile,dstfile)      #复制文件
            #print ("copy %s -> %s"%(srcfile,dstfile))
            logging.info(
                time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 复制文件成功。')

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


spiderbrowser = CollectionCHD(browser)
spiderbrowser.openurl_and_login(url, username, password)
home_info = spiderbrowser.home_info(browser)
host_info = spiderbrowser.all_host_info(browser)
average = spiderbrowser.average_to_file()

context = home_info+host_info
context.append(average)
spiderbrowser.writer_to_file(context)

# 用有GUI的浏览器时，才需要用到这个休眠，测试时可以看退出前是否是已经浏览到正确的页面
time.sleep(1)
browser.quit()

#加个退出，确保脚本有被退出，避免脚本残留系统消耗资源
sys.exit(0)
