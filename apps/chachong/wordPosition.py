# coding=gbk

'''
功能：返回被查找元素的位置及长度
'''


def  getText(filename):          #获取文本内容
    with open(filename, 'r',encoding='utf-8') as f:
        text = f.read()
    return text

def Numlen(list,str):                #返回重复元素在原文本的位置及长度，以列表形式
    Info = []                        #返回值，记录位置及长度
    InfoPlace = []                   #存储各个元素的信息
    T = str.find(list[0])
    infoplace = [T,T+len(list[0])-1]
    info = [T,len(list[0])]
    Info.append(info)
    InfoPlace.append(infoplace)
    for item in list[1:]:
        if item:
            length = len(item)                            #记录元素长度
            placelist = findNum(item,str)                #元素的所有位置索引
            placelist1 = placelist[:]
            place = compare(placelist1,InfoPlace)        #返回位置
            info = [place,length]
            Info.append(info)                             #存储信息
            info1 = [place,place+length-1]
            InfoPlace.append(info1)
    return Info

def  findNum(str1,str2):                        #找出元素的起始位置
    len1 = len(str1)                            #元素长度
    len2 = len(str2)                            #文本长度
    list = []
    for i in range(len2):
        fal_needle = str2[i:i + len1]
        if fal_needle == str1:
            list.append(i)
    return list

def compare(list1,list2):
    list = list1[:]
    for item in list:
        for item1 in list2:
            if item >= item1[0] and item<= item1[1]:
                #list1.remove(item)
                dellist(item,list1)
    if len(list1) == 0:
        m = list[-1]
    else:
        m = list1[0]
    return m

def dellist(item,list):
    for i in list[:]:
        if item == i:
            list.remove(i)
    return list








