from django.shortcuts import render
from django.http import HttpResponse
import json
from jiqun import predict
# Create your views here.

from guifan import FillNormalPro
from utils import sqlhelper
from Keywords import FillmidSheet
import re
import pymysql
from configuration import get_config_values
from chachong import views
import os
import time
from guifan import xqq_eport_norm

PORT = int(get_config_values('mysql', 'port'))
HOST = get_config_values('mysql', 'host')
USER = get_config_values('mysql', 'user')
PASW = get_config_values('mysql', 'password')
DATB = get_config_values('mysql', 'database')
database = DATB
host=HOST
user=USER
port=PORT
passwd=PASW
charset='utf8'

def checkfile(fileitem):
    connect = pymysql.connect(host=host, user=user, password=passwd, database=database)
    cursor = connect.cursor()
    check_list = []
    try:
        sql0 = "SELECT table_name FROM import_table;"
        cursor.execute(sql0)
        results = cursor.fetchall()
        #print('RR',list(results))
        for item in list(results):
            #print('CCCCCC',item[0])
            check_list.append(item[0])
        if fileitem in check_list:
            return fileitem
        # else:
        #     sql1 = "insert into import_table(table_name) values ('%s');" % fileitem
        #     cursor.execute(sql1)

    except Exception as e:
        connect.rollback()  # 事务回滚
        print('文件查重事务处理失败', e)
    else:
        connect.commit()  # 事务提交
        print('文件查重处理成功')
        # 关闭连接
        cursor.close()
        connect.close()
        return False



'''
功能：规范检查 和 项目录入 的文件接口
效果：第一次填缓存表，第一次填不规范表
'''
def FinishFillNormalPro(request):
    # database='guowang'
    # 获取填表开始信号
    if request.method=='POST':
        # 是否有参数传入
        #print(request.body)
        per = json.loads(request.body)
        print(per)
        # if request.POST:
        #a = request.POST.get('a', 0)
        if per:
            print('获取一次填表信息')
            # 填缓存表和不规范表
            file_list = per.get('file_list')
            print('file_list',file_list)
            #清空缓存表
            FillNormalPro.delete_normcheck_cache()
            for item in file_list:
                file_name = item['filePath']+item['fileName']
                print('file_name',file_name)
                print('table_name',item['fileName'][:-4])
                # TODO:这里准备启用防止表重复录入
                # checkfileresut = checkfile(item['fileName'][:-4])
                # if checkfileresut:
                #     response = HttpResponse('''[{"STATE":3, "MESSAGE":"%s已在库中，请检查"}]'''%(checkfileresut))
                #     response["Access-Control-Allow-Origin"] = "*"
                #     response["Content-Type"] = "application/json;charset=UTF-8"
                #     return response

                #TODO：准备启用防止无关表写入

                title = item['fileName']
                print(title ,'title')
                title_pat = '\d+年.*储备表.xls(x*)'
                ans = re.match(title_pat, title)
                if ans == None:
                    response = HttpResponse('''[{"STATE":2, "MESSAGE":"文件格式或文件名不正确，请检查"}]''')
                    response["Access-Control-Allow-Origin"] = "*"
                    response["Content-Type"] = "application/json;charset=UTF-8"
                    return response

                #TODO:检查文件头部1022
                # 一次填表
                FillNormalPro.write_sql2normcheck_cache(file_name)
            # 检查规范
            FillNormalPro.inspection_check()

            # 清除不规范表内的数据
            sqlhelper.execute("truncate table name_norm")
            # 从缓存表写入数据到不规范表
            sqlhelper.execute("""INSERT INTO name_norm (id,proType,proName,proImpleYear,proCode,abnormRea) SELECT id,pro_type.proType,proName,proImpleYear,proCode,abnormRea 
                                FROM normcheck_cache left JOIN pro_type on normcheck_cache.proType_nameid = pro_type.proType_id where normcheck_cache.normValue=1""")

            response = HttpResponse('''[{"STATE": 0,"MESSAGE":"请求成功"}]''')
            response["Access-Control-Allow-Origin"]="*"
            response["Content-Type"]="application/json;charset=UTF-8"
            return response

        response = HttpResponse('''[{"STATE":1, "MESSAGE":"服务器响应超时"}]''')
        response["Access-Control-Allow-Origin"] = "*"
        return response

    else:
        response = HttpResponse('''[{"STATE":1, "MESSAGE":"服务器响应超时"}]''')
        response["Access-Control-Allow-Origin"] = "*"
        return response

'''
功能：规范检查的下一步按钮
    效果：填写name_norm_result表，给第二界面。
'''
#TODO:20190718规范检查的确认
def guifan_confirm(request):
    '''

    :param request: 传入规范的id值
    :return:
    '''
    if request.method == 'POST':
        request_data = json.loads(request.body)

        if request_data:
            request_data = request_data.get('ID_List')
            print('规范确认收到修正ID列表',request_data)
        if request_data!=[]:
            # 1表示不规范
            sqlhelper.execute(""" update  name_norm set GFStatus = 1; """)
            sqlhelper.execute(""" update  normcheck_cache set normValue = 0; """)
            for item in request_data:
                #确认后修改规范值
                #TODO:20190718确认后修改不规范表准备导出
                #改不规范表的status
                sqlhelper.execute(""" update  name_norm set GFStatus = 0 where id= %s; """ % (item['proID']))
            xqqtup = sqlhelper.get_list("""select id from name_norm where GFStatus = 1""")
            # 改缓存表的status
            for proid in xqqtup:
                sqlhelper.execute("""update normcheck_cache set normValue=1 where id= %s; """ % (proid[0]))

        # 清除不规范表内的数据
        sqlhelper.execute("truncate table name_norm_result")
        #写norm_result表，不规范表
        result_command = """INSERT INTO  name_norm_result(proType,proName,proCode,abnormRea,proImpleYear) 
        SELECT proType,proName,proCode,abnormRea,proImpleYear FROM name_norm WHERE GFStatus=1;"""
        sqlhelper.execute(result_command)

        response = HttpResponse('''[{"STATE": 0,"MESSAGE":"请求成功"}]''')
        response["Access-Control-Allow-Origin"] = "*"
        response["Content-Type"] = "application/json;charset=UTF-8"
        return response
    else:
        response = HttpResponse('''[{"STATE":1, "MESSAGE":"服务器响应超时"}]''')
        response["Access-Control-Allow-Origin"] = "*"
        return response




'''功能：规范检查的导出按钮
    效果：导出name_norm_result表的信息到EXCEL
'''
#TODO：XQQ规范检查的导出
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

def guifan_exprot(request):
    """

    :param request:收到导出信号
    :return: 写excel
    """
    if request.method == 'POST':
        request_data = json.loads(request.body)
        print(request_data)
        if request_data:
           if request_data.get("export")== 1:
                #TODO: 写excel 返回一个下载链接
                mypth = os.path.abspath('.') + '/exportfile/NORMEXPORT/'

                cur_time = '不规范内容'+time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())+ '.xls'
                file_name = mypth + cur_time
                # TODO:下载链接怎么写。
                xqq_eport_norm.exportRepeTable(file_name)
                dowmload_link = 'http://'+str(get_host_ip())+':8000/exportfile/NORMEXPORT/'+cur_time
                # dowmload_link = 'http://127.0.0.1:8000/exportfile/NORMEXPORT/' + cur_time
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




"""*****************************************************以下为录入模块所需****************************************"""

# TODO:这是项目录入过程中规范检查的中间录入
'''
功能：项目录入的下一步按钮
效果：将normcheck_cache表中规范的项目导入到midresult表，完成集群的填写
'''
def luru_confirm(request):

    if request.method == 'POST':
        request_data = json.loads(request.body)
        if request_data:
            sin_data = request_data.get('ImportSingal')
            print('收到下一步导入信号',sin_data)
        # if request_data:
        #     request_data = request_data.get('ID_List')
        #     print('request_data::',request_data)
        # if request_data!=[]:
        #     for item in request_data:

        # TODO:集群识别 填表
        jiqunlist = ['战略型','民生型','运营型','提升型','无类型']
        filllist = []
        allitem = sqlhelper.get_list_dict("""SELECT id,proDesc from normcheck_cache """)
        # print(allitem)
        for row in allitem:
            # print(row['proDesc'])
            #todo:20191023项目内容为空的情况
            if row['proDesc']!=None:
                pre_des = re.sub('[\r\n\t]', '', row['proDesc']).replace(' ','')
                # print(pre_des)
                clustr = predict.JQ(pre_des)
            else:
                clustr = '无类型'
            cluindex =jiqunlist.index(clustr)+1
            tup = (cluindex,row['id'])
            filllist.append(tup)

            sqlhelper.execute("""UPDATE normcheck_cache set cluType_nameid=%s where id =%s"""%(tup))

        # 填规范总表
        sqlhelper.execute("truncate table midresult")
        sqlhelper.execute("""insert into midresult (proName,province_nameid,proType_nameid,cluType_nameid,proSeg,proAddr_nameid,proUnit_nameid,volLevel_nameid,proDesc,proNature,scheName,bussSub,proCate,
                                                          proImpleBody,proImpleYear,startTime,endStart,totalInvest,annPlan,proCode)
                            select                        proName,province_nameid,proType_nameid,cluType_nameid,proSeg,proAddr_name,proUnit_nameid,volLevel_nameid,proDesc,
                                                          proNature,scheName,bussSub,proCate,proImpleBody,proImpleYear,startTime,endStart,totalInvest,annPlan,proCode
                            from normcheck_cache where normValue=0 """)
        print('midresult表填写完毕！')


        # TODO:填写对象词典
        #TODO:20190718查重引入
        views.chachong()
        response = HttpResponse('''[{"STATE": 0,"MESSAGE":"请求成功"}]''')
        response["Access-Control-Allow-Origin"] = "*"
        response["Content-Type"] = "application/json;charset=UTF-8"
        return response

    else:
        response = HttpResponse('''[{"STATE": 1,"MESSAGE":"服务器响应超时"}]''')
        response["Access-Control-Allow-Origin"] = "*"
        response["Content-Type"] = "application/json;charset=UTF-8"
        return response

#TODO：20190718项目入库
# 这是项目录入过程中规范检查的最终录入
'''
功能：项目录入的录入按钮
效果：将midresult表中不重复的项目导入到multisource_data表，并完成关联中间表的填写
'''
def final(request):
    """
    :param request:收到录入信号
    :return: 写excel
    """
    if request.method == 'POST':
        request_data = json.loads(request.body)
        if request_data:
            sin_data = request_data.get('ImportSingal')
            print('收到最终录入信号', sin_data)

            if sin_data==1:
                try:
                    selecct_com = """select proName,province_nameid,proType_nameid,cluType_nameid,proSeg,proAddr_nameid,proUnit_nameid,
                                    volLevel_nameid,proDesc,proNature,scheName,bussSub,proCate,proImpleBody,proImpleYear,startTime,endStart,totalInvest,
                                    annPlan,proCode from midresult where midresult.CCStatus=0;"""
                    sobject = sqlhelper.get_list(selecct_com)

                    # fill_com = """insert into multisource_data (proName,province_id,proType_id,cluType_id,proSeg,proAddr_id,proUnit_id,
                    #                 volLevel_id,proDesc,proNature,scheName,bussSub,proCate,proImpleBody,proImpleYear,startTime,endStart,totalInvest,annPlan,proCode)
                    #                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE proName =VALUES(proName),proDesc=VALUES(proDesc);"""

                    sqlhelper.execute("""insert into multisource_data (proName,province_id,proType_id,cluType_id,proSeg,proAddr,proUnit_id,volLevel_id,proDesc,proNature,scheName,bussSub,proCate,
                                                                             proImpleBody,proImpleYear,startTime,endStart,totalInvest,annPlan,proCode)
                                               select                        proName,province_nameid,proType_nameid,cluType_nameid,proSeg,proAddr_nameid,proUnit_nameid,volLevel_nameid,proDesc,
                                                                             proNature,scheName,bussSub,proCate,proImpleBody,proImpleYear,startTime,endStart,totalInvest,annPlan,proCode
                                               from midresult where midresult.CCStatus=0 """)

                    # FillNormalPro.write_mysql('gw1', fill_com, sobject)
                except Exception as e:
                    print(e)

                # FillNormalPro.write_mysql('gw1', fill_com, sobject)

                # sqlhelper.execute("""insert into multisource_data (proName,province_id,proType_id,cluType_id,proSeg,proAddr_id,proUnit_id,volLevel_id,proDesc,proNature,scheName,bussSub,proCate,
                #                                                          proImpleBody,proImpleYear,startTime,endStart,totalInvest,annPlan,proCode)
                #                            select                        proName,province_nameid,proType_nameid,cluType_nameid,proSeg,proAddr_nameid,proUnit_nameid,volLevel_nameid,proDesc,
                #                                                          proNature,scheName,bussSub,proCate,proImpleBody,proImpleYear,startTime,endStart,totalInvest,annPlan,proCode
                #                            from midresult where midresult.CCStatus=0 """)

                # TODO: 填写 功能，变电站，线路，道路的中间表
                FillmidSheet.fillpro__facility()
                FillmidSheet.fillPro__circuit()
                FillmidSheet.fillPro__road()
                FillmidSheet.fillPro__substation()

                response = HttpResponse('''[{"STATE": 0,"MESSAGE":"请求成功"}]''')
                response["Access-Control-Allow-Origin"] = "*"
                response["Content-Type"] = "application/json;charset=UTF-8"
                print('最终录入成功!!!')
                return response
            else:
                response = HttpResponse('''[{"STATE": 2,"MESSAGE":"收到导入信号有误"}]''')
                response["Access-Control-Allow-Origin"] = "*"
                response["Content-Type"] = "application/json;charset=UTF-8"
                return response
    else:
        response = HttpResponse('''[{"STATE": 1,"MESSAGE":"服务器响应超时"}]''')
        response["Access-Control-Allow-Origin"] = "*"
        response["Content-Type"] = "application/json;charset=UTF-8"
        return response

if __name__=='__main__':
    mypth = os.path.abspath('.') + '/exportfile/NORMEXPORT/不规范内容'
    print(mypth)
    # import socket
    # def get_host_ip():
    #     """
    #     查询本机ip地址
    #     :return:
    #     """
    #     try:
    #         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #         s.connect(('8.8.8.8', 80))
    #         ip = s.getsockname()[0]
    #     finally:
    #         s.close()
    #
    #     return ip
    # print(get_host_ip())