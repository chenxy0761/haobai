# -*- coding: utf-8 -*-

from ftplib import FTP
import configparser as conf
# import ConfigParser as conf
import datetime
import time
import os
import logging
import sys

# 加载配置文件
#os.chdir("./")
cf = conf.ConfigParser()
cf.read(os.path.dirname(os.path.realpath(sys.argv[0]))+"/conf/config.conf")
# 获取连接FTP配置
username = cf.get("ftp", "username")
password = cf.get("ftp", "password")
host = cf.get("ftp", "host")
port = cf.getint("ftp", "port")
# 获取路径
remotepath = cf.get("path", "remotepath")
localpath = cf.get("path", "localpath")
if not os.path.exists(localpath):
    os.makedirs(localpath)
# 获取时间参数
date = cf.get("date","date")

ftpPath = remotepath.split(";")
logpath = localpath+"/log/"
if not os.path.exists(logpath):
    os.makedirs(logpath)

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename=logpath+(datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')+'_ftp_download.log',
                filemode='w')

# 连接FTP服务器
def ftpconnect(host, username, password):
    ftp = FTP()
    ftp.connect(host, port)
    ftp.login(username, password)
    logging.info("Connection success!")
    return ftp
#从ftp下载文件
def downloadfile(ftp, filename):
    bufsize = 1024
    for p in ftpPath:
        try:
            ftp.cwd(p)
            list = ftp.nlst()
        except Exception :
            logging.error("Remote path does not exist!Please check whether the configuration file 'remotepath' is correct")
        else:
            for name in list:
                # 正则过滤掉其他日期
                L = filename in name
                if L:
                    path = localpath +p
                    if not os.path.exists(path):
                        os.makedirs(path)
                    file = p+name
                    f = open(path+name, 'wb')
                    logging.info("File download success! File:"+path+name)
                    ftp.retrbinary('RETR '+file, f.write, bufsize)
                    f.close()
# 删除特定日期的文件
def removefiles(day):
    for p in ftpPath:
        try:
            for eachFile in os.listdir(localpath+p):
                if os.path.isfile(localpath+p+eachFile):
                    ft = os.stat(localpath+p+eachFile)
                    ltime = int(ft.st_mtime) # 获取文件最后修改时间
                    ntime = time.mktime((datetime.datetime.now() - datetime.timedelta(day)).timetuple())
                    if ltime <= ntime:
                        os.remove(localpath+p+ eachFile)
                        logging.info("File has been deleted! File:"+localpath+p+ eachFile)
        except Exception :
            logging.error("FileNotFoundError!System path does not exist!")
    for eachFile in os.listdir(localpath + "/log/"):
        if os.path.isfile(localpath + "/log/" + eachFile):
            print(localpath + "/log/" + eachFile)
            ft = os.stat(localpath + "/log/" + eachFile)
            ltime = int(ft.st_mtime)  # 获取文件最后修改时间
            ntime = time.mktime((datetime.datetime.now() - datetime.timedelta(day)).timetuple())
            if ltime <= ntime:
                os.remove(localpath + "/log/" + eachFile)
                logging.info("File has been deleted! File:" + localpath + "/log/" + eachFile)
if __name__ == "__main__":	
    # delete files    
    removefiles(90)
    # 日期参数判断，为空，某天，某个时间段
    if date=='':
        try:
            # 格式化取到昨天的日期
            d = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')
            ftp = ftpconnect(host, username, password)
            downloadfile(ftp, d)
        except Exception:
            logging.error(
                "====>The connection failed: Please check whether the'ftp'configuration information is correct")
        else:
            ftp.quit()
            logging.info("Connection closed!")

    elif len(date.split("-"))==1:
        try:
            ftp = ftpconnect(host, username, password)
            downloadfile(ftp, date)
        except Exception:
            logging.error(
                "====>The connection failed: Please check whether the'ftp'configuration information is correct")
        else:
            ftp.quit()
            logging.info("Connection closed!")
    elif len(date.split("-"))==2:
        d = date.split("-")
        if d[0]<=d[1]:
            date_list = []
            begin_date = datetime.datetime.strptime(date.split("-")[0], "%Y%m%d")
            end_date = datetime.datetime.strptime(date.split("-")[1], "%Y%m%d")
            while begin_date <= end_date:
                date_str = begin_date.strftime("%Y%m%d")
                date_list.append(date_str)
                begin_date += datetime.timedelta(days=1)
            try:
                for time in date_list:
                    ftp = ftpconnect(host, username, password)
                    downloadfile(ftp, time)
                ftp.quit()
            except Exception:
                    logging.error(
                        "====>The connection failed: Please check whether the'ftp'configuration information is correct")
            else:
                logging.info("Connection closed!")
        else:

            logging.error('====>The date format of the configuration file is wrong and the date is small before.，example："20171201-20171202"')
    else:
        logging.error('====>The date format of the configuration file is wrong.Date format："date=","date=20171201","date=20171201-20171202"')
    
