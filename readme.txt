自动化脚本获取CDH网站上主机运行状态并将其发送邮件到指定邮箱
本版本为linux_64bit版,phantomjs是64位版本，如果需要在32位中运行，请替换phantomjs文件

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


config.ini配置说明，请按实际部署的情况修改config.ini中的以下内容,详情请看manual.txt

2017-11-10: 新建立linux_64bit分支
