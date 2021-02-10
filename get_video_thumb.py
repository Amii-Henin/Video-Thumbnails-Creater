# !/usr/bin/env python
# -*- coding:utf-8 -*-
import subprocess
import fractions
import datetime
import ffmpeg
import ffmpy
import shlex
import time
import os
import re
from PIL import Image, ImageDraw, ImageFont
from io import StringIO,BytesIO


alldirs = []
now = time.strftime('%Y-%m-%d_%H%M%S',time.localtime(time.time()))

def main():
    rootpath = input('请输入文件夹地址：')
    alldirs.append(rootpath)
    get_dirs(rootpath)
    for path in alldirs:
        begin(path)

def get_dirs(root_path):
    dirs = os.listdir(root_path)
    for dir in dirs:
        dir = root_path + '\\' + dir
        if os.path.isdir(dir):
            alldirs.append(dir)
            get_dirs(dir)

def begin(path):
    files,nfiles,path_files = get_list(path)
    for x in range(len(files)):
        if os.path.exists(path + '\\' + nfiles[x] + '_thumb.jpg'):
            print ('已有缩略图____',nfiles[x],'\n')
            continue
##        try:
        if get_thumb(files[x],nfiles[x],path_files[x],path):
            print ('视频小于2分钟，跳过____',files[x])
            continue
##        except:
##            with open('get_thumb_log_' + str(now) + '.txt','a+',encoding='utf-8') as f:
##                f.write(path_files[x] + '\n')
##                print ('【【【Error File】】】',path_files[x],'\n\n')

def get_thumb(file,nfile,path_file,path):
    byte,size,bl,width,height,fps,sec,vtime = get_info(path_file)
    height_d = int(((height*960)/width)//1)
    if (sec < 120):
        return 1
    info = '文件名 :  ' + file + '\n' + '大  小   :  ' + size + ' (' + \
           str(byte) + ' Byte)\n' + '长宽比 :  ' + str(width) + 'x' + \
           str(height) + ' (' + bl + '), Fps: ' + fps + '\n时  长   :  ' + vtime
    tname = path + '\\' + nfile + '_thumb.jpg'
    num, row, jg = get_row(sec)
    t_width = 3840
    t_height = height_d * row + 300
    lw = 0
    lh = 300
    print ('图片数：',num,'  行数：',row)

    fullimg = Image.new('RGB',(t_width,t_height),(255,255,255))
    
    vinfo_img = Image.new('RGB',(3840,300),(255,255,255))
    font = ImageFont.truetype('STXINWEI.TTF',64)
    draw = ImageDraw.Draw(vinfo_img)
    draw.text((40,20),text=info,fill=(0,0,0),font=font)
    fullimg.paste(vinfo_img,(0,0))
    
    for i in range(num):
        time = jg * i + jg
        if (sec - time < 2):
            time -= 2
        tt = '0' + str(datetime.timedelta(seconds=time))        
        frame = get_frame(path_file, time)
        img = Image.open(BytesIO(frame)).resize((960,height_d),Image.ANTIALIAS)
        font = ImageFont.truetype('STXINWEI.TTF',36)
        draw = ImageDraw.Draw(img)
        draw.text((820,6),text=tt,fill=(255,255,255),font=font,stroke_width=3,stroke_fill='black')
        
        fullimg.paste(img,(lw,lh))
        lw += 960
        if ((i+1)%4==0):
            lh += height_d
            lw = 0
    fullimg.save(tname, quality = 80)
    print ('Well Done~~~~  ',tname,'\n')


def get_frame(path_file,time):
    out, err = (
        ffmpeg.input(path_file, ss = time)
              .output('pipe:', vframes=1, format='image2', vcodec='mjpeg')
              .run(capture_stdout=True,loglevel='quiet')
    )
    return out

def get_info(path_file):
    vv = 0
    probe = ffmpeg.probe(path_file)
    if (probe['streams'][0]['codec_type']=='audio'):
        vv = 1
    bytes = re.sub(r"(\d)(?=(\d\d\d)+(?!\d))", r"\1,", probe['format']['size'])
    size = hum_convert(int(probe['format']['size']))
    bl = str(fractions.Fraction(str(probe['streams'][vv]['width']) + '/' + str(probe['streams'][vv]['height'])))
    width = probe['streams'][vv]['width']
    height = probe['streams'][vv]['height']
    fpss = probe['streams'][vv]['r_frame_rate'].split('/')
    fps = str(round(int(fpss[vv])/int(fpss[1]),2))
    tim = int(float(probe['format']['duration'])//1)
    time = '0' + str(datetime.timedelta(seconds=(tim)))
    return (bytes,size,bl,width,height,fps,tim,time)

def get_list(path):
    all_files = os.listdir(path)
    rule = r"\.(mov|mp4|mpg|mov|mpeg|flv|wmv|avi|mkv|rmvb)$"
    path_file_list = []
    file_list = []
    nfile_list = []
    for files in all_files:
        if re.search(rule, files, re.IGNORECASE):
            file_list.append(files)
            nfile_list.append(os.path.splitext(files)[0])
            path_file_list.append(path + '\\' + files)
    return (file_list,nfile_list,path_file_list)

def hum_convert(value):
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024.0
    for i in range(len(units)):
        if (value / size) < 1:
            return "%.2f%s" % (value, units[i])
        value = value / size

def get_row(sec):
    jg = 0
    num = 0
    row = 0
    if (sec <= 601):
        jg = 5
    elif (sec <= 1800):
        jg = 15
    elif (sec <= 3600):
        jg = 30
    else :
        jg = 60
    num = sec//jg
    if (num%4==2 or num%4==3):
        row = num//4 + 1
    elif (num%4==0):
        row = num//4
    else:
        row = num//4
        num -= 1
    return (num, row, jg)






if __name__ == '__main__':
    main()
