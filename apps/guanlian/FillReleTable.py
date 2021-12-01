#!-*- coding:utf-8 -*-

import pymysql
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



def writeElec_rele(connect, cursor, proType, proAddr,relaType, relaObject):
    proType_list = [1,2,3,4,5,6,7,8,9,10,11]
    try:
        sql_turncate = "TRUNCATE TABLE elec_rele;"
        cursor.execute(sql_turncate)
        print('elec_rele关联表初始化成功')
        # for i in range(len(substation)):
        if relaType == '1':  # 变电站
            if proType in proType_list:
                sql_1 = "SELECT multisource_data.id,substation.substation,multisource_data.proType_id,multisource_data.proName,multisource_data.proCode,multisource_data.proImpleYear " \
                    "FROM pro__substation " \
                    "JOIN  multisource_data  ON  (pro__substation.pro_substation_id = multisource_data.id ) " \
                    "JOIN  substation   ON  (pro__substation.substation_id = substation.substation_id ) " \
                    "WHERE (pro__substation.substation_id='%d') and (multisource_data.province_id='%d') and(multisource_data.proType_id='%d');" % (int(relaObject),int(proAddr),int(proType))
            else:
                sql_1 = "SELECT multisource_data.id,substation.substation,multisource_data.proType_id,multisource_data.proName,multisource_data.proCode,multisource_data.proImpleYear " \
                        "FROM pro__substation " \
                        "JOIN  multisource_data  ON  (pro__substation.pro_substation_id = multisource_data.id ) " \
                        "JOIN  substation   ON  (pro__substation.substation_id = substation.substation_id ) " \
                        "WHERE (pro__substation.substation_id='%d') and (multisource_data.province_id='%d');" % (int(relaObject), int(proAddr))

        if relaType == '2':  # 线路
            if proType in proType_list:
                sql_1 = "SELECT multisource_data.id,circuit.circuit,multisource_data.proType_id,multisource_data.proName,multisource_data.proCode,multisource_data.proImpleYear " \
                        "FROM pro__circuit " \
                        "JOIN  multisource_data  ON  (pro__circuit.pro_circuit_id = multisource_data.id ) " \
                        "JOIN  circuit   ON  (pro__circuit.circuit_id = circuit.circuit_id ) " \
                        "WHERE (pro__circuit.circuit_id='%d') and (multisource_data.province_id='%d') and(multisource_data.proType_id='%d');" % (int(relaObject), int(proAddr),int(proType))

            else:
                sql_1 ="SELECT multisource_data.id,circuit.circuit,multisource_data.proType_id,multisource_data.proName,multisource_data.proCode,multisource_data.proImpleYear " \
                "FROM pro__circuit " \
                "JOIN  multisource_data  ON  (pro__circuit.pro_circuit_id = multisource_data.id ) " \
                "JOIN  circuit   ON  (pro__circuit.circuit_id = circuit.circuit_id ) " \
                "WHERE (pro__circuit.circuit_id='%d') and (multisource_data.province_id='%d');" % (int(relaObject), int(proAddr))

        cursor.execute(sql_1)  # 查找关联项目
        for row in cursor.fetchall():
            print('ROW',row)
            sql_2 = "insert into elec_rele(id,eleInfo,proType,proName,proCode,proImpleYear,corValue) " \
                    "values " \
                    "(%d,%s,%s,%s,%s,%s,1) on duplicate key update id=%d;" % (list(row)[0], repr(list(row)[1]), repr(list(row)[2]), repr(list(row)[3]), repr(list(row)[4]),repr(list(row)[5]),list(row)[0])
            cursor.execute(sql_2)  # 填入关联表中
            sql_3 = "update elec_rele " \
                    "join pro_type " \
                    "on elec_rele.proType = cast(pro_type.proType_id as char) " \
                    "set elec_rele.proType = pro_type.proType " \
                    "where elec_rele.proType = cast(pro_type.proType_id as char)";
            cursor.execute(sql_3)  # 更新项目类型，从ID变为字符
    except Exception as e:
        connect.rollback()  # 事务回滚
        print('事务处理失败', e)
    else:
        connect.commit()  # 事务提交
        print('处理成功')
    # 关闭连接
    cursor.close()
    connect.close()


def writeDev_rele(connect, cursor, proType, proAddr,relaType, relaObject):
    proType_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    try:
        sql_turncate = "TRUNCATE TABLE dev_rele;"
        cursor.execute(sql_turncate)
        print('dev_rele关联表初始化成功')
        if relaType == '1':  # 变电站
            if proType in proType_list:
                sql_1 = "SELECT multisource_data.id,substation.substation,multisource_data.proType_id,multisource_data.proName,multisource_data.proCode,multisource_data.proImpleYear " \
                    "FROM pro__substation " \
                    "JOIN  multisource_data  ON  (pro__substation.pro_substation_id = multisource_data.id ) " \
                    "JOIN  substation   ON  (pro__substation.substation_id = substation.substation_id ) " \
                    "WHERE (pro__substation.substation_id='%d') and (multisource_data.province_id='%d') and(multisource_data.proType_id='%d');" % (int(relaObject),int(proAddr),int(proType))
            else:
                sql_1 ="SELECT multisource_data.id,substation.substation,multisource_data.proType_id,multisource_data.proName,multisource_data.proCode,multisource_data.proImpleYear " \
                      "FROM pro__substation " \
                      "JOIN  multisource_data  ON  (pro__substation.pro_substation_id = multisource_data.id ) " \
                      "JOIN  substation   ON  (pro__substation.substation_id = substation.substation_id ) " \
                      "WHERE (pro__substation.substation_id='%d') and (multisource_data.province_id='%d');" % (int(relaObject), int(proAddr))

        if relaType == '3':  # 道路
            if proType in proType_list:
                sql_1 = "SELECT multisource_data.id,road.road,multisource_data.proType_id,multisource_data.proName,multisource_data.proCode,multisource_data.proImpleYear " \
                        "FROM pro__road " \
                        "JOIN  multisource_data  ON  (pro__road.pro_road_id = multisource_data.id ) " \
                        "JOIN  road   ON  (pro__road.road_id = road.road_id ) " \
                        "WHERE (pro__road.road_id='%d') and (multisource_data.province_id='%d') and(multisource_data.proType_id='%d');" % (int(relaObject), int(proAddr), int(proType))

            else:
                sql_1 = "SELECT multisource_data.id,road.road,multisource_data.proType_id,multisource_data.proName,multisource_data.proCode,multisource_data.proImpleYear " \
                        "FROM pro__road " \
                        "JOIN  multisource_data  ON  (pro__road.pro_road_id = multisource_data.id ) " \
                        "JOIN  road   ON  (pro__road.road_id = road.road_id ) " \
                        "WHERE (pro__road.road_id='%d') and (multisource_data.province_id='%d');" % (int(relaObject), int(proAddr))
        if relaType == '4':  # TODO：杆塔
            if proType in proType_list:
                sql_1 = "SELECT multisource_data.id,multisource_data.proType_id,multisource_data.proName,multisource_data.proCode,multisource_data.proImpleYear " \
                        "FROM pro__tower " \
                        "JOIN  multisource_data  ON  (pro__tower.pro_tower_id = multisource_data.id ) " \
                        "WHERE (multisource_data.province_id='%d') and(multisource_data.proType_id='%d');" % (int(proAddr), int(proType))

            else:
                sql_1 = "SELECT multisource_data.id,multisource_data.proType_id,multisource_data.proName,multisource_data.proCode,multisource_data.proImpleYear " \
                        "FROM pro__tower " \
                        "JOIN  multisource_data  ON  (pro__tower.pro_tower_id = multisource_data.id ) " \
                        "WHERE (multisource_data.province_id='%d');" % (int(proAddr))

        cursor.execute(sql_1)  # 查找关联项目
        for row in cursor.fetchall():
            print(row)
            if relaType!='4':

                sql_2 = "insert into dev_rele(id,devInfo,proType,proName,proCode,proImpleYear,corValue) " \
                    "values " \
                    "(%d,%s,%s,%s,%s,%s,1) on duplicate key update id=%d;" % (list(row)[0], repr(list(row)[1]), repr(list(row)[2]), repr(list(row)[3]), repr(list(row)[4]),repr(list(row)[5]),list(row)[0])
            else:
                sql_2 = "insert into dev_rele(id,devInfo,proType,proName,proCode,proImpleYear,corValue) " \
                        "values " \
                        "(%d,'杆塔',%s,%s,%s,%s,1) on duplicate key update id=%d;" % (list(row)[0], repr(list(row)[1]), repr(list(row)[2]), repr(list(row)[3]),repr(list(row)[4]),list(row)[0])

            cursor.execute(sql_2)  # 填入关联表中
            sql_3 = "update dev_rele " \
                    "join pro_type " \
                    "on dev_rele.proType = cast(pro_type.proType_id as char) " \
                    "set dev_rele.proType = pro_type.proType " \
                    "where dev_rele.proType = cast(pro_type.proType_id as char)";
            cursor.execute(sql_3)  # 更新项目类型，从ID变为字符
    except Exception as e:
        connect.rollback()  # 事务回滚
        print('事务处理失败', e)
    else:
        connect.commit()  # 事务提交
        print('处理成功')
    # 关闭连接
    cursor.close()
    connect.close()


def writeFun_rele(connect, cursor, proType, proAddr,relaType, relaObject):
    proType_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    try:
        sql_turncate = "TRUNCATE TABLE fun_rele;"
        cursor.execute(sql_turncate)
        print('fun_rele关联表初始化成功')
        if relaType == '5':  #园区
            if proType in proType_list:
                sql_1 = "SELECT multisource_data.id,facility.facility,multisource_data.proType_id,multisource_data.proName,multisource_data.proCode,multisource_data.proImpleYear " \
                        "FROM pro__facility " \
                        "JOIN  multisource_data  ON  (pro__facility.pro_facility_id = multisource_data.id ) " \
                        "JOIN  facility   ON  (pro__facility.facility_id = facility.facility_id ) " \
                        "WHERE (pro__facility.facility_id='%d') and (multisource_data.province_id='%d') and(multisource_data.proType_id='%d');" % (int(relaObject), int(proAddr), int(proType))

            else:
                sql_1 = "SELECT multisource_data.id,facility.facility,multisource_data.proType_id,multisource_data.proName,multisource_data.proCode,multisource_data.proImpleYear " \
                    "FROM pro__facility " \
                    "JOIN  multisource_data  ON  (pro__facility.pro_facility_id = multisource_data.id ) " \
                    "JOIN  facility   ON  (pro__facility.facility_id = facility.facility_id ) " \
                    "WHERE (pro__facility.facility_id='%d') and (multisource_data.province_id='%d');" % (int(relaObject), int(proAddr))

        cursor.execute(sql_1)  # 查找关联项目
        for row in cursor.fetchall():
            print(row)
            sql_2 = "insert into fun_rele(id,funInfo,proType,proName,proCode,proImpleYear,corValue) " \
                    "values " \
                    "(%d,%s,%s,%s,%s,%s,1) on duplicate key update id=%d;" % (list(row)[0], repr(list(row)[1]), repr(list(row)[2]), repr(list(row)[3]), repr(list(row)[4]),repr(list(row)[5]),list(row)[0])
            cursor.execute(sql_2)  # 填入关联表中
            sql_3 = "update fun_rele " \
                    "join pro_type " \
                    "on fun_rele.proType = cast(pro_type.proType_id as char) " \
                    "set fun_rele.proType = pro_type.proType " \
                    "where fun_rele.proType = cast(pro_type.proType_id as char)";
            cursor.execute(sql_3)  # 更新项目类型，从ID变为字符
    except Exception as e:
        connect.rollback()  # 事务回滚
        print('事务处理失败', e)
    else:
        connect.commit()  # 事务提交
        print('处理成功')
    # 关闭连接
    cursor.close()
    connect.close()

def fillReleTable(proType,proAddr,relaClass,relaType,relaObject):
    # 有二级目录时调用
    # keyword_list = FindKeyWords.getkeyword(P_name=P_name, P_content=P_content, C_type1=C_type1, C_type2=C_type2)
    connect, cursor = connectSql()
    if relaClass == '1':#电气关联
        writeElec_rele(connect, cursor,proType,proAddr,relaType, relaObject)
    if relaClass == '2':#设备关联
        writeDev_rele(connect, cursor,proType,proAddr,relaType, relaObject)
    if relaClass == '3':#功能关联
        writeFun_rele(connect, cursor,proType,proAddr,relaType, relaObject)
    pass

if __name__ == "__main__":
    from guifan import Inspection

    connect = pymysql.connect(host=HOST, user=USER, password=PASW, database=DATB)
    cursor = connect.cursor()
    try:
        sql0 = "SELECT proName FROM gw1.multisource_data ;"
        cursor.execute(sql0)
        # 获取所有记录列表
        results = cursor.fetchall()
        print(len(results))
        for row in results:
            # print(row[0])
            value = Inspection.findProvince(row[0])
            # print(value)
            sql_3 = "update multisource_data set province_id='%d' where proName = '%s';" % (value,row[0])
            cursor.execute(sql_3)  # 更新项目类型，从ID变为字符
    except Exception as e:
        connect.rollback()  # 事务回滚
        print('事务处理失败', e)
    else:
        connect.commit()  # 事务提交
        print('处理成功')
        # 关闭连接
        cursor.close()
        connect.close()
# proType='0'
# proAddr='1'
# relaClass='2' # 无编号
# relaType='4' # 无编号
# relaObject='1'# 有表，1对应凤凰山变
# fillReleTable(proType,proAddr,relaClass,relaType,relaObject)