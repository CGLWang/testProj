#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : guanlianStatistics.py
@Author: CQ
@Date  : 2019/5/25 9:50
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
key: 用来选择填写统计的哪个表
(substation'，'circuit'，'road'，'facility')
"""
def writeRele_statistics(releType2):
    print(releType2)
    releType2_dict = {
        '1': 'substation',
        '2': 'circuit',
        '3': 'road',
        '4': 'facility'
    }
    key = releType2_dict[releType2]
    print('KEY',key)
    connect, cursor = connectSql()
    # key = str(key)
    try:
        sql_turncate = "TRUNCATE TABLE rele_statistics_substation;".replace('substation', key)
        cursor.execute(sql_turncate)
        print('rele_statistics_substation关联表初始化成功'.replace('substation', key))
        # 查询有多少个变电站
        sql_1 = "select count(*) from substation".replace('substation', key)
        cursor.execute(sql_1)  # 查找关联项目
        # print(cursor.fetchall()[0][0])
        # num = cursor.fetchall()[0][0]

        # 查询变电站所有的名字
        sql_2 = "select substation_id from substation".replace('substation', key)
        cursor.execute(sql_2)  # 查找关联项目id
        # print(cursor.fetchall())
        result1 = cursor.fetchall()
        for item in result1:
            # 查询每一个变电站所有相关联的项目
            sql_3 = "SELECT pro__substation.pro_substation_id from pro__substation where (substation_id='%d');".replace('substation', key) % \
                    item[0]

            cursor.execute(sql_3)
            result2 = cursor.fetchall()
            # print(result2)
            pro = tuple(np.array(result2).reshape([-1]))
            every_pro_num = len(pro)
            # print('{}'.format(pro))
            # print(type(pro))
            pro = ','.join('%s' % id for id in pro)  # 此处的pidList是一个元组
            # print('pro',pro)
            if pro != '':
                #TODO :这里加一个变电站/...在信息表中的ID
                sql_41 = "select '%s','%d',sum(totalInvest),sum(annPlan) FROM multisource_data where id in (%s);".replace('substation', key)% (str(item[0]), every_pro_num, pro)
                cursor.execute(sql_41)

                part1 = cursor.fetchall()
                part2 = list(part1[0])
                part2.append(item[0])
                print(part2)

                # sql_42 = "insert into rele_statistics_substation(substation,sum_num,sum_totalInvest,sum_annPlan,substation_id) values('%s','%s','%f','%f','%d') "\
                #          % (part2[0],part2[1],part2[2],part2[3],part2[4])
                sql_42 = "insert into rele_statistics_substation(substation,sum_num,sum_totalInvest,sum_annPlan,substation_id) values(%s,%s,%s,%s,%s);".replace('substation', key)
                cursor.execute(sql_42,part2)
                # sql_4 = "insert into rele_statistics_substation(substation,sum_num,sum_totalInvest,sum_annPlan) " \
                #     "select '%s','%d',sum(totalInvest),sum(annPlan) FROM multisource_data where id in (%s);".replace('substation', key) \
                #     % (str(item[0]), every_pro_num, pro)
                # cursor.execute(sql_4)

                sql_5 = "update rele_statistics_substation " \
                        "join substation " \
                        "on rele_statistics_substation.substation = cast(substation.substation_id as char) " \
                        "set rele_statistics_substation.substation = substation.substation " \
                        "where rele_statistics_substation.substation = cast(substation.substation_id as char);".replace('substation', key)
                cursor.execute(sql_5)  # 更新项目类型，从ID变为字符
    except Exception as e:
        connect.rollback()  # 事务回滚
        print('事务处理失败', e)
    else:
        connect.commit()  # 事务提交
        print('处理成功')
    # 关闭连接
    cursor.close()
    connect.close()

if __name__ == '__main__':
    writeRele_statistics('1')
    writeRele_statistics('2')
    # writeRele_statistics(key='road')
    # writeRele_statistics(key='facility')
