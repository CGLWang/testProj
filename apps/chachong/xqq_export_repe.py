#auther:"l"
#date:2019/7/19
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymysql
import datetime
import xlrd
import xlwt
import os
from xlwt import Workbook
from xlutils.copy import copy
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



def readRepe_export():
    connect, cursor = connectSql()
    result_list = []
    try:
        sql = "select * from repe_export"
        cursor.execute(sql)
        result = cursor.fetchall()
        # print(result)
        for item in result:
            # print(item)
            result_list.append(list(item))
        # print(result_list)
    except Exception as e:
        connect.rollback()  # 事务回滚
        print('事务处理失败', e)
    else:
        connect.commit()  # 事务提交
        print('处理成功')
    # 关闭连接
    cursor.close()
    connect.close()
    return result_list

def initRepeTable(file_name):
    if os.path.isfile(file_name):
        print('%s is exit.' % file_name)
        return False
    else:
        workbook = xlwt.Workbook("UTF-8")
        sheet = workbook.add_sheet('sheet1', cell_overwrite_ok=True)
        workbook.save(file_name)

def title1Style():
    # 设置对齐
    al = xlwt.Alignment()  # 对齐方式
    al.horz = 0x02  # 设置水平居中
    al.vert = 0x01  # 设置垂直居中

    # 设置字体
    font = xlwt.Font()  # 为样式创建字体
    font.name = u'宋体'
    font.bold = 'bold'
    # font.color_index = 4
    font.height = 20 * 14

    style = xlwt.XFStyle()  # 样式对象
    style.alignment = al
    style.font = font
    return style

def title2Style():
    # 设置对齐
    al = xlwt.Alignment()  # 对齐方式
    al.horz = 0x02  # 设置水平居中
    al.vert = 0x01  # 设置垂直居中

    # 设置字体
    font = xlwt.Font()  # 为样式创建字体
    font.name = u'宋体'
    # font.bold = 'bold'
    # font.color_index = 4
    font.height = 20 * 11

    style = xlwt.XFStyle()  # 样式对象
    style.alignment = al
    style.font = font
    return style

def contentStyle():
    # 设置对齐
    al = xlwt.Alignment()  # 对齐方式
    al.horz = 0x02  # 设置水平居中
    al.vert = 0x01  # 设置垂直居中

    # 设置字体
    font = xlwt.Font()  # 为样式创建字体
    font.name = u'宋体'
    # font.bold = 'bold'
    # font.color_index = 4
    font.height = 20 * 11

    style = xlwt.XFStyle()  # 样式对象
    style.alignment = al
    style.font = font
    return style

def setWidth(worksheet,coln,width):
    row = worksheet.col(coln)
    row.width = 256 * width

def setHeight(worksheet,rown,height):
    tall_style = xlwt.easyxf('font:height {};'.format(str(height)))  # 36pt,类型小初的字号
    row = worksheet.row(rown)
    row.set_style(tall_style)

def exportRepeTable(file_name):
    initRepeTable(file_name)
    workbook = xlrd.open_workbook(file_name)  # 打开工作簿
    workbook = copy(workbook)  # 将xlrd对象拷贝转化为xlwt对象
    worksheet = workbook.get_sheet(0)  # 获取转化后工作簿中的第一个表格
    title1 = "重复项目汇总"
    worksheet.write_merge(0, 0, 0, 7, title1,title1Style())
    title2 = ["序号", "查询项目名", "查询项目类型", "查询项目年份", "库中项目名", "库中项目类型", "库中项目年份", "重复率"]
    for i in range(len(title2)):
        worksheet.write(1, i, title2[i], title2Style())
    # 设置列宽
    width_list = [8,50,20,15,50,20,20,10]
    for i in range(len(width_list)):
        setWidth(worksheet,i,width_list[i])
    # 设置行高
    setHeight(worksheet, 0, 360)
    setHeight(worksheet, 1, 270)

    result_list = readRepe_export()
    for i in range(len(result_list)):
        for j in range(len(result_list[i])):
            worksheet.write(i+2, j, result_list[i][j],contentStyle())

    for i in range(len(result_list)):
        for j in range(len(result_list[i])):
            worksheet.write(i+2, j, result_list[i][j],contentStyle())

    # print(result_list)
    merge_list = []
    num = 0
    temp = result_list[0][1]
    for item in result_list:
        if item[1] == temp:
            num += 1
        elif item[1] != temp:
            merge_list.append(num)
            temp = item[1]
            num = 1
        if item == result_list[-1]:
            merge_list.append(num)

    # print(merge_list)
    for i in range(len(merge_list)):
        if i == 0:
            if merge_list[0] == 1:
                worksheet.write(2,1,result_list[sum(merge_list[:i])][1],contentStyle())
                worksheet.write(2,2,result_list[sum(merge_list[:i])][2],contentStyle())
                worksheet.write(2,3,result_list[sum(merge_list[:i])][3],contentStyle())
            else:
                worksheet.write_merge(2,1+merge_list[0],1,1,result_list[sum(merge_list[:i])][1],contentStyle())
                worksheet.write_merge(2,1+merge_list[0],2,2,result_list[sum(merge_list[:i])][2],contentStyle())
                worksheet.write_merge(2,1+merge_list[0],3,3,result_list[sum(merge_list[:i])][3],contentStyle())
        else:
            if merge_list[i] == 1:
                worksheet.write(2+sum(merge_list[:i]),1,result_list[sum(merge_list[:i])][1],contentStyle())
                worksheet.write(2+sum(merge_list[:i]),2,result_list[sum(merge_list[:i])][2],contentStyle())
                worksheet.write(2+sum(merge_list[:i]),3,result_list[sum(merge_list[:i])][3],contentStyle())
            else:
                worksheet.write_merge(2+sum(merge_list[:i]),1+sum(merge_list[:i+1]),1,1,result_list[sum(merge_list[:i])][1],contentStyle())
                worksheet.write_merge(2+sum(merge_list[:i]),1+sum(merge_list[:i+1]),2,2,result_list[sum(merge_list[:i])][2],contentStyle())
                worksheet.write_merge(2+sum(merge_list[:i]),1+sum(merge_list[:i+1]),3,3,result_list[sum(merge_list[:i])][3],contentStyle())

    workbook.save(file_name)  # 保存工作簿
    return file_name


