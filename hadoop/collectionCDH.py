import configparser, logging, shutil, time, os, selenium
from bs4 import BeautifulSoup


class CollectionCDH:
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

        self.cpuload_list = []
        self.disk_list = []
        self.memory_list = []
        self.total_disk_list = []
        self.total_memory_list = []

    # 获取一些首页的信息
    def home_info(self):
        time.sleep(3)
        home_list = []
        text1 = self.browser.find_elements_by_xpath('//*[@id="charts-view-id"]/div[1]/div/div/div[5]')
        text2 = self.browser.find_elements_by_xpath('//*[@id="charts-view-id"]/div[2]/div/div/div[5]')
        text3 = self.browser.find_elements_by_xpath('//*[@id="charts-view-id"]/div[3]/div/div/div[5]')
        text4 = self.browser.find_elements_by_xpath('//*[@id="charts-view-id"]/div[4]/div/div/div[5]')

        home_list.append('群集 CPU')
        for d in text1:
            a = d.get_attribute('innerHTML')
            soup = BeautifulSoup(a, 'lxml')
            b = soup.select('span')
            # 得到的内容是多个span，但是只有奇数位的内容是需要的
            home_list.append(b[0]['title'])

        home_list.append('群集磁盘 IO')
        for d in text2:
            a = d.get_attribute('innerHTML')
            soup = BeautifulSoup(a, 'lxml')
            b = soup.select('span')
            # 得到的内容是多个span，但是只有奇数位的内容是需要的
            home_list.append(b[0]['title'])
            home_list.append(b[2]['title'])

        home_list.append('群集网络 IO')
        for d in text3:
            a = d.get_attribute('innerHTML')
            soup = BeautifulSoup(a, 'lxml')
            b = soup.select('span')
            # 得到的内容是多个span，但是只有奇数位的内容是需要的
            home_list.append(b[0]['title'])
            home_list.append(b[2]['title'])

        home_list.append('HDFS IO')
        for d in text4:
            a = d.get_attribute('innerHTML')
            soup = BeautifulSoup(a, 'lxml')
            b = soup.select('span')
            # 得到的内容是多个span，但是只有奇数位的内容是需要的
            home_list.append(b[0]['title'])
            home_list.append(b[2]['title'])
            home_list.append(b[4]['title'])
            home_list.append(b[6]['title'])
        logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 收集首页数据完成。')
        return home_list

    def all_host_info(self):

        info_list = []
        # 点击最上面的菜单，主机->所有主机，进入到页面
        self.browser.find_element_by_link_text("主机").click()
        self.browser.find_element_by_link_text("所有主机").click()
        time.sleep(1)

        data = self.browser.find_elements_by_xpath('//*[@id="hostsForm"]/div/div[2]/div[3]/table/tbody/tr')

        for d in data[3:]:
            tr = d.get_attribute('innerHTML')
            soup = BeautifulSoup(tr, 'lxml')

            lstats = soup.select('td')
            name = lstats[2].text  # 主机名称
            cpuload = lstats[6].text.split('\xa0\xa0')  # 平均负载,去掉两个空格，这里的空格是\xa0
            disk = lstats[7].text.split('/')  # 磁盘使用情况
            memory = lstats[8].text.split('/')  # 物理内存

            info_list.append(
                '主机名称:' + name + '；CPU负载(15分钟):' + cpuload[2] + '% ；已用磁盘空间:' + disk[0].rstrip()+
                '；总磁盘空间:' + disk[1].rstrip() + '；已用物理内存：' + memory[0].rstrip()+
                '；总物理内存：' + memory[1].rstrip())

            #转换磁盘空间的单位
            disk_free = self.change_to_gb(disk[0])
            total_disk_free = self.change_to_gb(disk[1])

            # 将数值添加到列表，后面拿这个来计算平均值
            self.cpuload_list.append(cpuload[2])
            self.disk_list.append(disk_free)  # 删除空格和GiB字符，剩下字符串的数字
            self.memory_list.append(float(memory[0].strip().rstrip('GiB'))) #需要转换成float，不然后面直接调sum会报错
            self.total_disk_list.append(total_disk_free)
            self.total_memory_list.append(float(memory[1].strip().rstrip('GiB')))

        logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 收集所有主机数据完成。')
        return info_list

    def change_to_gb(self,value):
        # 磁盘空间需要把TB换算成GB，因为集群的主机空间可能是TB和GB多种单位混合
        if 'TiB' in value:
            # 字段中包含TiB，表示是TB为单位，乘以1024换算成GB，先将字符串转换为float，方便后面直接用sum求和
            change = float(value.rstrip().rstrip('TiB')) * 1024
        elif 'GiB' in value:
            # 字段中包含GiB，不用换算，直接赋值，先将字符串转换为float，方便后面直接用sum求和
            change = float(value.rstrip().rstrip('GiB'))
        return change


    def average(self, list):
        # 取平均值，方法很多，先用最简单的方法，相加后求值,这样可用不用导入类似pynum之类的外部库
        sum = 0.0
        list_num = len(list)
        for num in list:
            sum = sum + float(num)
        average = sum / float('%.2f' % list_num)
        return float('%.2f' % average)

    def average_to_file(self):
        cpuload_average = self.average(self.cpuload_list) #计算cpu负载平均值
        disk_average = self.average(self.disk_list) #计算cpu负载平均值
        disk_used_total = sum(self.disk_list) #计算磁盘空间总值
        disk_total = sum(self.total_disk_list)
        memory_average = self.average(self.memory_list)
        memory_used_total = sum(self.memory_list) #计算物理内存空间总值
        memory_total = sum(self.total_memory_list)

        average = '群集CPU负载(15分钟)平均值：' + str(cpuload_average) + '%\n群集已用磁盘空间平均值：' +\
                  str(disk_average) + ' GiB；群集总已用磁盘空间：' + str(float('%.2f' % disk_used_total))+ \
                  ' GiB；群集总磁盘空间：' + str(float('%.2f' % disk_total)) +\
                  ' GiB\n群集已用物理内存平均值：' + str(float('%.2f' %memory_average)) + \
                  ' GiB；群集总已用物理内存：'+ str(float('%.2f' %memory_used_total))+\
                  ' GiB；群集总物理内存：'+ str(float('%.2f' % memory_total))+' GiB。'
        logging.info(time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 计算平均值及总值完成。')
        return average

    def writer_to_file(self, info_text):
        file_name = 'CDHstatus.txt'
        # 组合状态的数据，形成一份txt的文档，将其添加为邮件的附件
        with open(os.path.abspath('../data/' + file_name), 'w', encoding='utf-8') as stxt:
            stxt.write('数据采集时间：' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '\n')
            for t in info_text:
                stxt.write(t + '\n')
            logging.info(
                time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 数据写入文件完成')
        self.copy_file_to(file_name)

    def copy_file_to(self, filename):
        srcfile = os.path.abspath('../data/' + filename)
        dstfile = self.config.get('spider', 'copy_to_path') + filename
        if not os.path.isfile(srcfile):
            #print("%s not exist!" % (srcfile))
            logging.error(
                time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 源文件不存在。')
        else:
            fpath, fname = os.path.split(dstfile)  # 分离文件名和路径
            if not os.path.exists(fpath):
                os.makedirs(fpath)  # 创建路径
            shutil.copyfile(srcfile, dstfile)  # 复制文件
            #print ("copy %s -> %s"%(srcfile,dstfile))
            logging.info(
                time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 复制文件成功。')
