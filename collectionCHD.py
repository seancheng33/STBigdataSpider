import time, xlsxwriter

from bs4 import BeautifulSoup
from selenium import webdriver

headers = {
    'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

browser = webdriver.Chrome(executable_path='chromedriver.exe')
#browser = webdriver.PhantomJS(executable_path='phantomjs.exe',headers=headers)
# 先行测试用，最终须修改成无GUI的PhantomJS浏览器

browser.get("http://10.245.254.139:7180/cmf/home")

# 登录到系统中
browser.find_element_by_id("username").send_keys("admin")
browser.find_element_by_id("password").send_keys("admin")
browser.find_element_by_name("submit").click()
# 点击最上面的菜单，主机->所有主机，进入到页面
browser.find_element_by_link_text("主机").click()
browser.find_element_by_link_text("所有主机").click()

time.sleep(1)

# 脚本运用的当前时间作为文件名,格式为 年月日-时分秒
filename = time.strftime('%Y%m%d', time.localtime(time.time()))
workbook = xlsxwriter.Workbook(filename + '.xlsx')
worksheet = workbook.add_worksheet(filename)

# 设置列宽,
worksheet.set_column('A:A', 20)
worksheet.set_column('B:B', 20)
worksheet.set_column('C:C', 20)
worksheet.set_column('D:D', 20)
worksheet.set_column('E:E', 20)
worksheet.set_column('F:F', 20)
# worksheet.set_column('G:G', 20)

# 设置标题头样式，字体加粗，水平对齐,上下居中，边框1像素
titlecss = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
contextcss = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1, })

# # 不按行爬取数据，按列爬取，再将各数值填写到excel表中
# # 名称列
# names = browser.find_elements_by_class_name("名称")
# i = 1
# for name in names:
#     if i == 1:
#         css = titlecss
#     else:
#         css = contextcss
#     worksheet.write('A' + str(i), name.text, css)
#     i += 1
# # ip列
# ipadds = browser.find_elements_by_class_name("ip")
# i = 1
# for ipadd in ipadds:
#     if i == 1:
#         css = titlecss
#     else:
#         css = contextcss
#     worksheet.write('B' + str(i), ipadd.text, css)
#     i += 1
#
# loadaverages = browser.find_elements_by_class_name("平均负载")
# i = 1
# for loadaverage in loadaverages:
#     if i == 1:
#         css = titlecss
#     else:
#         css = contextcss
#     worksheet.write('C' + str(i), loadaverage.text, css)
#     i += 1
#
# dfs = browser.find_elements_by_class_name("磁盘使用情况")
# i = 1
# for df in dfs:
#     if i == 1:
#         css = titlecss
#     else:
#         css = contextcss
#     worksheet.write('D' + str(i), df.text, css)
#     i += 1
#
# memorys = browser.find_elements_by_class_name("物理内存")
# i = 1
# for memory in memorys:
#     if i == 1:
#         css = titlecss
#     else:
#         css = contextcss
#     worksheet.write('E' + str(i), memory.text, css)
#     i += 1
#
# swaps = browser.find_elements_by_class_name("交换空间")
# i = 1
# for swap in swaps:
#     if i == 1:
#         css = titlecss
#     else:
#         css = contextcss
#     worksheet.write('F' + str(i), swap.text, css)
#     i += 1

data = browser.find_elements_by_xpath('//*[@id="hostsForm"]/div/div[2]/div[3]/table/tbody/tr')
for d in data[3:]:
    tr = d.get_attribute('innerHTML')
    soup = BeautifulSoup(tr,'lxml')

    print(soup.select('td'))

# 用有GUI的浏览器时，才需要用到这个休眠，测试时可以看退出前是否是已经浏览到正确的页面
time.sleep(1)
browser.quit()
