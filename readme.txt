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


config.ini配置说明，修改config.ini.backup为config.ini,然后请按实际部署的情况修改config.ini中的以下内容,详情请看manual.txt

2017-12-04：完成hadoop的CDH的首页和所有主机信息功能的获取
2017-12-28：添加判断附件文件的最后修改时间，如果时间与文件lasttime中的时间相同，表示文件未更新，不添加为附件，同时该文件内容不会被写入到正文中。
2017-11-22:发信间隔时间、发信次数判断，调整Spider.py部分代码至sendmail.py中。为发信功能剥离独立做准备。
2017-11-22:
新增功能：
1、判断是否有内容需要发信，调整需要发信才写入文件进行保存
2、发信是否达到设定阈值，达到则不再发信。
3、修改浏览器插件的使用为配置文件可选有GUI和无GUI，数据采集后不再是直接写在正文中，改为保存在data文件夹中的status.txt文件，添加为邮件附件的形式发送。
2017-11-10: 新增linux_64bit分支，添加了linux_64位版本,development分支是无浏览器界面的windows版。
2017-11-08: 增加start.cmd脚本，可于window下在计划任务中添加执行定时任务用。