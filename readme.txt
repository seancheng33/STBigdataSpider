自动化脚本获取CDH网站上主机运行状态并将其发送邮件到指定邮箱
本版本为window版

开发运行环境：
python-3.6.2

所需用到的插件：
beautifulsoup4==4.6.0
bs4==0.0.1
configparser==3.5.0
lxml==4.1.0
PySocks==1.6.7
selenium==3.6.0

可用使用下面的命令批量安装模块：
pip install -r requests.txt


config.ini配置说明，请按实际部署的情况修改config.ini中的以下内容

[spider]#爬取数据功能的配置
url = #需要打开的网址，例：http://127.0.0.1:7180/cmf/home
username = #登录的用户名，例：admin 或 root
password = #登录的密码，例：password 或 123456789
checkstatus = #需要检查的状态的定义字段，具体见下面的列表，建议将下面的''内的内容直接复制过去 例：cm-icon-status-bad-health
[proxy] #邮件功能的网络代理的配置
url = #代理服务器的地址，例：proxy.domain.com 或 127.0.0.1 可以是域名或IP
port = #代理服务器的端口，例：8081 或 8080

[mail] #邮件发送的配置
host = #邮件smtp服务器，测试了139邮箱，可以发送，例：smtp.139.com
name = #登陆用户名，例：username
password = #登陆密码，例：password
sender = #发送者邮箱，例：xxx@139.com
to_receivers = #收件的邮箱地址，可以多个也可以一个，多个邮箱用英文的逗号“,”分隔，例： xxx@163.com,xxx@qq.com，xxx@139.com
cc_receivers = #抄送的邮箱地址，可以多个也可以一个或者留空，多个邮箱用英文的逗号“,”分隔，例： xxx@163.com,xxx@qq.com，xxx@139.com


需要检查状态的定义字段，此内容根据cdh的页面的css分析得出
'cm-icon-status-unknown': '未知',页面的显示图标为
'cm-icon-status-history-not-available': '（未知）',
'cm-icon-status-down': '（未知）',
'cm-icon-status-stopping': '正在停止',
'cm-icon-status-starting': '正在启动',
'cm-icon-status-disabled-health': '已禁用的运行状况',
'cm-icon-status-stopped': '已停止',
'cm-icon-status-none': '无'     在页面的显示图标为灰色
'cm-icon-status-unknown-health': '未知运行状况',
'cm-icon-status-bad-health': '运行状况不良'     在页面的显示图标为红色  （本应用脚本主要就是要抓取这个状态的信息）
'cm-icon-status-good-health': '运行状态良好'    在页面的显示图标为绿色
'cm-icon-status-concerning-health': '存在隐患的运行状况'     页面的显示图标为黄色
