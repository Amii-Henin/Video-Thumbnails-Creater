# !/usr/bin/env python
# -*- coding:utf-8 -*-

# 作者：AMII
# 时间：2022-01-14
# 更新内容：弃用ffmpeg，改用OpenCV截取帧以提高速度
# 脚本功能：为视频创建网格状缩略图，默认宽度3840，每行图片个数默认横版4张，竖版5张；默认间隔2分钟以下：2s，10分钟：5s，30分钟：15s，1小时：30s，其他：60s

import time
import os
import re
import cv2
import fractions
import datetime
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None

logname = 'get_video_thumb_log.json'                                    # 日志文件
logpath = 'D:\Sources\PY\get_video_thumb\log\\'                         # 日志位置
fontpath = 'D:\Sources\PY\get_video_thumb\\fonts\\TW_remix.ttf'         # 字体位置（建议用字体软件混合多种语言字体）
now = time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime(time.time()))    # 当前时间

# 主控制
def start(path):
    file_list,path_list = get_list(path)        # 获取文件、目录列表
    for f in file_list:                         # 循环文件列表
        try:
            if get_thumb(path,f):               # 截取缩略图，若返回True删除占位缩略图
                delete_thumb(path,f)
                save_log('"' + os.path.join(path,f) + '", "跳过"\n')
        except:
            save_log(',' + os.path.join(path,f) + ',"Error"\n')
            print ('【Error File】',os.path.join(path,f))
            delete_thumb(path,f)
    if len(path_list):                          # 如本级有目录则循环递归调用
        for p in path_list:
            start(p)

# 获取视频截图并保存
def get_thumb(path, file):
    # 视频基础数据获取
    nfile = os.path.splitext(file)[0]
    pfile = os.path.join(path,file)
    tname = os.path.join(path, nfile + '_thumb.jpg')
    if (os.path.exists(tname)): return False    # 已存在缩略图
    with open(tname, 'w') as f: pass            # 生成占位缩略图
    cap = cv2.VideoCapture(pfile)               # 读取视频文件
    frames, fps, durations, tim, width, height = get_info(cap)  # 获取视频信息
    if (rotate % 2):                            # 长宽互换检测
        temp = width
        width = height
        height = temp
    bl = str(fractions.Fraction(width, height)) # 比例设置
    if frames == 0: return True                 # 帧数为零，返回True，删除生成的占位缩略图
    if (durations < 5): return True             # 时间过短，返回True，删除生成的占位缩略图
    byte = os.path.getsize(pfile)               # 获取文件字节大小
    bytes = format(byte, ",")                   # 格式化字节大小
    size = hum_convert(byte)                    # 字节转MB、GB
    save_log('"' + os.path.join(path,file) + '",')

    # 缩略图数据设置
    col_default = col_def
    xs = width_default/3840                 # 比例系数
    tsize_info = int((64 * xs)//1)          # 视频信息文字大小
    tsize_filename = int((64 * xs)//1)      # 文件名文字大小
    tsize_time = int((36 * xs)//1)          # 时间信息文字大小
    logo = "-- by AMII"
    if rotate == 0 and (height/width) > 1.2 and col_default == 4:
        col_default = 5                                                 # 竖版视频一行5张图
    width_each_pic = int((width_default/col_default)//1)                # 定义每张缩略图宽度
    height_each_pic = int(((height*width_each_pic)/width)//1)           # 定义每张缩略图高度
    info = '文件名 :\n' + '大    小 :  ' + size + ' (' + \
           str(bytes) + ' Byte)\n' + '长宽比 :  ' + str(width) + 'x' + \
           str(height) + ' (' + bl + '),  FPS: ' + str(fps) + '\n时    长 :  ' + tim
    info_name = '文件名 :  '
    num, row, jg = get_row(durations,col_default)
    lw = 0                                      # 左上角坐标宽度
    lh = int((330 * xs)//1)                     # 左上角坐标高度
    height_full = height_each_pic * row + lh    # 总图高度
    while (height_full > 65530):                # 图片高度大于65530则增加每行图片数量
        col_default += 1
        width_each_pic = int((width_default/col_default)//1)
        height_each_pic = int(((height*width_each_pic)/width)//1)
        row = int((num + col_default -1) // col_default)
        height_full = height_each_pic * row + lh
    save_log(str(durations) + ',"' + tim + '",' + str(num))

    # 循环获取截图并保存
    fullimg = Image.new('RGB',(width_default,height_full),"white")      # 新建总图底图
    vinfo_img = Image.new('RGB',(width_default,lh),"white")             # 新建信息条底图
    font = ImageFont.truetype(fontpath,tsize_info)                      # 设置视频信息字体
    font_time = ImageFont.truetype(fontpath,tsize_time)                 # 设置截图时间字体
    font_filename = ImageFont.truetype(fontpath,tsize_filename)         # 设置文件名字体
    name_size = font.getsize(info_name)                                 # 获取文件名左侧长度
    filename_size = font_filename.getsize(file)                         # 获取文件名长度
        # 文件名过长缩小字体
    while (filename_size[0] > (width_default - name_size[0] - int((40*xs)//1))):
        tsize_filename -= 2
        font_filename = ImageFont.truetype(fontpath, tsize_filename)
        filename_size = font_filename.getsize(file)
        # 绘制信息条内容
    draw = ImageDraw.Draw(vinfo_img)
    logo_size = font.getsize(logo)
    draw.text((int((40*xs)//1) + name_size[0],int((24*xs)//1)),text=file,fill=(0,0,0),font=font_filename)
    draw.text((int((40*xs)//1),int((24*xs)//1)),text=info,fill=(0,0,0),font=font)
    draw.text((width_default - logo_size[0] - 10, lh - logo_size[1] - 11), text=logo, fill=(0, 0, 0), font=font)
    fullimg.paste(vinfo_img,(0,0)) 
    chk = 2
    print(nfile + '\n[',end="")
        # 循环截取视频截图并粘贴至总图
    for i in range(num):
        save_log(',' + str(i+1))
        rotate_deg = [Image.ROTATE_90,Image.ROTATE_180,Image.ROTATE_270]
        time = jg * i + jg
        # if ((i + 1) == num):                                  ####【调试】####
        #     # continue
        #     time -= 1
        ttt = str(datetime.timedelta(seconds=time))
        tt = '0' + ttt if len(ttt) == 7 else ttt
        time_size = font_time.getsize(tt)
        cap.set(cv2.CAP_PROP_POS_FRAMES, (time * fps) // 1)     # 设置截取帧数
        ret, frame = cap.read()
        frame = Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
        if (rotate == 0):               # 截图旋转检测
            img = frame.resize((width_each_pic,height_each_pic),Image.ANTIALIAS)
        else:
            img = frame.transpose(rotate_deg[rotate - 1]).resize((width_each_pic,height_each_pic),Image.ANTIALIAS)
        draw = ImageDraw.Draw(img)      # 绘制截图时间
        draw.text((width_each_pic - time_size[0] - 10, -2),text=tt,fill="white",font=font_time,stroke_width=3,stroke_fill="black")
        fullimg.paste(img,(lw,lh))      # 粘贴截图至总图
        lw += width_each_pic            # 向右平移坐标
        if ((i+1)%col_default==0):      # 换行检测
            lh += height_each_pic
            lw = 0
        if (((i + 1)/num)*100 > chk):
            sn = int((((i + 1)/num)*100 - chk) / 2)
            for x in range(sn):
                print('■',end="")
            chk += 2 * sn
    fullimg.save(tname, quality = 80)   # 保存总图
    save_log(',Done\n')
    print ('] Done~')

# 获取视频文件和文件夹列表
def get_list(path):
    file_list = []
    path_list = []
    rule = r"\.(avi|wmv|wmp|wm|asf|mpg|mpeg|mpe|m1v|m2v|mpv2|mp2v|ts|tp|tpr|trp|vob|ogm|ogv|mp4|m4v|m4p|m4b|3gp|3gpp|3g2|3gp2|mkv|rm|ram|rmvb|rpm|flv|swf|mov|qt|nsv|dpg|m2ts|m2t|mts|dvr-ms|k3g|skm|evo|nsr|amv|divx|webm|wtv|f4v|mxf)$"
    lists = os.listdir(path)
    for p in lists:
        if re.search("\$RECYCLE\.BIN|System Volume Information|Recovery",p): continue   # 排除windows系统文件夹
        if os.path.isdir(os.path.join(path,p)):
            path_list.append(os.path.join(path,p))      # 追加文件夹
            continue
        if re.search(rule, p, re.IGNORECASE):
            file_list.append(p)                         # 追加文件
    return (file_list, path_list)

# 获取视频基本信息
def get_info(cap):
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))     # 总帧数
    fps = round(cap.get(cv2.CAP_PROP_FPS))              # 帧率
    durations = int(frames / fps)                       # 时间
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))      # 宽度
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))    # 高度
    tim = str(datetime.timedelta(seconds=durations))    # 格式化时间
    tim = '0' + tim if len(tim) == 7  else tim          # 格式化时间前补零
    return (frames, fps, durations, tim, width, height)

# 设定并返回图片个数、行数、间隔
def get_row(sec,col):
    jg, num = (0,0)
    if (sec <= 120): jg = s2            # 2分钟内间隔
    elif (sec <= 601): jg = s10         # 10分钟内间隔
    elif (sec <= 1801): jg = s30        # 30分钟内间隔
    elif (sec <= 3601): jg = s60        # 60分钟内间隔
    else : jg = sot                     # 大于60分钟间隔
    num = sec//jg
    row = int((num + col -1) // col)
    return (num, row, jg)

# 删除缩略图
def delete_thumb(path,file):
    nfile = os.path.splitext(file)[0] + '_thumb.jpg'
    path_nfile = os.path.join(path,nfile)
    if(os.path.exists(path_nfile)):
        os.remove(path_nfile)

# 保存日志
def save_log(mess):
    with open (os.path.join(logpath,logname),'a+',encoding='utf-8') as f:
        f.write(mess)

# 格式化并返回文件大小
def hum_convert(value):
    units = [" B", " KB", " MB", " GB", " TB", " PB"]
    size = 1024.0
    for i in range(len(units)):
        if (value / size) < 1:
            return "%.2f%s" % (value, units[i])
        value = value / size

if __name__ == '__main__':
    if not os.path.exists(logpath):
        os.makedirs(logpath)
    rootpath = input('请输入文件夹地址：') or 'D:\downloads'
    col_def = int(input('你想一行几张图片（默认横版4,竖版5）：') or 4)
    width_default = int(input('缩略图宽度（默认3840）：') or 3840)
    rotate = int(input('是否逆时针旋转截图（1:90 2:180 3:270）：') or 0)
    print('默认间隔2分钟以下：2s，10分钟：5s，30分钟：15s，1小时：30s，其他：60s【输入数字修改，回车跳过】')
    s2 = int(input('2分钟内间隔：') or 2)
    s10 = int(input('10分钟内间隔：') or 5)
    s30 = int(input('30分钟内间隔：') or 15)
    s60 = int(input('60分钟内间隔：') or 30)
    sot = int(input('大于60分钟间隔：') or 60)
    # stime = time.time()
    save_log('\t' + now + ' ' + rootpath + '\n')
    start(rootpath)
