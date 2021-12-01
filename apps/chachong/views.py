from django.shortcuts import render
from django.http import HttpResponse
from chachong import checkrepe, FillRepeTable
from Keywords import FillmidSheet
from utils import sqlhelper
import json
import linecache
import re
import os
import time
from configuration import get_config_values
from chachong import xqq_repe_database
from chachong import xqq_export_repe
from guifan import  FillNormalPro
PORT = int(get_config_values('mysql', 'port'))
HOST = get_config_values('mysql', 'host')
USER = get_config_values('mysql', 'user')
PASW = get_config_values('mysql', 'password')
DATB = get_config_values('mysql', 'database')


#TODO:填表函数
import pymysql


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

def tun():
    connect, cursor = connectSql()
    # key = str(key)
    try:
        sql_key = "SET FOREIGN_KEY_CHECKS=0;"
        cursor.execute(sql_key)
        sql_turncate = "TRUNCATE TABLE repeatcheck_cache;"
        cursor.execute(sql_turncate)
        sql_key = "SET FOREIGN_KEY_CHECKS=1;"
        cursor.execute(sql_key)
    except Exception as e:
        connect.rollback()  # 事务回滚
        print('事务处理失败', e)
    else:
        connect.commit()  # 事务提交
        print('处理成功')
    # 关闭连接
    cursor.close()
    connect.close()


"""
功能：查重文件的录入接口
效果：对文件进行查重，填写查重缓存表，对查重缓存表查重后写中间表和结果表
"""
#
def CC(request):
    if request.method == 'POST':

        print('使用文件查重接口...')
        per = json.loads(request.body)
        print(per)
        if per:

            file_list = per.get('file_list')
            sqls = ['''SET FOREIGN_KEY_CHECKS=0;''','''TRUNCATE TABLE repeatcheck_cache;''','''SET FOREIGN_KEY_CHECKS=1;''']
            sqlhelper.execute_many_sql(sqls)
            # 加入文件格式判断
            for item in file_list:
                title = item['fileName']
                title_pat = '\d+年.*储备表.xls(x*)'
                ans = re.match(title_pat, title)
                if ans == None:
                    response = HttpResponse('''[{"STATE":2, "MESSAGE":"文件格式或文件名不正确，请检查"}]''')
                    response["Access-Control-Allow-Origin"] = "*"
                    response["Content-Type"] = "application/json;charset=UTF-8"
                    return response
            print(file_list,'file')
            # 写查重缓存表repeatcheck_cache
            for item in file_list:
                file_name = item['filePath'] + item['fileName']
                # TODO: 将文件写入到repeatcheck_cache表中 2019-09-06
                FillRepeTable.write_sql2repeatcheck_cache(file_name)
                print('查重缓存表填写完毕！')
                # FillRepeTable.write_data(file_name)
            # 得到每一条的查重结果
            # value = checkrepe.CHA()
            # TODO:查重明细结果20190909
            value = checkrepe.NewCHA()
            # print('VAL',value)
            print('填写查重明细完成！')

            # 写查重中间表pro__repe
            FillmidSheet.fillPro__repe(value)

            # TODO:寫重複結果顯示表
            sqlhelper.execute('''truncate table repe_all''')
            sqlhelper.execute('''insert into repe_all(proId,proName,proDesc,proImpleYear) 
                                select distinct rc.id,rc.proName,rc.proDesc,rc.proImpleYear from pro__repe as pr 
                                inner join repeatcheck_cache as rc on pr.pro_repe_id=rc.id''')

            # TODO：写查重HTML文件
            response = HttpResponse('''[{"STATE": 0,"MESSAGE":"请求成功"}]''')
            response["Access-Control-Allow-Origin"] = "*"
            response["Content-Type"] = "application/json;charset=UTF-8"
            return response
        response = HttpResponse('''[{"STATE":1, "MESSAGE":"服务器响应超时"}]''')
        response["Access-Control-Allow-Origin"] = "*"
        response["Content-Type"] = "application/json;charset=UTF-8"
        return response
    response = HttpResponse('''[{"STATE":1, "MESSAGE":"服务器响应超时"}]''')
    response["Access-Control-Allow-Origin"] = "*"
    response["Content-Type"] = "application/json;charset=UTF-8"
    return response

"""
功能：查重界面下一步按钮
效果：将不打钩的列表传入，修改repe_all和midresult状态值，填写确认后的查重结果表
"""
#TODO:20190718查重下一步写查重确认表
def chachong_confirm(request):
    """

    :param request: 收到打钩的ID列表（）
    :return:没有返回，直接准备写导出表
    """
    if request.method == 'POST':
        request_data = json.loads(request.body)
        xqqlist = []
        if request_data:
            #返回的是不重复列表
            request_data = request_data.get('ID_List')
            print('视为不重复的列表:',request_data)
            if request_data!=[]:
                # 1表示重复
                sqlhelper.execute(""" update  repe_all set CCStatus = 1; """)
                sqlhelper.execute(""" update  midresult set CCStatus = 0; """)
                for item in request_data:
                    #确认后修改规范值
                    #TODO:20190718确认后修改repe_all表的重复状态值
                    #改不规范表的status
                    sqlhelper.execute(""" update  repe_all set CCStatus = 0 where proId= %s; """% (item['proID']))
            xqqtup = sqlhelper.get_list("""select proID from repe_all where CCStatus = 1""")
            # [str(i[0]) for i in xqqtup]
            for proid in xqqtup:
                sqlhelper.execute(""" update  midresult set CCStatus = 1 where id= %s; """% (proid[0]))

            # TODO:XQQ将确认后的表写出来
            xqq_repe_database.writeRepe_export(xqqtup)

            response = HttpResponse('''[{"STATE": 0,"MESSAGE":"请求成功"}]''')
            response["Access-Control-Allow-Origin"] = "*"
            response["Content-Type"] = "application/json;charset=UTF-8"
            return response
        else:
            response = HttpResponse('''[{"STATE": 1,"MESSAGE":"服务器没有收到数据"}]''')
            response["Access-Control-Allow-Origin"] = "*"
            response["Content-Type"] = "application/json;charset=UTF-8"
            return response

    else:
        response = HttpResponse('''[{"STATE":2, "MESSAGE":"请求方法有误"}]''')
        response["Access-Control-Allow-Origin"] = "*"
        response["Content-Type"] = "application/json;charset=UTF-8"
        return response


"""
功能：查重界面导出按钮
效果：将查重结果表导出为excel
"""
import socket
def get_host_ip():
    """
    查询本机ip地址
    :return:
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip
def export(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        print(request_data)
        if request_data:
           if request_data.get("export")== 1:
                #TODO: 写excel 返回一个下载链接
                mypth = os.path.abspath('.') + '\\exportfile\\REPEXPORT\\'
                cur_time = '重复内容'+time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())+ '.xls'
                file_name = mypth + cur_time
                print('写文件名',file_name)
                # TODO:下载链接怎么写。
                xqq_export_repe.exportRepeTable(file_name)
                dowmload_link = 'http://'+str(get_host_ip())+':8000/exportfile/REPEXPORT/' + cur_time
                # dowmload_link = 'http://127.0.0.1:8081/exportfile/REPEXPORT/' + cur_time
                print('传文件名',dowmload_link)
                response = HttpResponse('''[{
                "Status": 0,
                "downLink":"%s"
                }
                ]''' % dowmload_link)
                response["Access-Control-Allow-Origin"] = "*"
                response["Content-Type"] = "application/json;charset=UTF-8"
        else:
            response = HttpResponse('''[{
                    "Status": 0,
                    "downLink":None
                    }
                    ]''')
            response["Access-Control-Allow-Origin"] = "*"
            response["Content-Type"] = "application/json;charset=UTF-8"
    return response


"""
功能：查重明细
效果：从pro__repe表中取出相应明细
"""
def detail(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        print(request_data)
        if request_data:
            pro_id = request_data.get('id')
            print('WhatID',int(pro_id['proID']))
            # FillRepeTable.writeRepe_pro(pro_id)
            checkrepe.repeat_detail(int(pro_id['proID']))
            response = HttpResponse('''[{"STATE": 0}]''')
            response["Access-Control-Allow-Origin"] = "*"
            response["Content-Type"] = "application/json;charset=UTF-8"
            return response
        response = HttpResponse('''[{"STATE": 1}]''')
        response["Access-Control-Allow-Origin"] = "*"
        response["Content-Type"] = "application/json;charset=UTF-8"
        return response
    response = HttpResponse('''[{"STATE": 2}]''')
    response["Access-Control-Allow-Origin"] = "*"
    response["Content-Type"] = "application/json;charset=UTF-8"
    return response


"""*****************************************************以下为项目录入模块独有*****************************************"""
"""
功能：项目录入中规范检查到查重检查的下一步按钮
效果：将查重结果表导出为excel
"""
def chachong():
        print('进入录入查重部分')
        # TODO：20190718这里填写中间表修改
        sqls = ['''SET FOREIGN_KEY_CHECKS=0;''', '''TRUNCATE TABLE repeatcheck_cache;''',
                '''SET FOREIGN_KEY_CHECKS=1;''']
        sqlhelper.execute_many_sql(sqls)
        # multisource表到repeatcheck_cache表
        #todo:修改转移的内容
        sqlhelper.execute('''insert into repeatcheck_cache(proType_repeid,proName,proDesc,proImpleYear,province_repeid,proCode,proSeg,proUnit_repeid,volLevel_repeid,proAddr) 
                                        select distinct rc.proType_nameid,rc.proName,rc.proDesc,rc.proImpleYear,rc.province_nameid,rc.proCode,rc.proSeg,rc.proUnit_nameid,rc.volLevel_nameid,rc.proAddr_nameid
                                         from midresult as rc 
                                        ''')
        # value = checkrepe.CHA()
        # TODO:20190909使用新的查重
        value = checkrepe.NewCHA()
        # repeword = str(CC_highlight(value[0][0], value[0][1]))
        # value.append(repeword)
        # print('VAL',value)

        # TODO:查重中间表
        FillmidSheet.fillPro__repe(value)
        # TODO:寫重複結果顯示表
        sqlhelper.execute('''truncate table repe_all''')
        sqlhelper.execute('''insert into repe_all(proId,proName,proDesc,proImpleYear) 
                            select distinct rc.id,rc.proName,rc.proDesc,rc.proImpleYear from pro__repe as pr 
                            inner join repeatcheck_cache as rc on pr.pro_repe_id=rc.id''')



if __name__ == '__main__':
    # PROID = {'proID':1}
    # value = checkrepe.CHA(PROID)
    # #print(value[0][0])
    # CC_highlight(value[0][0],value[0][1])
    # sqls = ['''SET FOREIGN_KEY_CHECKS=0;''', '''TRUNCATE TABLE repeatcheck_cache;''', '''SET FOREIGN_KEY_CHECKS=1;''']
    # sqlhelper.execute_many_sql(sqls)
    # sqlhelper.execute('''insert into repeatcheck_cache(proType_id,proName,proDesc,proImpleYear)
    #                                 select distinct rc.proType_id,rc.proName,rc.proDesc,rc.proImpleYear from multisource_data as rc
    #                                 ''')
    # mydict = {"A":1,"B":2}
    # print(mydict.get("c"))
    cur_time = '重复内容' + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + '.xls'
    print(cur_time)
    time.sleep(3)
    a = cur_time
    print(a)