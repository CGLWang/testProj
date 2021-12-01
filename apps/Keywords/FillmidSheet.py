from Keywords import FindKeyWords
import pymysql
from configuration import get_config_values

PORT = int(get_config_values('mysql', 'port'))
HOST = get_config_values('mysql', 'host')
USER = get_config_values('mysql', 'user')
PASW = get_config_values('mysql', 'password')
DATB = get_config_values('mysql', 'database')

def fillpro__facility():
    # FILL_list = []
    # functiondict = {}
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
    try:
        sql_turncate = "TRUNCATE TABLE pro__facility;"
        cursor.execute(sql_turncate)
        sql_turncate = "alter table pro__facility auto_increment=1;"
        cursor.execute(sql_turncate)
        print('pro__facility关联表初始化成功')
        sql0 = "SELECT id,proDesc,proName FROM multisource_data ;"
        # 执行SQL语句
        cursor.execute(sql0)
        # 获取所有记录列表
        results = cursor.fetchall()
        # print(results)
        for row in results:
            functionlist = FindKeyWords.findfunctions(row[2],row[1])
            # print(functionlist)
            # functiondict['P_ID'] = row[0]
            # functiondict['facility'] = functionlist
            if functionlist != []:
                for i in range(len(functionlist)):
                    sql1 = "insert into pro__facility(pro_facility_id,facility_id) select '%d',facility_id from facility where(facility= '%s');"% (row[0],functionlist[i])
                    cursor.execute(sql1)
                # FILL_list.append(functiondict.copy())
    except Exception as e:
        connect.rollback()  # 事务回滚
        print('事务处理失败', e)
    else:
        connect.commit()  # 事务提交
        print('处理成功')
    # 关闭连接
    cursor.close()
    connect.close()
    pass


def fillPro__circuit():
    # FILL_list = []
    # functiondict = {}
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
    try:
        sql_turncate = "TRUNCATE TABLE pro__circuit;"
        cursor.execute(sql_turncate)
        sql_turncate = "alter table pro__circuit auto_increment=1;"
        cursor.execute(sql_turncate)
        print('pro__circuit关联表初始化成功')
        sql0 = "SELECT id,proDesc,proName FROM multisource_data ;"
        # 获取所有同杆项目的ID号
        # 执行SQL语句
        cursor.execute(sql0)
        # 获取所有记录列表
        results = cursor.fetchall()
        # print(results)
        for row in results:
            functionlist = FindKeyWords.findlines(row[1])
            # print(functionlist)
            # functiondict['P_ID'] = row[0]
            # functiondict['facility'] = functionlist
            if functionlist != []:
                for i in range(len(functionlist)):
                    sql1 = "insert into pro__circuit(pro_circuit_id,circuit_id) select '%d',circuit_id from circuit where(circuit= '%s');"% (row[0],functionlist[i])
                    cursor.execute(sql1)
                # FILL_list.append(functiondict.copy())
    except Exception as e:
        connect.rollback()  # 事务回滚
        print('事务处理失败', e)
    else:
        connect.commit()  # 事务提交
        print('处理成功')
    # 关闭连接
    cursor.close()
    connect.close()
    pass


def fillPro__substation():
    # FILL_list = []
    # functiondict = {}
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
    try:
        sql_turncate = "TRUNCATE TABLE pro__substation;"
        cursor.execute(sql_turncate)
        sql_turncate = "alter table pro__substation auto_increment=1;"
        cursor.execute(sql_turncate)
        print('pro__substation关联表初始化成功')
        sql0 = "SELECT id,proDesc,proName FROM multisource_data ;"
        # 获取所有同杆项目的ID号
        # 执行SQL语句
        cursor.execute(sql0)
        # 获取所有记录列表
        results = cursor.fetchall()
        # print(results)
        for row in results:
            functionlist = FindKeyWords.findsubstation(row[1])
            # print(functionlist)
            # functiondict['P_ID'] = row[0]
            # functiondict['facility'] = functionlist
            if functionlist != []:
                for i in range(len(functionlist)):
                    sql1 = "insert into pro__substation(pro_substation_id,substation_id) select '%d',substation_id from substation where(substation= '%s');"% (row[0],functionlist[i])
                    cursor.execute(sql1)
                # FILL_list.append(functiondict.copy())
    except Exception as e:
        connect.rollback()  # 事务回滚
        print('事务处理失败', e)
    else:
        connect.commit()  # 事务提交
        print('处理成功')
    # 关闭连接
    cursor.close()
    connect.close()
    pass


def fillPro__road():
    # FILL_list = []
    # functiondict = {}
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
    try:
        sql_turncate = "TRUNCATE TABLE pro__road;"
        cursor.execute(sql_turncate)
        sql_turncate = "alter table pro__road auto_increment=1;"
        cursor.execute(sql_turncate)
        print('pro__road关联表初始化成功')
        sql0 = "SELECT id,proDesc,proName FROM multisource_data ;"
        # 获取所有同杆项目的ID号
        # 执行SQL语句
        cursor.execute(sql0)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            functionlist = FindKeyWords.findway(row[2],row[1])
            # functiondict['P_ID'] = row[0]
            # functiondict['facility'] = functionlist
            if functionlist != []:
                for i in range(len(functionlist)):
                    sql1 = "insert into pro__road(pro_road_id,road_id) select '%d',road_id from road where(road= '%s');"% (row[0],functionlist[i])
                    cursor.execute(sql1)
                # FILL_list.append(functiondict.copy())
    except Exception as e:
        connect.rollback()  # 事务回滚
        print('事务处理失败', e)
    else:
        connect.commit()  # 事务提交
        print('处理成功')
    # 关闭连接
    cursor.close()
    connect.close()
    pass
    # print(FILL_list)
    # return FILL_list
    # return tower_list


def fillPro__repe(value):
    # FILL_list = []
    # functiondict = {}
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
    try:

        #sql_turncate = "TRUNCATE TABLE pro__repe;"
        sql_turncate = "delete from pro__repe;"
        cursor.execute(sql_turncate)

        sql_turncate = "alter table pro__repe auto_increment=1;"
        cursor.execute(sql_turncate)

        print('pro__repe中间表初始化成功')
        for item in value:
            # print(item)
            sql1 = """insert into pro__repe(pro_repe_id,repe_id,repetion,repe_word) values ('%d','%d','%f',"%s")""" % (item[0],item[1],item[2],item[3])
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
    pass
    # print(FILL_list)
    # return FILL_list
    # return tower_list

# fillpro__facility()
# fillPro__circuit()
# fillPro__substation()
# fillPro__road()

if __name__ == '__main__':
    fillPro__repe([[1, 287, 0.2445, "['中文','B']"]])