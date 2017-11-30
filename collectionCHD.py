import time,sys
from bs4 import BeautifulSoup
from selenium import webdriver

browser = webdriver.Chrome(executable_path='chromedriver.exe')

browser.get("http://10.245.254.139:7180/cmf")

# 登录到系统中
browser.find_element_by_id("username").send_keys("admin")
browser.find_element_by_id("password").send_keys("admin")
browser.find_element_by_name("submit").click()
#停留数秒，确保图表的div层有被加载
time.sleep(5)
#获取一些首页的信息

text1 = browser.find_elements_by_xpath('//*[@id="charts-view-id"]/div[1]/div/div/div[5]')
text2 = browser.find_elements_by_xpath('//*[@id="charts-view-id"]/div[2]/div/div/div[5]')
text3 = browser.find_elements_by_xpath('//*[@id="charts-view-id"]/div[3]/div/div/div[5]')
text4 = browser.find_elements_by_xpath('//*[@id="charts-view-id"]/div[4]/div/div/div[5]')

for d in text1:
    a = d.get_attribute('innerHTML')
    soup = BeautifulSoup(a,'lxml')
    b = soup.select('span')
    print(b)
for d in text2:
    a = d.get_attribute('innerHTML')
    soup = BeautifulSoup(a,'lxml')
    b = soup.select('span')
    print(b)
for d in text3:
    a = d.get_attribute('innerHTML')
    soup = BeautifulSoup(a,'lxml')
    b = soup.select('span')
    print(b)
for d in text4:
    a = d.get_attribute('innerHTML')
    soup = BeautifulSoup(a,'lxml')
    b = soup.select('span')
    print(b)

# 点击最上面的菜单，主机->所有主机，进入到页面
browser.find_element_by_link_text("主机").click()
browser.find_element_by_link_text("所有主机").click()

time.sleep(1)

data = browser.find_elements_by_xpath('//*[@id="hostsForm"]/div/div[2]/div[3]/table/tbody/tr')
for d in data[3:]:
    tr = d.get_attribute('innerHTML')
    soup = BeautifulSoup(tr,'lxml')

    lstats = soup.select('td')
    name = lstats[2].text  # 名称
    cpuload = lstats[6].text  # 平均负载
    disk = lstats[7].text # 磁盘使用情况
    memory = lstats[8].text # 物理内存

    print(name+'|'+cpuload+'|'+disk+'|'+memory)

# 用有GUI的浏览器时，才需要用到这个休眠，测试时可以看退出前是否是已经浏览到正确的页面
time.sleep(1)
browser.quit()

sys.exit(0)