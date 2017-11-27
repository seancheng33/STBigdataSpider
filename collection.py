import logging
import time

import os
import selenium
from bs4 import BeautifulSoup
from selenium import webdriver


class Collection():
    def __init__(self, browser):
        self.browser = browser

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
        # return browser

    def login_to(self, username, password):
        # 登录到系统中
        self.browser.find_element_by_id("username").send_keys(username)
        self.browser.find_element_by_id("password").send_keys(password)
        self.browser.find_element_by_name("submit").click()

    def getHomeStatus(self):
        # 获取状态的图标和项目名
        statuspane = self.browser.find_elements_by_class_name("service-status-and-name")

        # 用一个list保存各个状态
        statusDict = []

        for pane in statuspane:
            statuslist = pane.find_element_by_tag_name('i').get_attribute('class')
            # 可以取data-original-title属性拿到中文内容，但是考虑到i18n的语言问题，如果是使用了其他的语言浏览，就导致报错，所以取class属性比较保险
            statusname = pane.find_elements_by_tag_name('a')

            name = statusname[1].text
            link = statusname[0].get_attribute('href')

            # 保存为字典，方便以后的操作使用，statuslist去掉前面没用及相同的25位字符
            dict = {'name': name, 'status': statuslist[25:], 'link': link}
            # 将字典追加到list中
            statusDict.append(dict)
        # 最后的一条数据是Cloudera Management Service的，不需要，上面的采集可能需要再做优化改正
        return statusDict[:-1]

    # 定义查询每页的详情
    def statusDetials(self, statusDict, checkstatus):
        statList = {}
        # statusDict操作这个list里面的字典。得到各项的状态，再做进一步的操作。
        for status in statusDict:
            # 判断条件，根据上面的i的class的内容来判断
            # 红色是cm-icon-status-bad-health，绿色是cm-icon-status-good-health，黄色是cm-icon-status-concerning-health
            if status['status'] == checkstatus:
                # print('Good Status!')
                self.browser.get(status['link'])
                logging.info(
                    time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 打开' + status[
                        'name'] + '页面成功')
                self.browser.find_element_by_link_text('实例').click()
                logging.info(
                    time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 打开' + status[
                        'name'] + '实例页面成功')
                time.sleep(3)

                # 整行tr获取，避免出现数据混乱的情况。数据完整性比按列获取要好
                trs = self.browser.find_elements_by_xpath(
                    '/ html / body / div[7] / form / div / div[2] / div[4] / table / tbody / tr')

                # 用来存指定状态的字典的数组
                sList = []
                for tr in trs[3:]:
                    linecode = tr.get_attribute('innerHTML')
                    # 将上面提取的信息，传给beautifulsoup处理
                    soup = BeautifulSoup(linecode, "lxml")
                    # 状态图标的这个独立拿出来处理，用来判断状态情况，这个得到的是一个数组['tiny','cm-icon','cm-icon-status-xxx-xxx']
                    stat = soup.i['class']
                    # 判断状态, 数组的前两个元素'tiny','cm-icon' 没有判断状态的意义，取第三个元素出来用'cm-icon-status-xxx-xxx'
                    if stat[2] == checkstatus:
                        # 得到的数组的数据结构[复选框，状态的图标，角色类型，状态，主机，授权状态，角色组]
                        lstats = soup.select('td')
                        type = lstats[2].text  # 角色类型
                        name = lstats[4].text  # 主机
                        # 组成有一个字典字段
                        # tmpDict = {'status': stat[2], 'type': type, 'name': name}
                        tmpDict = {'运行状态': self.status_name(stat[2]), '角色类型': type, '主机名': name}
                        #
                        sList.append(tmpDict)
                if len(sList) != 0:
                    statList[status['name']] = sList

                logging.info(
                    time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 收集' + status[
                        'name'] + '数据完成')
        return statList

    def status_name(self, statustype):
        # 字典内容根据分析css表及页面得到以下内容，主要是用三个状态，红色、绿色、黄色
        # 红色是cm-icon-status-bad-health，绿色是cm-icon-status-good-health，黄色是cm-icon-status-concerning-health
        status = {'cm-icon-status-unknown': '未知',
                  'cm-icon-status-history-not-available': '历史记录不可用',
                  'cm-icon-status-down': '停止',
                  'cm-icon-status-stopping': '正在停止',
                  'cm-icon-status-starting': '正在启动',
                  'cm-icon-status-disabled-health': '已禁用的运行状况',
                  'cm-icon-status-stopped': '已停止',
                  'cm-icon-status-none': '无',
                  'cm-icon-status-unknown-health': '未知运行状况',
                  'cm-icon-status-bad-health': '运行状况不良',
                  'cm-icon-status-good-health': '运行状态良好',
                  'cm-icon-status-concerning-health': '存在隐患的运行状况'}
        return status[statustype]

    def status_table(self, text):
        # 组合状态的数据，形成一份table的表格形式，将插入在邮件的正文中
        table_text = text
        html_table = '<table border="1"><tr align="center"><td>事件类型</td><td>运行状态</td><td>角色类型</td><td>主机名</td></tr>'

        for item in table_text.keys():
            event_list = table_text[item]
            list_num = len(event_list)
            line = 1
            for i in event_list:
                html_table += '<tr>'
                for j in i:
                    if line == 1:
                        html_table += '<td rowspan="' + str(list_num) + '">' + item + '</td>'

                    html_table += '<td>' + str(i[j]) + '</td>'
                    line += 1
                html_table += '</tr>'

        html_table += '</table>'

        return html_table

    def status_writer_to_file(self, status_text):
        #只有status_text非空，有内容，才会执行文件的写入功能，不然不写入文件
        if len(status_text) !=0:
            # 组合状态的数据，形成一份txt的文档，将其添加为邮件的附件
            with open(os.path.abspath('data/status.txt'),'w',encoding='utf-8') as stxt:
                stxt.write('数据采集时间：'+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))+'\n')
                for item in status_text:
                    stxt.write(item+'\n')
                    for event_list in status_text[item]:
                        for i in event_list:
                            stxt.write('#'+i+':'+event_list[i])
                        stxt.write('\n')

                logging.info(
                    time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 数据写入文件完成')

    def need_send_mail(self,status_text):
        #状态字典的长度为零，表示没有预算需要采集的信息，不用发信
        if len(status_text) == 0:
            return False

        return True
