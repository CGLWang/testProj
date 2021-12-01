#!/usr/bin/env python
#!-*- coding:utf-8 -*-
#!time      : 2019/4/19 15:26
#!@Author   : Tang
#!@File     :.py

import xlrd
import pymysql
import os
from guifan import Inspection
from django.http import HttpResponse
from configuration import get_config_values

PORT = int(get_config_values('mysql', 'port'))
HOST = get_config_values('mysql', 'host')
USER = get_config_values('mysql', 'user')
PASW = get_config_values('mysql', 'password')
DATB = get_config_values('mysql', 'database')

#TODO:填表函数



database = DATB
host=HOST
user=USER
port=PORT
passwd=PASW
charset='utf8'

#file_nme = r'C:\Users\太乙真人\Desktop\项目\国家电网\文件\2016年教育培训项目储备表.xls'
#file_name = r'C:\Users\keen\Desktop\项目\国家电网\文件\2016年信息化项目储备表.xls'
file_name = r'C:\Users\keen\Desktop\项目\国家电网\文件\2016年生产大修项目储备表.xls'

keywords = ['项目名称', '项目编码', '所属单位', '电压等级', '专业细分', '项目内容', '年度计划']
table_heads = ['项目名称', '省份', '项目类型', '集群类型', '专业细分', '所在地', '所属单位',
                '电压等级', '内容', '项目性质', '调度名称', '业务科目', '项目类别', '实施主体',
                '实施年份', '总投资','项目起始时间', '项目结束时间', '止', '年度计划',
                '项目编码', '词向量','哈希值']


table_heads_list = ['项目名称', '省份', '项目类型', '集群类型', '专业细分', '所在地', '所属单位',
                    '电压等级', '内容', '项目性质', '调度名称', '业务科目', '项目类别', '实施主体',
                    '实施年份','项目起始时间', '起', '项目结束时间', '止', '总投资', '年度计划',
                    '项目编码', '词向量','哈希值']


#project_type_names = ['非生产大修', '非生产技改', '管理咨询', '小型基建', '教育培训', '零星购置专业', '生产大修项目', '生产技改', '信息化', '研究开发', '电网基建']
project_type_names = ['非生产技改', '非生产大修', '管理咨询', '小型基建', '教育培训', '零星购置专业', '生产大修', '生产技改', '信息化', '研究开发', '电网基建']
folder_path = r'C:\Users\keen\Desktop\项目\国家电网\文件'




#获取项目类型名称
def get_porject_type():
    sql = """select * from pro_type"""
    pro_names = read_mysql_all(database,sql)
    return pro_names

#获取文件路径
def get_doc_path(folder_path):
    # 获取路径下所有文件名
    doc_path =[]
    doc_names = os.listdir(folder_path)
    for doc_name in doc_names:
        doc_path.append(folder_path + '\\' + doc_name)
    return doc_path

#查找文件(项目)类型所对应的的id
def find_doc_type_index(file_name):
    pro_names = get_porject_type()
    #print(pro_names)
    if '非' in file_name:
        for pro_name in pro_names:

            if '非' in pro_name[1]:
                if pro_name[1] in file_name:
                    return pro_name[0]
    else:
        for pro_name in pro_names:
            if pro_name[1] in file_name:
                return pro_name[0]




#读取excel文件
def open_excel(file):
    try:
        data = xlrd.open_workbook(file)
        return data
    except Exception as e:
        print(e)
        print('文件不存在')
        response = HttpResponse('''[{"STATE": 3}]''')
        response["Access-Control-Allow-Origin"] = "*"
        response["Content-Type"] = "application/json;charset=UTF-8"
        return response

def get_excel_keyword_data(file):
    # print('GETFILE',file)
    data = open_excel(file)
    # TODO：这个位置在linux要修正
    My_year = int(file.split('\\')[-1][:4])
    # print(My_year)
    table = data.sheets()[0]
    rows = table.nrows
    cols = table.ncols

    # 获取序号为1的行
    for i in range(rows):
#        if (type(table.cell_value(i, 0)) == float) and (table.cell_value(i, 0) == 1.0):
        if table.cell_value(i,0) == 1 or table.cell_value(i,0) == '1' or table.cell_value(i,0) == 1.0:
            first_row = i
            break
    table_head_index = []
    #找出表头所在列号
    table_head_row = first_row
    print(table_head_row)
    while table_head_row != 1 :
        table_head_row -= 1
        table_head_name = table.row_values(table_head_row)
        # print('table_head_name:',table_head_name)
        for table_head in table_heads:
            for i in range(len(table_head_name)):
                # print(table_head_name[i])
                if table_head in table_head_name[i] and '起止'not in table_head_name[i]:
                    if table_head_name[i]=='止':
                        table_head_index.append((i-1,'起'))
                    table_head_index.append((i, table_head))
                    break

#    print(table_head_index)
    # table_heads_to_colums(table_head_index)
    pro_type_id = find_doc_type_index(file)
    total_row_count = rows - first_row
    keywords_in_excel_data = {'proName':[None]*(total_row_count),'Province':[None]*(total_row_count),'proType':[pro_type_id]*(total_row_count),'cluType':[None]*(total_row_count),'proSeg':[None]*(total_row_count)
                              ,'proAddr':[None]*(total_row_count),'proUnit':[None]*(total_row_count),'volLevel':[None]*(total_row_count),'proDesc':[None]*(total_row_count),'proNature':[None]*(total_row_count)
                              ,'scheName':[None]*(total_row_count),'bussSub':[None]*(total_row_count),'proCate':[None]*(total_row_count),'proImpleBody':[None]*(total_row_count),'proImpleYear':[My_year]*(total_row_count)
                              ,'startTime':[None]*(total_row_count),'endStart':[None]*(total_row_count),'totalInvest':[None]*(total_row_count),'annPlan':[None]*(total_row_count),'proCode':[None]*(total_row_count)
                              ,'docVec':[None]*(total_row_count),'hashValue':[None]*(total_row_count),'repetRate':[None]*(total_row_count),'normValue':[None]*(total_row_count),'abnormRea':[None]*(total_row_count)}

    for child_value in table_head_index:
        if child_value[1] in table_heads_list:
            if (table_heads_list.index(child_value[1]) == 0):
                keywords_in_excel_data['proName'] = table.col_values(child_value[0],first_row)

            if (table_heads_list.index(child_value[1]) == 1):   #省份id预留（没有省份ID）
                # province_list = []
                keywords_in_excel_data['Province'] = table.col_values(child_value[0],first_row)
                # for item in keywords_in_excel_data['proName']:
                #     a_province = Inspection.findProvince(item)
                #     province_list.append(a_province)
                # keywords_in_excel_data['Province'] = province_list
                # print('province_list',province_list)
            # if (table_heads_list.index(child_value[1]) == 2):   #项目类型_id
            #     keywords_in_excel_data['proType'] = table.col_values(child_value[0],first_row)
            if (table_heads_list.index(child_value[1]) == 3):
                keywords_in_excel_data['cluType'] = table.col_values(child_value[0],first_row)
            if (table_heads_list.index(child_value[1]) == 4):
                keywords_in_excel_data['proSeg'] = table.col_values(child_value[0],first_row)
                #print('CHECKME',keywords_in_excel_data['proSeg'])

            if (table_heads_list.index(child_value[1]) == 5):
                keywords_in_excel_data['proAddr '] = table.col_values(child_value[0],first_row)
            # if (table_heads_list.index(child_value[1]) == 6): #项目所属单位_id保留
            #     keywords_in_excel_data['proUnit'] = table.col_values(child_value[0],first_row)
            if (table_heads_list.index(child_value[1]) == 7):   #电压等级
                #keywords_in_excel_data['volLevel'] = table.col_values(child_value[0],first_row)
                vol = table.col_values(child_value[0],first_row)
                for vol_level in range(len(vol)):
                    if vol[vol_level] == '48V':
                        vol[vol_level] = 1
                    elif vol[vol_level] == '220V':
                        vol[vol_level] = 2
                    elif vol[vol_level] == '380V':
                        vol[vol_level] = 3
                    elif vol[vol_level] == '10kV':
                        vol[vol_level] = 4
                    elif vol[vol_level] == '35kV':
                        vol[vol_level] = 5
                    elif vol[vol_level] == '220KV':#这里应该改成kV
                        vol[vol_level] = 6
                    elif vol[vol_level] == '500kV':
                        vol[vol_level] = 7
                    elif vol[vol_level] == '800kV':
                        vol[vol_level] = 8
                    else:
                        vol[vol_level] = 9
                keywords_in_excel_data['volLevel'] = vol
            if (table_heads_list.index(child_value[1]) == 8):
                keywords_in_excel_data['proDesc'] = table.col_values(child_value[0],first_row)
            if (table_heads_list.index(child_value[1]) == 9):
                keywords_in_excel_data['proNature'] = table.col_values(child_value[0],first_row)
            if (table_heads_list.index(child_value[1]) == 10):
                keywords_in_excel_data['scheName'] = table.col_values(child_value[0],first_row)
            if (table_heads_list.index(child_value[1]) == 11):
                keywords_in_excel_data['bussSub'] = table.col_values(child_value[0],first_row)
            if (table_heads_list.index(child_value[1]) == 12):
                keywords_in_excel_data['proCate'] = table.col_values(child_value[0],first_row)
            if (table_heads_list.index(child_value[1]) == 13):
                keywords_in_excel_data['proImpleBody'] = table.col_values(child_value[0],first_row)
            #TODO:年份待修正
            #if (table_heads_list.index(child_value[1]) == 14):
                #keywords_in_excel_data['proImpleYear'] = table.col_values(child_value[0],first_row)
            #keywords_in_excel_data['proImpleYear'] = [My_year]*(total_row_count)
            if (table_heads_list.index(child_value[1]) == 15 or table_heads_list.index(child_value[1]) == 16):
                # keywords_in_excel_data['startTime'] = table.col_values(child_value[0],first_row)
                #TODO:空白测试
                mylist =table.col_values(child_value[0],first_row)
                for i in range(len(mylist)):
                    if mylist[i]=='':
                        mylist[i]=str(My_year)+'-01-01'
                keywords_in_excel_data['startTime'] = mylist

            if (table_heads_list.index(child_value[1]) == 17 or table_heads_list.index(child_value[1]) == 18):
                # keywords_in_excel_data['endStart'] = table.col_values(child_value[0],first_row)
                # TODO:空白测试
                mylist2 = table.col_values(child_value[0],first_row)
                for i in range(len(mylist2)):
                    if mylist2[i] == '':
                        mylist2[i] = str(My_year) + '-12-31'
                keywords_in_excel_data['endStart'] = mylist2

            if (table_heads_list.index(child_value[1]) == 19):
                keywords_in_excel_data['totalInvest'] = table.col_values(child_value[0],first_row)
            if (table_heads_list.index(child_value[1]) == 20):
                keywords_in_excel_data['annPlan'] = table.col_values(child_value[0],first_row)
            if (table_heads_list.index(child_value[1]) == 21):
                keywords_in_excel_data['proCode'] = table.col_values(child_value[0],first_row)
            if (table_heads_list.index(child_value[1]) == 22):
                keywords_in_excel_data['docVec'] = table.col_values(child_value[0],first_row)
            if (table_heads_list.index(child_value[1]) == 23):
                keywords_in_excel_data['hashValue'] = table.col_values(child_value[0],first_row)

            # if (table_heads_list.index(child_value[1]) == 24):
            #     keywords_in_excel_data['repetRate'] = table.col_values(child_value[0],first_row)
            # if (table_heads_list.index(child_value[1]) == 25):
            #     keywords_in_excel_data['normValue'] = table.col_values(child_value[0],first_row)
            # if (table_heads_list.index(child_value[1]) == 26):
            #     keywords_in_excel_data['abnormRea'] = table.col_values(child_value[0],first_row)


    #按行存放数据
#    write_data = list(zip(*keywords_in_excel_data.values()))

    return keywords_in_excel_data



def read_mysql_all(database,cmd):
    """
    读数据库
    :param database: 读所有
    :param cmd:
    :return:
    """
    #con = pymysql.connect(host='127.0.0.1', user='gw', port=3310, passwd='292014', db=database, charset='utf8')
    con = pymysql.connect(host=host, user=user, port=port, passwd=passwd, db=database, charset=charset)
    cur = con.cursor()
    try:
        cur.execute(cmd)
        data = cur.fetchall()
        #col_name = cur.description
        return data     #,col_name
    except Exception as e:
        print(e)
    cur.close()
    con.close()

def write_mysql(database,cmd,data):
    """
    写数据库
    :param database: 写多条
    :param cmd:
    :param data:
    :return:
    """
    con = pymysql.connect(host=host, user=user, port=port, passwd=passwd, db=database, charset=charset)
    cur = con.cursor()
    try:
        cur.executemany(cmd, data)
        con.commit()
    except Exception as e:
        print(e)
    cur.close()
    con.close()

def delete_normcheck_cache():
    con = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASW,db=DATB, charset='utf8')
    cur = con.cursor()
    try:
        cur.execute("delete from normcheck_cache")
        cur.execute("alter table normcheck_cache auto_increment=1")
        con.commit()
    except Exception as e:
        print(e)
    cur.close()
    con.close()

#写入命名缓存表
def write_sql2normcheck_cache(file_name):

    excel_data = get_excel_keyword_data(file_name)
    #print('proImpleYear',excel_data['proImpleYear'])

    data = {}
    data['proName'] = excel_data['proName']
    data['province_nameid'] = excel_data['Province']
    data['proType_nameid'] = excel_data['proType']
    data['cluType_nameid'] = excel_data['cluType']
    data['proSeg'] = excel_data['proSeg']
    data['proAddr_nameid'] = excel_data['proAddr']
    data['proUnit_nameid'] = excel_data['proUnit']
    data['volLevel_nameid'] = excel_data['volLevel']
    data['proDesc'] = excel_data['proDesc']
    data['proNature'] = excel_data['proNature']
    data['scheName'] = excel_data['scheName']
    data['bussSub'] = excel_data['bussSub']
    data['proCate'] = excel_data['proCate']
    data['proImpleBody'] = excel_data['proImpleBody']
    data['proImpleYear'] = excel_data['proImpleYear']
    data['startTime'] = excel_data['startTime']
    data['endStart'] = excel_data['endStart']
    data['totalInvest'] = excel_data['totalInvest']
    data['annPlan'] = excel_data['annPlan']
    # print('ANN',data['annPlan'])
    # print(type(data['annPlan'][0]))
    data['proCode'] = excel_data['proCode']
    data = list(zip(*data.values()))
    for i in range(len(data)):
        data[i] =list(data[i])
        # print(i,data[i])
        if data[i][-2]=='' or data[i][-2]==None:
            data[i][-2]=0
        if data[i][-3]=='' or data[i][-3]==None:
            data[i][-3] = 0
        else:
            data[i][-2]=float(data[i][-2])
            data[i][-3]=float(data[i][-3])
        # print(float(data[i][-2]))
        # data[i][-2] =float(data[i][-2])
        # data[i][-3] =float(data[i][-3])

    # print(data)
    # print(type(data))
    #TODO:20190718分情况填表：
    #新语句： INSERT INTO 表(项1，项2) VALUES (值1，值2) ON DUPLICATE KEY UPDATE 待更新项=新值；
    # 项中要有唯一索引性质的项，判断它 ：不存在重复 填大部分内容（前面的值）；存在重复 更新部分内容（后面的值）
    # command = """INSERT INTO  normcheck_cache(proName,province_nameid,proType_nameid,cluType_nameid,proSeg,proAddr_nameid,proUnit_nameid,volLevel_nameid,proDesc,
    #                proNature,scheName,bussSub,proCate,proImpleBody,proImpleYear,startTime,endStart,totalInvest,annPlan,proCode)
    #               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE
    #               proName =VALUES(proName),proDesc=VALUES(proDesc);"""
    command = """
            insert into normcheck_cache(proName,province_nameid,proType_nameid,cluType_nameid,proSeg,proAddr_name,proUnit_nameid,volLevel_nameid,proDesc,
                   proNature,scheName,bussSub,proCate,proImpleBody,proImpleYear,startTime,endStart,totalInvest,annPlan,proCode)
                   values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

    #delete_normcheck_cache()

    write_mysql('gwpro',command,data)


def specifacation_check_get_data():
    """
    规范检查要读的数据
    :return: 返回id ,项目名称，项目类型 的元组
    """
    sql = """SELECT id,proName,pro_type.proType FROM normcheck_cache LEFT JOIN pro_type on normcheck_cache.proType_nameid=pro_type.proType_id"""
    data = read_mysql_all(database,sql)

    return data

def update_normcheck_cache(database,check_result):
    """
    更新缓存表的规范检查数据
    :param database: 数据库名称
    :param check_result: 以字典的形式传入规范检查后的结果，包括id, normValue, abnormRea数据
    :return:
    """
#    data_length = len(check_result) - 2
#    update_data = {}
#    update_data = {'normValue':[None]*data_length,'abnormRea':[None]*data_length,'id':[None]*data_length}

    # update_data['normValue'] = check_result['normValue']
    # update_data['abnormRea'] = check_result['abnormRea']
    # update_data['id'] = check_result['id']

    #data = list(zip(*update_data.values()))
    # update_data = []
    # update_data.append(check_result['normValue'])
    # update_data.append(check_result['abnormRea'])
    # update_data.append(check_result['id'])

    con = pymysql.connect(host=host, user=user, port=port, passwd=passwd, db=database, charset=charset)
    cur = con.cursor()
    try:
        # for row in data:
        #sql = """update normcheck_cache set normValue='%s',abnormRea='%s' where id='%s'""" % (row[0], row[1], row[2])
        sql = """update normcheck_cache set province_nameid='%s',normValue='%s',abnormRea='%s' where id='%s'""" % (check_result['province_nameid'],check_result['normValue'], check_result['abnormRea'], check_result['id'])

        cur.execute(sql)
        con.commit()
    except Exception as e:
        print(e)
    cur.close()
    con.close()

def inspection_check():
    data = specifacation_check_get_data()
    results = {}
    for row in data:
        print(row[1], row[2])
        check_result = Inspection.checkALL(row[1], row[2])

        results['normValue'] = check_result['normValue']
        results['abnormRea'] = check_result['abnormRea']
        results['id'] = row[0]
        results['province_nameid'] = Inspection.findProvince(row[1])
        #print('check results',results)
        update_normcheck_cache(database, results)



if __name__ == '__main__':

    # data = [['2017','A',1,1],['2018','B',2,2],['2019','C',2,3],['2020','NEW',1,1]]
    #
    # command = """INSERT INTO multisource_data(proCode,proDesc,proType_id,cluType_id) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE proDesc= VALUES(proDesc);"""
    # '''proName='测试',province_id=22,proType_id=22,'''
    # #sqlhelper.execute(command)
    #
    # write_mysql('gw1', command, data)
    file_path = r'C:\Users\ldz\Desktop\测试文件\2017年教育培训项目储备表.xls'
    pro_type_id = find_doc_type_index(file_path)
    pro_names = get_porject_type()
    for a, b in pro_names:
        if b in file_path:
            pro_type = b
            break

    print(pro_type)



