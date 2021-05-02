# !/usr/bin/env python
# -*- coding:utf-8 -*-

# 作者：AMII
# 时间：2021-05-02
# 更新内容：初版
# 脚本功能：为视频创建缩略图，默认间隔2分钟以下：2s，10分钟：5s，30分钟：15s，1小时：30s，其他：60s

import datetime
import fractions
import os
import re
import time
import ffmpeg
from io import BytesIO
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None

alldirs = []
logfilename = 'get_video_thumb_pic_log.json'
logpath = 'D:\Sources\PY\get_video_thumb\log\\'
fontpath = 'D:\Sources\PY\get_video_thumb\\fonts\\'
now = time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime(time.time()))
fontType = os.path.join(fontpath, "杨任东竹石体-Heavy.ttf")
fontTTF = TTFont(fontType)
uniMap = fontTTF['cmap'].tables[0].ttFont.getBestCmap()

def main():
    alldirs.append(rootpath)
    get_dirs(rootpath)
    get_dirs_check(alldirs)
    # print (alldirs)
    save_log(logpath + logfilename,'a+',now + '  ' + rootpath + ':{\n')
    for x in range(len(alldirs)):
        begin(alldirs[x])
    save_log(logpath + logfilename,'a+','}\n')

def get_dirs(root_path):    #遍历目录
    dirs = os.scandir(root_path)
    # print (root_path)
    for x in dirs:
        if x.is_dir():
            if x.name != '$RECYCLE.BIN' and x.name != 'System Volume Information':
                alldirs.append(root_path + '\\' + x.name)
                get_dirs(root_path + '\\' + x.name)

def get_dirs_check(alldirs):    #遍历目录检查机制
    if re.search('\\\\\\\\',alldirs[-1]):
        for x in range(len(alldirs)):
            temp = alldirs[x].replace('\\\\','\\')
            alldirs[x] = temp

def begin(path):        #开始程序
    files,nfiles,path_files = get_list(path)
    for x in range(len(files)):
        if not os.path.exists(path + '\\pic\\'):      #判断是否已有缩略图文件夹
            os.mkdir(path + '\\pic\\')
        try:
            if get_pic(files[x],nfiles[x],path_files[x],path):        #已有缩略图_0000则跳过
                save_log(logpath + logfilename,'a+','0,AlreadyExists],\n')
                print ('已存在缩略图，跳过____',files[x])
                continue
            save_log(logpath + logfilename,'a+','\"Done\"],\n')
        except:
            save_log(logpath + 'get_video_thumb_pic_errlog_' + str(now) + '.txt','a+',path_files[x] + '\n')
            save_log(logpath + logfilename,'a+','0,\"err\"],\n')
            print ('\n【【【Error File】】】',path_files[x],'\n')    #运行出错，保留日志

def get_pic(file,nfile,path_file,path):       #获取视频截图并保存
    save_log(logpath + logfilename,'a+','    [\"' + path_file + '\",')
    width, height, sec, vtime = get_info(path_file)
    num, jg = get_row(sec)
    tt = '0' + str(datetime.timedelta(seconds=jg)).replace(":","：")
    if os.path.exists(path + '\\pic\\' + nfile + '【0001】' + tt + '.jpg'):
        return 1
    save_log(logpath + logfilename,'a+',str(sec) + ',\"' + vtime + '\",' + str(num) + ',')
    for x in range(num):
        time = jg + x * jg
        if (sec - time) < 2:
            time -= 2
        tt = '0' + str(datetime.timedelta(seconds=time)).replace(":","-")
        pic_name = nfile + '【' + '{:0>4d}'.format(x + 1) + '】' + tt + '.jpg'
        path_pic = path + '\\pic\\' + pic_name
        frame = get_frame(path_file, time)
        img = Image.open(BytesIO(frame))
        img.save(path_pic, quality = 85)
        save_log(logpath + logfilename,'a+',str(x + 1) + ',')
    print ('Well Done~~~~  \n')                 #搞定~~

def get_frame(path_file,time):      #获并返回取帧
    out, err = (
        ffmpeg.input(path_file, ss = time)
              .output('pipe:', vframes=1, format='image2', vcodec='mjpeg')
              .run(capture_stdout=True)
    )
    return out

def get_info(path_file):        #获取并返回视频基本信息
    vv = 0
    probe = ffmpeg.probe(path_file)
    for x in range(6):
        if (probe['streams'][x]['codec_type']=='video'):
            vv = x
            break
    width = probe['streams'][vv]['width']
    height = probe['streams'][vv]['height']
    tim = int(float(probe['format']['duration'])//1)
    time = '0' + str(datetime.timedelta(seconds=tim))
    return (width,height,tim,time)

def get_list(path):     #获取并返回目录下视频文件及目录等
    all_files = os.listdir(path)
    rule = r"\.(avi|wmv|wmp|wm|asf|mpg|mpeg|mpe|m1v|m2v|mpv2|mp2v|ts|tp|tpr|trp|vob|ogm|ogv|mp4|m4v|m4p|m4b|3gp|3gpp|3g2|3gp2|mkv|rm|ram|rmvb|rpm|flv|swf|mov|qt|nsv|dpg|m2ts|m2t|mts|dvr-ms|k3g|skm|evo|nsr|amv|divx|webm|wtv|f4v|mxf)$"
    path_file_list = []
    file_list = []
    nfile_list = []
    for files in all_files:
        if re.search(rule, files, re.IGNORECASE):
            file_list.append(files)
            nfile_list.append(os.path.splitext(files)[0])
            path_file_list.append(path + '\\' + files)
    return (file_list,nfile_list,path_file_list)

def hum_convert(value):     #格式化并返回文件大小
    units = [" B", " KB", " MB", " GB", " TB", " PB"]
    size = 1024.0
    for i in range(len(units)):
        if (value / size) < 1:
            return "%.2f%s" % (value, units[i])
        value = value / size

def get_row(sec):       #设定并返回图片个数、行数、间隔
    jg = 0
    num = 0
    if (sec <= 120):
        jg = s2
    elif (sec <= 601):
        jg = s10
    elif (sec <= 1801):
        jg = s30
    elif (sec <= 3601):
        jg = s60
    else :
        jg = sot
    num = sec//jg
    return (num, jg)

def save_log(logname,mode,mess):     #写入日志
    with open (logname,mode,encoding='utf-8') as f:
        f.write(mess)

if __name__ == '__main__':
    if not os.path.exists(logpath):
        os.makedirs(logpath)
    rootpath = input('请输入文件夹地址：')
    print('默认间隔2分钟以下：2s，10分钟：5s，30分钟：15s，1小时：30s，其他：60s【输入数字修改，回车跳过】')
    s2 = int(input('2分钟内间隔：') or 2)
    s10 = int(input('10分钟内间隔：') or 5)
    s30 = int(input('30分钟内间隔：') or 15)
    s60 = int(input('60分钟内间隔：') or 30)
    sot = int(input('大于60分钟间隔：') or 60)
    main()
