# coding=gbk

'''
���ܣ����ر�����Ԫ�ص�λ�ü�����
'''


def  getText(filename):          #��ȡ�ı�����
    with open(filename, 'r',encoding='utf-8') as f:
        text = f.read()
    return text

def Numlen(list,str):                #�����ظ�Ԫ����ԭ�ı���λ�ü����ȣ����б���ʽ
    Info = []                        #����ֵ����¼λ�ü�����
    InfoPlace = []                   #�洢����Ԫ�ص���Ϣ
    T = str.find(list[0])
    infoplace = [T,T+len(list[0])-1]
    info = [T,len(list[0])]
    Info.append(info)
    InfoPlace.append(infoplace)
    for item in list[1:]:
        if item:
            length = len(item)                            #��¼Ԫ�س���
            placelist = findNum(item,str)                #Ԫ�ص�����λ������
            placelist1 = placelist[:]
            place = compare(placelist1,InfoPlace)        #����λ��
            info = [place,length]
            Info.append(info)                             #�洢��Ϣ
            info1 = [place,place+length-1]
            InfoPlace.append(info1)
    return Info

def  findNum(str1,str2):                        #�ҳ�Ԫ�ص���ʼλ��
    len1 = len(str1)                            #Ԫ�س���
    len2 = len(str2)                            #�ı�����
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








