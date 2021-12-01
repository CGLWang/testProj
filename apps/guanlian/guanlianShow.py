#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : guanlianShow.py
@Author: CQ
@Date  : 2019/5/25 15:14
@Desc  : 
"""
import pymysql
import numpy as np
from configuration import get_config_values

PORT = int(get_config_values('mysql', 'port'))
HOST = get_config_values('mysql', 'host')
USER = get_config_values('mysql', 'user')
PASW = get_config_values('mysql', 'password')
DATB = get_config_values('mysql', 'database')

def connectSql():
    connect = pymysql.Connect(
        host=HOST,
        port=PORT,
        user=USER,
        passwd=PASW,
        db=DATB,
        charset='utf8'
    )
    # 获取游标
    cursor = connect.cursor()
    return connect,cursor

"""
parameter:
releType1:
    releType1_dict = {
        '1': 'elec_rele',
        '2': 'dev_rele',
        '3': 'fun_rele'
    }用来选择更新的关联表
releType2:
    releType2_dict = {
        '1': 'substation',
        '2': 'circuit',
        '3': 'road',
        '4': 'facility'
    }用来选择二级关联
proAddr:{1:湖北,2:湖南,3:河北,4:江西,5:其他}
relaObject：指具体的什么变电站、线路、道路、园区
startYear:选择的起始年份
endYear:选择的结束年份，在这个范围内把项目挑选出来
"""

def writeReleTable(releType1,releType2,proType,proAddr,releObject,startYear,endYear):
    print(releType1,releType2,proType,proAddr,releObject,startYear,endYear)

    connect, cursor = connectSql()
    releType1_dict = {
        '1': 'elec_rele',
        '2': 'dev_rele',
        '3': 'fun_rele'
    }
    releType2_dict = {
        '1': 'substation',
        '2': 'circuit',
        '3': 'road',
        '4': 'facility'
    }
    proAddr_str = '' if proAddr == '0' else " and (multisource_data.province_id='%d')" % (int(proAddr))
    proType_str = '' if proType == '0' else " and (multisource_data.proType_id='%d')" % (int(proType))
    if startYear == '0' or endYear == '0':
        year_str = ''
    else:
        year_list = list(range(int(startYear), int(endYear) + 1))
        year_str = ','.join('%s' % i for i in year_list)
        year_str = " and (multisource_data.proImpleYear in (%s))" % year_str
    print(year_str)
    try:
        sql_turncate = "TRUNCATE TABLE elec_rele;".replace('elec_rele',releType1_dict[releType1])
        cursor.execute(sql_turncate)
        print('elec_rele关联表初始化成功'.replace('elec_rele',releType1_dict[releType1]))
        # for i in range(len(substation)):
        if releType2 == '1':  # 变电站
            sql_1 = "SELECT multisource_data.id,substation.substation,multisource_data.proName,multisource_data.proType_id,multisource_data.proCode,multisource_data.province_id,multisource_data.proImpleYear,multisource_data.proDesc " \
                "FROM pro__substation " \
                "JOIN  multisource_data  ON  (pro__substation.pro_substation_id = multisource_data.id ) " \
                "JOIN  substation   ON  (pro__substation.substation_id = substation.substation_id ) " \
                "WHERE (pro__substation.substation_id='%d'){stence1}{stence2}{stence3};".format(stence1=proAddr_str,stence2=proType_str,stence3=year_str) % (int(releObject))
            print('关联明细语句:',sql_1)
        if releType2 == '2':  # 线路
            sql_1 = "SELECT multisource_data.id,substation.substation,multisource_data.proName,multisource_data.proType_id,multisource_data.proCode,multisource_data.province_id,multisource_data.proImpleYear,multisource_data.proDesc " \
                    "FROM pro__substation " \
                    "JOIN  multisource_data  ON  (pro__substation.pro_substation_id = multisource_data.id ) " \
                    "JOIN  substation   ON  (pro__substation.substation_id = substation.substation_id ) " \
                    "WHERE (pro__substation.substation_id='%d') {stence1} {stence2} {stence3};".format(stence1=proAddr_str,stence2=proType_str,stence3=year_str).replace('substation', releType2_dict[releType2]) % (int(releObject))
        if releType2 == '3':  # 道路
            sql_1 = "SELECT multisource_data.id,substation.substation,multisource_data.proName,multisource_data.proType_id,multisource_data.proCode,multisource_data.province_id,multisource_data.proImpleYear,multisource_data.proDesc " \
                    "FROM pro__substation " \
                    "JOIN  multisource_data  ON  (pro__substation.pro_substation_id = multisource_data.id ) " \
                    "JOIN  substation   ON  (pro__substation.substation_id = substation.substation_id ) " \
                    "WHERE (pro__substation.substation_id='%d') {stence1} {stence2} {stence3};".format(stence1=proAddr_str,stence2=proType_str,stence3=year_str).replace('substation', releType2_dict[releType2]) % (int(releObject))
        if releType2 == '4':  # 园区
            sql_1 = "SELECT multisource_data.id,substation.substation,multisource_data.proName,multisource_data.proType_id,multisource_data.proCode,multisource_data.province_id,multisource_data.proImpleYear,multisource_data.proDesc " \
                    "FROM pro__substation " \
                    "JOIN  multisource_data  ON  (pro__substation.pro_substation_id = multisource_data.id ) " \
                    "JOIN  substation   ON  (pro__substation.substation_id = substation.substation_id ) " \
                    "WHERE (pro__substation.substation_id='%d') {stence1} {stence2} {stence3};".format(stence1=proAddr_str,stence2=proType_str,stence3=year_str).replace('substation', releType2_dict[releType2]) % (int(releObject))
        # print(sql_1)
        cursor.execute(sql_1)  # 查找关联项目
        result = cursor.fetchall()
        # print(result)
        for row in result:
            # print(row)
            if releType1=='1':
                sql_2 = "insert into elec_rele(eleInfo,proName,proType,proCode,proProvince,proImpleYear,proDesc) " \
                        "values " \
                        "(%s,%s,%s,%s,%s,%s,%s);".replace('elec_rele',releType1_dict[releType1]) % (repr(row[1]), repr(row[2]), repr(row[3]), repr(row[4]), repr(row[5]), repr(row[6]), repr(row[7]))
                cursor.execute(sql_2)  # 填入关联表中
            elif releType1=='2':
                sql_2 = "insert into elec_rele(devInfo,proName,proType,proCode,proProvince,proImpleYear,proDesc) " \
                        "values " \
                        "(%s,%s,%s,%s,%s,%s,%s);".replace('elec_rele', releType1_dict[releType1]) % (
                        repr(row[1]), repr(row[2]), repr(row[3]), repr(row[4]), repr(row[5]), repr(row[6]),
                        repr(row[7]))
                cursor.execute(sql_2)  # 填入关联表中
            else:
                sql_2 = "insert into elec_rele(funInfo,proName,proType,proCode,proProvince,proImpleYear,proDesc) " \
                        "values " \
                        "(%s,%s,%s,%s,%s,%s,%s);".replace('elec_rele', releType1_dict[releType1]) % (
                            repr(row[1]), repr(row[2]), repr(row[3]), repr(row[4]), repr(row[5]), repr(row[6]),
                            repr(row[7]))
                cursor.execute(sql_2)  # 填入关联表中

            sql_3 = "update elec_rele " \
                    "join pro_type " \
                    "on elec_rele.proType = cast(pro_type.proType_id as char) " \
                    "set elec_rele.proType = pro_type.proType " \
                    "where elec_rele.proType = cast(pro_type.proType_id as char);".replace('elec_rele',releType1_dict[releType1])
            cursor.execute(sql_3)  # 更新项目类型，从ID变为字符
            sql_4 = "update elec_rele " \
                    "join pro_addr " \
                    "on elec_rele.proProvince = cast(pro_addr.proAddr_id as char) " \
                    "set elec_rele.proProvince = pro_addr.proAddr " \
                    "where elec_rele.proProvince = cast(pro_addr.proAddr_id as char);".replace('elec_rele',releType1_dict[releType1])
            cursor.execute(sql_4)  # 更新项目地址，从ID变为字符
    except Exception as e:
        connect.rollback()  # 事务回滚
        print('事务处理失败', e)
    else:
        connect.commit()  # 事务提交
        print('处理成功')
    # 关闭连接
    cursor.close()
    connect.close()

# writeReleTable(releType1,releType2,proType,proAddr,releObject,startYear,endYear):
# writeReleTable('1','1','0','0','3','2010','2010')  # 电气关联，变电站，所有专项，湖北，凤凰山变，2016-2019 的所有项目
if __name__=='__main__':
    pass