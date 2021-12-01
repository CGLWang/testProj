#!/usr/bin/env python
#!-*- coding:utf-8 -*-
#!time      : 2019/4/19 14:50
#!@Author   : Tang
#!@File     :.py

import jieba
import re
import pymysql
import os
from configuration import get_config_values

PORT = int(get_config_values('mysql', 'port'))
HOST = get_config_values('mysql', 'host')
USER = get_config_values('mysql', 'user')
PASW = get_config_values('mysql', 'password')
DATB = get_config_values('mysql', 'database')

'''线路和变电站针对大修和技改项目'''
base_dir = os.path.split(os.path.realpath(__file__))[0]
PATH_STOP =base_dir+r'\停用词表.txt'
PATH_FUNC = base_dir+r'\功能.txt'
PATH_NEWD = base_dir+r'\newDict.txt'
PATH_NEWD2 = base_dir+r'\newDict2.txt'
 # 去停用词
def movestopwords(pre_string):
    with open(PATH_STOP, 'r') as f:
        words = f.read().strip().replace(' ', '')
        word_list = words.split("\n")  # 以换行符分隔
        for word in word_list:
            pre_string = pre_string.replace(word, '')
    return pre_string

# 找变电站
def findsubstation(P_content):
    jieba.load_userdict(PATH_NEWD)  # 加载自定义词库

    # 记录每一个内容中出现的变电站
    station_list = []

    delete_list = ['时发变', '要求变', '电厂变', '电网变', '高抗变', '主变', '低压变', '研究变', '超高压变', '交流变',
                    '综上变', '情况变', '频繁变', '区段变', '非停变', '给变', '特高压变', '交流变']
    # 顿号在后面要去除，但又作为一个关键查找的点
    if P_content!=None:
        string_pro = P_content.strip().replace('、', ',')
        pre_string = movestopwords(string_pro)  # 对字符串去掉停用词
        word_list = ' '.join(jieba.cut(pre_string)).split(' ')  # 将字符串变成数组
        # erro_list用于检查漏检
        pattern = re.compile('.{5}变')
        erro_list = pattern.findall(pre_string)  # 返回字符串数组
        for i in range(len(word_list)):
            if (word_list[i] in ['变', '变电站']) and (5 > len(word_list[i - 1]) > 1):
                A_station = word_list[i - 1] + '变'
                # 既不重复也不多余
                if A_station not in (station_list + delete_list):
                    station_list.append(A_station)
            # 形如xxx、xxx变电站这样的形式挑选出来
            if (word_list[i] in ['变', '变电站']) and (word_list[i - 2] == ',') and (5 > len(word_list[i - 3]) > 1):
                if '变' not in word_list[i - 3]:
                    key_word = word_list[i - 3] + '变'
                else:
                    key_word = word_list[i - 3]
                B_station = [key_word, word_list[i - 1] + '变']
                for item in B_station:
                    if item not in (station_list + delete_list):
                        station_list.append(item)
    return station_list


# 找线路
def findlines(P_content):
    jieba.load_userdict(PATH_NEWD2)
    # 记录每一个检查出来的线路
    lines_list= []
    delete_list = ['接地线', '电力线', '导地线', '钢绞线', '漆包线', '联络线', '铝绞线', '耐张线', '传输线', '双绞线',
                   '紫外线', '电源线', '信号线', '输电线', '高压线', '电缆线', '电磁线', '由本线', '生命线', '包络线','张恩线']
    string_pro = P_content.strip()
    pre_string = movestopwords(string_pro)
    word_list = ' '.join(jieba.cut(pre_string)).split(' ')
    # 漏检 检查
    pattern1 = re.compile('.{5}线')
    pattern2 = re.compile('.{5}回')
    erro_list = pattern1.findall(string_pro) + pattern2.findall(string_pro)
    # print(word_list)
    for i in range(len(word_list)):
        connet_word = '回'
        # 找汉字编号线
        for key_words in ['一回', '一线', '二回', '四回', '二线', '三回', '三线', '四线']:
            if key_words in word_list[i] and word_list[i - 1] != '':
                if word_list[i - 1][-1] in ['一', '二', '三', '四']:
                    A_line = word_list[i - 2] + word_list[i - 1] + word_list[i][-1], \
                             (word_list[i - 2] + word_list[i - 1])[:-1] + word_list[i]
                    for item in A_line:
                        # 数字编号统一用罗马
                        item = item.translate(str.maketrans('一二三四', 'ⅠⅡⅢⅣ'))
                        if item not in lines_list:
                            lines_list.append(item)
                #TODO：顿号bug
                if word_list[i - 1]=='、':
                    A_line = word_list[i-3]+word_list[i - 2]+word_list[i][-1],\
                             word_list[i-3]+word_list[i]
                    for item in A_line:
                        # 数字编号统一用罗马
                        item = item.translate(str.maketrans('一二三四', 'ⅠⅡⅢⅣ'))
                        if item not in lines_list:
                            lines_list.append(item)
                else:
                    A_line = word_list[i - 1] + word_list[i]
                    A_line = A_line.translate(str.maketrans('一二三四', 'ⅠⅡⅢⅣ'))
                    if A_line not in lines_list and len(A_line)==4:
                        lines_list.append(A_line)
        # 找罗马编号线
        for key_words in ['Ⅲ', 'Ⅰ', 'Ⅱ', 'Ⅳ']:
            if key_words in word_list[i]:
                if word_list[i + 1] in ['Ⅲ', 'Ⅰ', 'Ⅱ', 'Ⅳ']:
                    if word_list[i + 2] == '线':
                        connet_word = word_list[i + 2]
                    B_line = word_list[i - 1] + word_list[i] + connet_word, word_list[i - 1] + word_list[
                        i + 1] + connet_word
                    for item in B_line:
                        item = item.translate(str.maketrans('一二三四', 'ⅠⅡⅢⅣ'))
                        if item not in lines_list and (len(item)>3):
                            lines_list.append(item)
                elif word_list[i + 1] == '、' and word_list[i + 2] in ['Ⅲ', 'Ⅰ', 'Ⅱ', 'Ⅳ']:
                    if word_list[i + 3] == '线':
                        connet_word = word_list[i + 3]
                    B_line = word_list[i - 1] + word_list[i] + connet_word, word_list[i - 1] + word_list[
                        i + 2] + connet_word
                    for item in B_line:
                        item = item.translate(str.maketrans('一二三四', 'ⅠⅡⅢⅣ'))
                        if item not in lines_list:
                            lines_list.append(item)
                elif word_list[i + 1] in ['回', '回路', '回线', '线'] and word_list[i - 1] not in ['Ⅲ', 'Ⅰ', 'Ⅱ', '、', 'Ⅳ']:
                    if word_list[i + 1] == '线':
                        connet_word = word_list[i + 1]
                    B_line = word_list[i - 1] + word_list[i] + connet_word

                    # 将汉字统一用罗马表示
                    B_line = B_line.translate(str.maketrans('一二三四', 'ⅠⅡⅢⅣ'))
                    if B_line not in lines_list and len(B_line)==4:
                        lines_list.append(B_line)
        # 找无编号线
        if word_list[i] != '':
            if word_list[i]=='线' and (len(word_list[i-1])== 2) and '回' not in word_list[i-1] and '线' not in word_list[i-1]:
                words = word_list[i-1]+word_list[i]
                if words not in (lines_list + delete_list):
                    lines_list.append(words)
    # print(lines_list)
    return lines_list



'''功能针对非生产大修、技改,零购，生产大修、技改的设施关键字提取'''
#找园区
def findfunctions_bak(P_name,P_content):
    jieba.load_userdict(PATH_NEWD)
    function_txt = open(PATH_FUNC,'r').readlines()
    function_list = []
    mylist = []
    # 已经提取出的关键词列表
    for item in function_txt:
        mylist.append(item.strip('\n'))
    # print(mylist)
    # 先在内容里找关键字
    if P_content!=None:
        pro_content = P_content.strip()
        pre_content = movestopwords(pro_content)
        word_list = ' '.join(jieba.cut(pre_content)).split(' ')
        for word in word_list:
            if (word in mylist) and (word not in function_list):
                function_list.append(word)
    # 再从名字中获取关键词作为补充
    if P_name != None:
        pro_name = P_name.strip()
        pre_name = movestopwords(pro_name)
        name_list = ' '.join(jieba.cut(pre_name)).split(' ')
        for word in name_list:
            if (word in mylist) and (word not in function_list):
                function_list.append(word)

    return function_list


#找设施
def findfunctions(P_name,P_content):
    jieba.load_userdict(PATH_NEWD)
    function_txt = open(PATH_FUNC,'r').readlines()
    function_list = []
    mylist = []
    # 已经提取出的关键词列表
    for item in function_txt:
        mylist.append(item.strip('\n'))
    # print(mylist)
    # 先在内容里找关键字
    pro_content = P_content.strip()
    pre_content = movestopwords(pro_content)
    word_list = ' '.join(jieba.cut(pre_content)).split(' ')
    for word in word_list:
        if (word in mylist) and (word not in function_list):
            function_list.append(word)
        if word == "调度楼"  and (word not in function_list) and('电力调控分中心' not in function_list):
            function_list.append(word)
        if word == "调度大楼" and ("调度楼" not in function_list):
            function_list.append("调度楼")

    # 再从名字中获取关键词作为补充
    province_list = ['湖北','湖南','四川','重庆','河南','江西']
    pro_name = P_name.strip()
    pre_name = movestopwords(pro_name)
    name_list = ' '.join(jieba.cut(pre_name)).split(' ')
    for word in name_list:
        if (word in mylist) and (word not in function_list):
            function_list.append(word)
        if word == "调度楼" and (word not in function_list) and ('电力调控分中心' not in function_list):
            function_list.append(word)
        if word == "调度大楼" and ("调度楼" not in function_list):
            function_list.append("调度楼")
        if word in ["检修公司","检修分公司"]:
            for province in province_list:
                if province in pro_name and (province+"检修公司" not in function_list):
                    function_list.append(province+"检修公司")
    return function_list


'''
找道路
输入：
P_name：项目名
P_cont：项目内容
P_id:项目ID

返回：
其中 waylist: 道路 列表
'''
def findway(P_name,P_cont):
    flag = 0
    jieba.load_userdict(PATH_NEWD)
    wordlist = ['铁路','公路','高速','客专','高铁','城铁','城铁路','高速铁路']
    delelist = ['以上','主干','跨越','二回','线路','城际']
    waylist = []
    if P_name!= None:
        for word in wordlist:
            # 项目名称中有道路出现
            if word in P_name:
                flag = 1
                break
    if flag ==1:
        if P_cont!= None:
            print('P_cont:',P_cont)
            content_str = P_cont.replace(' ','')
            content_str = re.sub('[’‘“”()]', '', content_str)
            content_list = ' '.join(jieba.cut(content_str)).split(' ')
        else:
            content_list=[]
        name_str = re.sub('[’‘“”()]', '', P_name)
        name_list = ' '.join(jieba.cut(name_str)).split(' ')
        # 项目内容和名称一起找
        aim_list = content_list+name_list
        #print(content_list)
        for i in range(len(aim_list)):
            if aim_list[i] in wordlist and len(aim_list[i - 1]) != 1:
                if aim_list[i - 1][-2:] not in (delelist + waylist):

                    waylist.append(aim_list[i - 1][-2:])

        for i in range(len(waylist)):
            waylist[i] =waylist[i]+'路'
    #直接返回道路列表的话
    return waylist


'''
同塔双回
没有关联项目
返回列表：
[478, 533, 636, 846, 855, 876, 880]
# fill_list:所有的待填写入库 同杆项目名称 及 同杆电线名称的列表
# [{'P_Name':同杆项目名,'L_Name'：[同杆线路列表]}，{...},...]
'''


def SameTower():
    tower_list = []
    connect = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASW,db=DATB, charset='utf8')
    cursor = connect.cursor()
    try:
        sql_turncate = "TRUNCATE TABLE pro__tower;"
        cursor.execute(sql_turncate)
        sql_turncate = "alter table tower auto_increment=1;"
        cursor.execute(sql_turncate)
        print('pro__tower关联表初始化成功')
        sql0 = "SELECT proDesc,id FROM multisource_data ;"
        cursor.execute(sql0)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            if '同塔' in row[0]:
                tower_list.append(row[1])
        # cursor.close()
        # connect.close()
        # return tower_list
                # 填写Tower的中间表
                sql1 = "insert into pro__tower(pro_tower_id) values('%d');" % (row[1])
                cursor.execute(sql1)
    except Exception as e:
        connect.rollback()  # 事务回滚
        print('事务处理失败', e)
    else:
        connect.commit()  # 事务提交
        print('处理成功')
        # 关闭连接
        cursor.close()
        connect.close()
    # except:
    #     print("Error: unable to get tower_list")
    # cursor.close()
    # connect.close()

    # # 查找所有同杆项目要显示的信息
    # fill_dict={}
    # fill_list = []
    # for item in tower_list:
    #     line_list=[]
    #     pro_circuit_id = item
    #     sql1 = "SELECT proName,circuit FROM guowang.pro__circuit a left outer join guowang.circuit b on a.circuit_id = b .circuit_id " \
    #            "left outer join guowang.multisource_data c on a.pro_circuit_id = c.id where pro_circuit_id =%s;"
    #     try:
    #         cursor.execute(sql1,[pro_circuit_id])
    #         results = cursor.fetchall()
    #         P_name = results[0][0]
    #         for row in results:
    #             line_list.append(row[1])
    #         #print (line_list)
    #         fill_dict['P_Name'] = P_name
    #         fill_dict['L_Name'] = line_list
    #         #print ('N:',P_name,'L:',line_list)
    #         ans =fill_dict
    #         fill_list.append(fill_dict.copy())
    #     except:
    #         print ("Error: unable to get Line_dict")
    #
    # #TODO: 合并线路一致的项目
    #
    # return fill_list


'''主函数'''
# 找出关键字段

# 项目名称，项目内容，关联类别...
def getkeyword(P_name,P_content,C_type1,C_type2=None):
    if C_type1 == '电气关联':
        if C_type2 =='变电站':
            ans = findsubstation(P_content)
        elif C_type2=='线路':
            ans = findlines(P_content)

        else:
            print('ERROR!')

    if C_type1 == '设备关联':
        if C_type2 =='变电站':
            ans = findsubstation(P_content)
        elif C_type2 =='跨道路':
            ans = findway(P_name,P_content)
        elif C_type2 =='同塔':
            ans = SameTower()
        else:
            print('ERROR!!')

    if C_type1 == '功能关联':
        if C_type2 == '园区':
            ans = findfunctions(P_name, P_content)
        elif C_type2 == '设施':
            ans = findfunctions(P_name, P_content)
        else:
            print('ERROR!!')
    return ans


if __name__=='__main__':
    print(os.getcwd()+r'\newDict.txt')