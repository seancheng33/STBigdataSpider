import logging,os,shutil,time

class File_Operation:
    def status_writer_to_file(self, status_text):
        file_name = 'status.txt'
        # 组合状态的数据，形成一份txt的文档，将其添加为邮件的附件
        with open(os.path.abspath('../data/' + file_name), 'w', encoding='utf-8') as stxt:
            stxt.write('数据采集时间：' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '\n')
            if len(status_text) > 0:
                for item in status_text:
                    stxt.write(item + '\n')
                    for event_list in status_text[item]:
                        for i in event_list:
                            stxt.write('#' + i + ':' + event_list[i])
                        stxt.write('\n')
            else:
                stxt.write('#CDH集群无异常')

        logging.info(
            time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 数据写入文件完成')
        self.copy_file_to(file_name)


    def copy_file_to(self, filename):
        srcfile = os.path.abspath('../data/' + filename)
        dstfile = self.config.get('spider', 'copy_to_path') + filename
        if not os.path.isfile(srcfile):
            print("%s not exist!" % (srcfile))
            logging.info(
                time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 源文件不存在。')
        else:
            fpath, fname = os.path.split(dstfile)  # 分离文件名和路径
            if not os.path.exists(fpath):
                os.makedirs(fpath)  # 创建路径
            shutil.copyfile(srcfile, dstfile)  # 复制文件
            # print ("copy %s -> %s"%(srcfile,dstfile))
            logging.info(
                time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time())) + ' -->> 复制文件成功。')
