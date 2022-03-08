# !/usr/bin/env python
# -*- coding:utf-8 -*-

# 作者：AMII
# 时间：2022-03-08
# 更新内容：改用OpenCV提高速度，优化遍历方式减轻硬盘压力
# 脚本功能：为视频创建截图，默认间隔2分钟以下：2s，10分钟：5s，30分钟：15s，1小时：30s，其他：60s

import time
import os
import re
import cv2
import datetime
import numpy as np
# from PIL import Image, ImageDraw, ImageFont

logname = 'get_video_pic_log.json'                                          # 日志文件
logpath = os.path.join(os.path.split(os.path.abspath(__file__))[0],'log')   # 日志位置
now = time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime(time.time()))        # 当前时间

# 主控制
def start(path):
    file_list,path_list = get_list(path)        # 获取文件、目录列表
    for f in file_list:                         # 循环文件列表
        try:
            if get_pic(path,f):               # 截取截图，如已存在截图则跳过
                save_log('"' + os.path.join(path,f) + '", "跳过"\n')
        except:
            save_log('\n【----Error----】,' + os.path.join(path,f) + '\n')
            print ('\n【Error File】',os.path.join(path,f))
    if len(path_list):                          # 如本级有目录则循环递归调用
        for p in path_list:
            start(p)

# 获取视频截图并保存
def get_pic(path, file):
    # 视频基础数据获取
    nfile = os.path.splitext(file)[0]           # 视频文件名
    pfile = os.path.join(path,file)             # 视频路径+文件名
    path_pic = os.path.join(path,'pics_' + nfile)   # 截图存放路径
    temp_pic = os.path.join(path_pic,'0000.jpg')    # 临时文件
    if not os.path.exists(path_pic):            # pics文件夹检测
        os.makedirs(path_pic)
    if (os.path.exists(temp_pic)): return True  # 已存在临时文件
    with open (temp_pic,'w') as f: pass         # 创建临时文件
    cap = cv2.VideoCapture(pfile)               # 读取视频文件
    frames, fps, durations, tim, width, height = get_info(cap)  # 获取视频信息
    num, jg = get_row(durations)                # 获取截图数量、时间间隔
    if frames == 0: return False                # 帧数为零，返回True
    if (durations < 5): return False            # 时间过短，返回True
    save_log('"' + os.path.join(path,file) + '",' + str(frames) + ',' + str(fps) + ',' + str(durations) + ',"' + tim + '",' + str(num))

    chk = 2
    print(nfile + '\n[',end="")
    for i in range(num):
        loop_num = 0
        if i and i % 500 == 0:
            save_log('\n')
        name_t = str(datetime.timedelta(seconds=((i + 1) * jg))).replace(":","：")
        name_t = '0' + name_t if len(name_t) == 7 else name_t           # 文件名时间
        tmp_name = 'temp__' + str(i) + '.jpg'           # 临时文件名
        file_name = nfile + '__' + name_t + '.jpg'      # 截图文件名
        path_file = os.path.join(path_pic,file_name)    # 截图路径加文件名
        path_tmp = os.path.join(path_pic,tmp_name)      # 截图路径加临时文件名
        time_fps = int(((i + 1)* jg * fps) // 1)        # 时间帧数
        if os.path.exists(path_file):                   # 截图存在跳过
            save_log(',跳' + str(i+1))
            continue
        cap.set(cv2.CAP_PROP_POS_FRAMES, time_fps)      # 设置截取帧数
        ret, frame = cap.read()                         # 读取帧
        if (time_fps / frames) > 0.5:   # 设定回退or前进固定帧
            up_or_down = -round(fps)    # 回退
        else:
            up_or_down = round(fps)     # 前进
        while not ret:                  # 截图出错回退or前进指定帧
            if loop_num > (jg * 2):     # 回退or前进超过2个间隔退出
                save_log('\n【----Error----】,' + os.path.join(path,file) + '\n')
                print ('\n【Error File】',os.path.join(path,file))
                return True
            time_fps += up_or_down
            save_log('[' + str(int(time_fps)) + ']')
            print('.',end="")
            cap.set(cv2.CAP_PROP_POS_FRAMES, time_fps)
            ret, frame = cap.read()
            loop_num += 1
        if dwidth: 
            dheight = int(((dwidth/width)*height)//1)
            frame = cv2.resize(frame,(dwidth,dheight))   # 调整长宽
        if rotate: 
            frame = rotate_bound(frame, rotate)         # 旋转检测
        cv2.imwrite(path_tmp,frame)                     # 保存截图
        if os.path.exists(path_tmp): os.renames(path_tmp,path_file)     # 替换文件名
        save_log(',' + str(i+1))
        if (((i + 1)/num)*100 > chk):                   # 进度条模块
            sn = int((((i + 1)/num)*100 - chk) / 2)
            for x in range(sn):
                print('■',end="")
            chk += 2 * sn
    save_log(',Done\n')
    print ('] Done~')

# 获取指定类型文件和文件夹列表
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
    fps = round(cap.get(cv2.CAP_PROP_FPS), 4)           # 帧率
    durations = int(frames / fps)                       # 时间
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))      # 宽度
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))    # 高度
    tim = str(datetime.timedelta(seconds=durations))    # 格式化时间
    tim = '0' + tim if len(tim) == 7  else tim          # 格式化时间前补零
    return (frames, fps, durations, tim, width, height)

# OpenCV旋转图片
def rotate_bound(image, angle):
    (h, w) = image.shape[:2]        # 获取图片长宽
    (cX, cY) = (w // 2, h // 2)     # 设置旋转中心坐标
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)  # 设置M矩阵
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY
    return cv2.warpAffine(image, M, (nW, nH))

# 设定并返回图片个数、间隔
def get_row(sec):
    jg, num = (0,0)
    if (sec <= 120): jg = s2            # 2分钟内间隔
    elif (sec <= 601): jg = s10         # 10分钟内间隔
    elif (sec <= 1801): jg = s30        # 30分钟内间隔
    elif (sec <= 3601): jg = s60        # 60分钟内间隔
    else : jg = sot                     # 大于60分钟间隔
    num = sec//jg
    return (num, jg)

# 保存日志
def save_log(mess):
    with open (os.path.join(logpath,logname),'a+',encoding='utf-8') as f:
        f.write(mess)

if __name__ == '__main__':
    if not os.path.exists(logpath):
        os.makedirs(logpath)
    rootpath = input('请输入文件夹地址：') or 'D:\downloads'
    if input("是否改变默认参数："):
        dwidth = int(input('截图宽度：') or 0)
        rotate = int(input('是否逆时针旋转截图（输入度数）：') or 0)
        print('默认间隔2分钟以下：2s，10分钟：5s，30分钟：15s，1小时：30s，其他：60s【输入数字修改，回车跳过】')
        s2 = int(input('2分钟内间隔：') or 2)
        s10 = int(input('10分钟内间隔：') or 5)
        s30 = int(input('30分钟内间隔：') or 15)
        s60 = int(input('60分钟内间隔：') or 30)
        sot = int(input('大于60分钟间隔：') or 60)
    else:
        dwidth, rotate, s2, s10, s30, s60, sot = (0, 0, 2, 5, 15, 30, 60)
    print('[■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■] 进度条')
    # stime = time.time()
    save_log('\t' + now + ' ' + rootpath + '\n')
    start(rootpath)
