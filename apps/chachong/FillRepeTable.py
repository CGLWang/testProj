#auther:"l"
#date:2019/5/10
import xlrd
import pymysql
from django.http import HttpResponse
from configuration import get_config_values
from utils import sqlhelper
from guifan import FillNormalPro,Inspection
PORT = int(get_config_values('mysql', 'port'))
HOST = get_config_values('mysql', 'host')
USER = get_config_values('mysql', 'user')
PASW = get_config_values('mysql', 'password')
DATB = get_config_values('mysql', 'database')


repe_keywords = ['项目名称', '内容']

#读取excel文件
def open_excel(file):
    try:
        data = xlrd.open_workbook(file)
        return data
    except Exception as e:
        print(e)
        print('查重文件不存在')
        response = HttpResponse('''[{"STATE": 3}]''')
        response["Access-Control-Allow-Origin"] = "*"
        response["Content-Type"] = "application/json;charset=UTF-8"
        return response

def write_data(file):
    data = open_excel(file)

    table = data.sheets()[0]
    rows = table.nrows
    cols = table.ncols

    # 获取序号为1的行
    for i in range(rows):
#        if (type(table.cell_value(i, 0)) == float) and (table.cell_value(i, 0) == 1.0):
        if table.cell_value(i,0) == 1 or table.cell_value(i,0) == '1' or table.cell_value(i,0) == 1.0:
            first_row = i
            break

    # 找出表头所在列号
    table_head_row = first_row
    while table_head_row != 1:
        table_head_row -= 1

    table_heads = table.row_values(table_head_row)
    #获取项目类别的ID
    pro_type_id = FillNormalPro.find_doc_type_index(file)
    #获取项目类别字符串
    pro_names = FillNormalPro.get_porject_type()
    for a, b in pro_names:
        if b in file:
            pro_type = b
            break
    #获取项目年份
    pro_year = int(file.split('\\')[-1][:4])
    # print(table_heads)
    table_contends = []
    for item in repe_keywords:
        for i in range(len(table_heads)):
            if item in table_heads[i]:
                table_contends.append(table.col_values(i,start_rowx=first_row))
    #todo:20190727加入年份和项目专项：
    total_row_count = len(table.col_values(i,start_rowx=first_row))
    #加入项目类别
    proType =[pro_type_id] * (total_row_count)
    table_contends.append(proType)
    #加入项目年份
    proyear =[pro_year] * (total_row_count)
    table_contends.append(proyear)
    table_data = list(zip(*table_contends))
    #print(table_data)

    sqlhelper.insert_many('''insert into repeatcheck_cache(proName,proDesc,proType_id,proImpleYear) values (%s,%s,%s,%s)''', table_data)
    #return table_data


def write_sql2repeatcheck_cache(file_name):

    excel_data = FillNormalPro.get_excel_keyword_data(file_name)
    #print('proImpleYear',excel_data['proImpleYear'])

    data = {}
    province_list = []
    data['proName'] = excel_data['proName']
    for item in excel_data['proName']:
        a_province = Inspection.findProvince(item)
        province_list.append(a_province)
    data['province_nameid']  = province_list
    #省份ID列表
    #print('province_list',province_list)
    # data['province_nameid'] = excel_data['Province']
    data['proType_nameid'] = excel_data['proType']
    data['proSeg'] = excel_data['proSeg']
    data['proAddr_nameid'] = excel_data['proAddr']
    data['proUnit_nameid'] = excel_data['proUnit']
    data['volLevel_nameid'] = excel_data['volLevel']
    data['proDesc'] = excel_data['proDesc']
    data['proImpleYear'] = excel_data['proImpleYear']
    data['proCode'] = excel_data['proCode']
    data = list(zip(*data.values()))

    # 一次写查重缓存表
    command = """
            insert into repeatcheck_cache(proName,province_repeid,proType_repeid,proSeg,proAddr,proUnit_repeid,volLevel_repeid,proDesc,
                  proImpleYear,proCode) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

    FillNormalPro.write_mysql('gwpro',command,data)
    #TODO: 这里要更新填写省份





if __name__ == '__main__':
    file_path = r'C:\Users\ldz\Desktop\测试文件\2017年教育培训项目储备表.xls'
    write_data(file_path)