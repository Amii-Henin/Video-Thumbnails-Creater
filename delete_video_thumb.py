# !/usr/bin/env python
# -*- coding:utf-8 -*-

# 作者：AMII
# 时间：20210310
# 更新内容：解决历史遗留问题

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
logfilename = 'delete_video_thumb_log.json'
logpath = 'log\\'
fontpath = 'fonts\\'
now = time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime(time.time()))
# fontType = os.path.join(fontpath, "杨任东竹石体-Heavy.ttf")
# fontTTF = TTFont(fontType)
# uniMap = fontTTF['cmap'].tables[0].ttFont.getBestCmap()


def main():
    alldirs.append(rootpath)
    get_dirs(rootpath)
    get_dirs_check(alldirs)
    # print (alldirs)
    save_log(logpath + logfilename,'a+',now + '  ' + rootpath + ':{\n')
    for path in alldirs:
        delete_thumb(path)
    save_log(logpath + logfilename,'a+','}\n')

# def main():     #删除繁体、日语缩略图（历史遗留问题）
#     alldirs.append(rootpath)
#     get_dirs(rootpath)
#     get_dirs_check(alldirs)
#     save_log(logpath + logfilename,'a+',now + '  ' + rootpath + ':{\n')
#     for path in alldirs:
#         delete_thumb(path)
#     save_log(logpath + logfilename,'a+','}\n')

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

def delete_thumb(path):        #删除缩略图
    files,nfiles,path_files = get_list(path)
    for x in range(len(files)):
        pic_name = path + '\\' + nfiles[x] + '_thumb.jpg'
        if os.path.exists(path + '\\' + nfiles[x] + '_thumb.jpg'):      #判断是否已有缩略图
            os.remove(pic_name)
            save_log(logpath + logfilename,'a+','    \"' + pic_name + '\",\n')
            print ('删除',pic_name)

# def delete_thumb(path):        #删除繁体、日语缩略图（历史遗留）
#     files,nfiles,path_files = get_list(path)
#     for x in range(len(files)):
#         pic_name = path + '\\' + nfiles[x] + '_thumb.jpg'
#         if os.path.exists(path + '\\' + nfiles[x] + '_thumb.jpg'):      #判断是否已有缩略图
#             if not check_font(files[x]):
#                 os.remove(pic_name)
#                 save_log(logpath + logfilename,'a+','    \"' + pic_name + '\",\n')
#                 print ('删除',pic_name)

# def delete_thumb(path):        #查找特定名称
#     files,nfiles,path_files = get_list(path)
#     for x in range(len(files)):
#         if not check_font(files[x]):
#             save_log(logpath + logfilename,'a+','    \"' + path + '\\' + files[x] + '\",\n')

def check_font(file):       #检查字体是否能显示文件名
    for x in file:
        if (ord(x) < 128):
            continue
        if not (ord(x) in uniMap.keys()):
            return False
    return True

def get_list(path):     #获取并返回目录下视频文件及目录等
    all_files = os.listdir(path)
    rule = r"\.(avi|wmv|wmp|wm|asf|mpg|mpeg|mpe|m1v|m2v|mpv2|mp2v|ts|tp|tpr|trp|vob|ifo|ogm|ogv|mp4|m4v|m4p|m4b|3gp|3gpp|3g2|3gp2|mkv|rm|ram|rmvb|rpm|flv|swf|mov|qt|nsv|dpg|m2ts|m2t|mts|dvr-ms|k3g|skm|evo|nsr|amv|divx|webm|wtv|f4v|mxf)$"
    path_file_list = []
    file_list = []
    nfile_list = []
    for files in all_files:
        if re.search(rule, files, re.IGNORECASE):
            file_list.append(files)
            nfile_list.append(os.path.splitext(files)[0])
            path_file_list.append(path + '\\' + files)
    return (file_list,nfile_list,path_file_list)

def save_log(logname,mode,mess):     #写入日志
    with open (logname,mode,encoding='utf-8') as f:
        f.write(mess)

if __name__ == '__main__':
    if not os.path.exists(logpath):
        os.makedirs(logpath)
    rootpath = input('请输入文件夹地址：')
    main()
