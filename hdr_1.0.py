import cv2 as cv
import numpy as np
import os
import shutil
import exifread
import datetime
import glob

def exif_info(path):
    '''返回图片时间与ev值'''
    f = open(path, 'rb')
    tags = exifread.process_file(f)
    re = []
    re.append(datetime.datetime.strptime(str(tags['Image DateTime']), '%Y:%m:%d %H:%M:%S'))
    re.append(str(tags['EXIF ExposureBiasValue']))
    return re

def time_dif(path1, path2):
    '''判断图片是否同时拍摄'''
    return (exif_info(path2)[0]-exif_info(path1)[0]).seconds <= 1

def EV_det(path):
    '''判断图片ev值是否是特定值'''
    return str(exif_info(path)[1]) == '-2/3' or str(exif_info(path)[1]) == '0' or str(exif_info(path)[1]) == '2/3'

def is_hdr(path1, path2, path3):
    '''判断三张图是否是aeb连拍'''
    return time_dif(path1, path2) and time_dif(path2, path3) and EV_det(path1) and EV_det(path2) and EV_det(path3)

def path_folder_isexist(uDir):
    '''如果存在文件夹,则返回原路径,如果不存在文件夹,则创建该目录并返回'''
    if os.path.exists(uDir):
        return uDir
    else:
        os.mkdir(uDir)
        return uDir

def hdr(path1, path2, path3):
    """给出路径，同级输出hdr照片,并移除原图"""
    img_fn = [path1, path2, path3]
    img_list = [cv.imread(fn) for fn in img_fn]
    merge_mertens = cv.createMergeMertens()
    res_mertens = merge_mertens.process(img_list)
    res_mertens_8bit = np.clip(res_mertens*255, 0, 255).astype('uint8')
    cv.imwrite(os.path.dirname(path1)+"/"+str(n)+".jpg", res_mertens_8bit)
    tar_f= os.path.dirname(path1)+'/jpg_origenal'
    path_folder_isexist(tar_f)
    shutil.move(path1,tar_f)
    shutil.move(path2,tar_f)
    shutil.move(path3,tar_f)

#path = '/Users/fkj/Desktop/dji/22.9.3/100MEDIA'
path = input("输入目标路径，比如100MEDIA文件夹的路径： ")
jpg_list_items = glob.iglob(path+'/*.JPG')
jpg_list = []
for jpg in jpg_list_items:
    jpg_list.append(jpg)
jpg_list.sort()
n = 0 
p = 0
for i in range(len(jpg_list)):
    i += p
    if i+2 > len(jpg_list):
        break
    path1 = jpg_list[i]
    path2 = jpg_list[i+1]
    path3 = jpg_list[i+2]
    print('\n')
    if is_hdr(path1, path2, path3):
        hdr(path1, path2, path3)
        n += 1
        p += 2
