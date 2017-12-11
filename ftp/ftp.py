import configparser
import ftplib


config = configparser.ConfigParser()
with open('config.ini','r',encoding='utf-8') as config_file:
    config.read_file(config_file)


host = config.get('ftp','host')
username = config.get('ftp','username')
password = config.get('ftp','password')

ftp = ftplib.FTP()
ftp.connect(host)
ftp.encoding = 'utf-8'

ftp.login(username,password)

docs = [] #建立一个list
ftp.dir('',docs.append) #查询目录的值保存到list中

print(docs)

for i in docs:
    #每行是一个长的字符串，
    if i[0]=='-':
        #判断第一个字符是-还是d，是-的话就是文件，如果是d就是文件夹
        print(i.split(" ")[-1])

ftp.close()