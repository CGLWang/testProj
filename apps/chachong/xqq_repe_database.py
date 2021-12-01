#auther:"l"
#date:2019/7/19

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
    return connect, cursor

"""
key: 传入需要导出的项目pro_repe_id
['72','85','128’]
"""
def writeRepe_export(list_pro_repe_id):
    connect, cursor = connectSql()
    # key = str(key)
    print('W',list_pro_repe_id)
    if list_pro_repe_id != ():
        id_str = ','.join(str(i[0]) for i in list_pro_repe_id)
        print(id_str)
        # print(type(id_str))
        try:
            sql_turncate = "TRUNCATE TABLE repe_export"
            cursor.execute(sql_turncate)
            print('repe_export关联表初始化成功')
            # sql = "SELECT repeatcheck_cache.proName,repeatcheck_cache.proType_id,repeatcheck_cache.proImpleYear,multisource_data.proName,multisource_data.proType_id,multisource_data.proImpleYear,pro__repe.repetion " \
            #       "FROM pro__repe " \
            #       "JOIN  repeatcheck_cache  ON  (pro__repe.pro_repe_id = repeatcheck_cache.id ) " \
            #       "JOIN  multisource_data   ON  (pro__repe.repe_id = multisource_data.id ) " \
            #       "WHERE pro__repe.pro_repe_id in (%s));" % (id_str)
            sql = "SELECT repeatcheck_cache.proName,repeatcheck_cache.proType_repeid,repeatcheck_cache.proImpleYear,multisource_data.proName,multisource_data.proType_id,multisource_data.proImpleYear,pro__repe.repetion " \
                  "FROM pro__repe " \
                  "JOIN  repeatcheck_cache  ON  (pro__repe.pro_repe_id = repeatcheck_cache.id ) " \
                  "JOIN  multisource_data   ON  (pro__repe.repe_id = multisource_data.id ) " \
                  "WHERE pro__repe.pro_repe_id in (72,128);"
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
            sql_1 = "insert into repe_export(pro_name, pro_type, pro_year, repe_name, repe_type, repe_year, repetion) " \
                  "SELECT repeatcheck_cache.proName,repeatcheck_cache.proType_repeid,repeatcheck_cache.proImpleYear,multisource_data.proName,multisource_data.proType_id,multisource_data.proImpleYear,pro__repe.repetion " \
                  "FROM pro__repe " \
                  "JOIN  repeatcheck_cache  ON  (pro__repe.pro_repe_id = repeatcheck_cache.id ) " \
                  "JOIN  multisource_data   ON  (pro__repe.repe_id = multisource_data.id ) " \
                  "WHERE pro__repe.pro_repe_id in (%s);" % (id_str)
            cursor.execute(sql_1)  # 填入关联表中
            sql_2 = "update repe_export " \
                    "join pro_type " \
                    "on repe_export.pro_type = cast(pro_type.proType_id as char) " \
                    "set repe_export.pro_type = pro_type.proType " \
                    "where repe_export.pro_type = cast(pro_type.proType_id as char);"
            cursor.execute(sql_2)  # 填入关联表中
            sql_3 = "update repe_export " \
                    "join pro_type " \
                    "on repe_export.repe_type = cast(pro_type.proType_id as char) " \
                    "set repe_export.repe_type = pro_type.proType " \
                    "where repe_export.repe_type = cast(pro_type.proType_id as char);"
            cursor.execute(sql_3)  # 填入关联表中
        except Exception as e:
            connect.rollback()  # 事务回滚
            print('事务处理失败', e)
        else:
            connect.commit()  # 事务提交
            print('处理成功')
    else:
        sql_turncate = "TRUNCATE TABLE repe_export"
        cursor.execute(sql_turncate)
    # 关闭连接
    cursor.close()
    connect.close()