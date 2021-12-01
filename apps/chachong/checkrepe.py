# coding=gbk
# coding:utf-8
# encoding:utf-8

import difflib
import jieba
import pymysql
import linecache
import re
import xlwt
from utils import sqlhelper
import os
from configuration import get_config_values
from utils import sqlhelper
import time
import random

PORT = int(get_config_values('mysql', 'port'))
HOST = get_config_values('mysql', 'host')
USER = get_config_values('mysql', 'user')
PASW = get_config_values('mysql', 'password')
DATB = get_config_values('mysql', 'database')


base_dir = os.path.split(os.path.realpath(__file__))[0]
DATAS_PATH = base_dir+r"\datas.txt"
CUTDATAS_PATH = base_dir+r"\cutdatas.txt"

# 从数据库中读取数据并传入到datas.txt中
# 将datas.txt文件中的内容分词后，放入cutdatas.txt中
def txtfun(path1, path2, path3, path4):
    # db = pymysql.connect("127.0.0.1", "root", "123456", "guowang") # 打开数据库连接
    """旧的连接方式"""
    # db = pymysql.connect(path1, path2, path3, path4)  # 打开数据库连接
    # cursor = db.cursor()
    # sql = "SELECT * FROM multisource_data"
    # cursor.execute(sql)  # 游标.执行
    # datas1 = cursor.fetchall()

    #TODO:20190726修改连接方式
    # 结果确认为[{'A':xxx,'B':,xxsss}]
    # sqls = ['''ALTER  TABLE  `multisource_data` DROP `id`;''', '''ALTER  TABLE  `multisource_data` ADD 'id' MEDIUMINT(6) PRIMARY KEY NOT NULL AUTO_INCREMENT FIRST;''']
    # sqlhelper.execute_many_sql(sqls)
    testsql ="""SELECT id,proName,proDesc,proCode,proType_id FROM multisource_data;"""
    datas1 = sqlhelper.get_list_dict(testsql)
    s = ""
    with open(DATAS_PATH, 'w', encoding='utf-8') as f:
        for row in datas1:
            # id = row[0]
            # proName = row[1]
            # proDesc = row[9]
            # proCode = row[20]
            id = row['id']
            proName = row['proName']
            proDesc = row['proDesc']
            proCode = row['proCode']
            proType = row['proType_id']

            #TODO:20190726修改对比内容，内容为空的项目需要特别处理进行查重
            if proDesc=='' or proDesc==None:
                proDesc= random.uniform(10, 20)
            str1 = str(proName)
            str11 = re.sub('[\r\n\t]', '', str1).replace(' ','')
            str2 = str(proDesc)
            str22 = re.sub('[\r\n\t]', '', str2).replace(' ','')
            s += "id:"+str(id)+"   proType:"+str(proType)+"\n"+"proName:"+str11+"\n"+"proDesc:"+str22+"\n"+"proCode:"+str(proCode)+"\n\n"
    with open(DATAS_PATH, 'w', encoding='utf-8') as f:
        f.write(s)
    # cursor.close()
    # db.close()

    path = DATAS_PATH  # 训练语料库
    cutpath = base_dir+r"\cutdatas.txt"  # 语料分词
    jieba.load_userdict(base_dir+r"\newDict.txt")
    with open(path, 'r', encoding='utf-8') as f1:
        f2 = open(cutpath, 'w', encoding='utf-8')
        for item in f1.readlines():
            string = item.strip('\n')
            #string1 = re.sub(r'[^\w\s]', '', string)
            s1 = ' '.join(jieba.cut(string))
            f2.write(s1 + "\n")
    f1.close()
    f2.close()


# 查重函数
def checkfun(listNP):
    weight_name, weight_desc = 0.2, 0.8
    # proName={}  # 记录查重结果，键值对，原句+重复率
    # proDesc={}
    proNP = {}
    # 1 找到对比库的历史数据
    checkpath = CUTDATAS_PATH   # 数据库中对比项目语料库
    with open(checkpath,"r",encoding="utf-8") as f:
        checklist = [line[:] for line in f.readlines()]
    proNamename = [name for name in checklist if "proName" in name]  # 遍历checklist，如果"proName"在sub中，返回sub.项目名称
    proDescname = [desc for desc in checklist if "proDesc" in desc]  # 项目简介
    proType = [ptype for ptype in checklist if "proType" in ptype ]  # 表中项目专项

    outreslut = ""
    list1 = []
    with open(DATAS_PATH, 'r', encoding='utf-8') as f3:
        for line in f3:
            list1.append(line)
    for i in range(len(proNamename)):
        # 得到表中的每一个项目的专项ID：
        sheettype = int(re.findall('\d+', proType[i])[1])
        #TODO:加入了一条语句判断是否为同一专项
        if sheettype==int(listNP[3]):
            line1 = ''.join(str(proNamename[i]).split(' ')[2:])
            line2 = ''.join(str(proDescname[i]).split(' ')[2:])
            sub1 = difflib.SequenceMatcher(None, listNP[0].split('\n')[0].replace('proName:',''),line1).ratio()
            sub2 = difflib.SequenceMatcher(None, listNP[1].split('\n')[0].replace('proDesc:', ''), line2).ratio()
            sub11 = sub1 * weight_name + sub2 * weight_desc
            sub12 = float('%.4f' % (sub11))
            proNP[proNamename[i]] = sub12
    sort1 = sorted(proNP.items(), key=lambda e: e[1], reverse=True)  # 排序
    for item in sort1[0:4]:
        if item[1] >= 0.6:
            item1 = item[0].replace(' ', '')
            for line in list1:
                if item1 in line:
                    l1 = list1.index(line)
            outreslut += list1[l1 - 1] + list1[l1] + list1[l1 + 1] + list1[l1 + 2] + "相似率为：" + str(item[1]) + "\n"
    return outreslut


def CHA():
    # 写分词文件
    txtfun(HOST, USER, PASW, DATB)  # 数据库：(IP地址，用户名，密码，数据库名称)
    myfile = open('./chachong/cutdatas.txt', 'r', encoding='utf-8')
    # print('MY',myfile.read())
    value =[]
    listNP=[]

    proname_prodesc = sqlhelper.get_list_dict('''select id,proName,proDesc,proType_id from repeatcheck_cache''')

    # listNP.append(proname_prodesc['proName'])
    # listNP.append(proname_prodesc['proDesc'])
    #print(proname_prodesc)

    for item in proname_prodesc:
        listNP.append([item['proName'],item['proDesc'],item['id'],item['proType_id']])
    # 库中取出一条：
    for np in listNP:
        # 计算重复率的函数
        result = checkfun(np).split('\n')
        #根据result是否为['']判断是否重复，不重复标为0，否则为1
        # if result[0] == '':
        #     sqlhelper.execute('''update repeatcheck_cache set proFilename=0 where id=%d''' % np[2])
        # else:
        #     sqlhelper.execute('''update repeatcheck_cache set proFilename=1 where id=%d''' % np[2])
        #print(result)

        for i in range(len(result)//5):
            #ans = [getID,int(result[i * 5 + 0][3:]),float(result[i * 5 + 4][5:])]
            # result[i * 5 + 0]为文档中 id和type的一行
            databaseid = int(re.findall('\d+', result[i * 5 + 0])[0])
            ans = [np[2],databaseid,float(result[i * 5 + 4][5:]),CC_highlight(np[1],np[2],databaseid)]
            value.append(ans)
    # print(value)
    return value

# TODO:20190909 重写查重功能函数
import time
import datetime
import time #获取当前时间, 其中中包含了year, month, hour, 需要import datetime
from chachong import wordPosition

def NewCHA():
    resvalue = []
    today = datetime.date.today()
    t_year = int(today.year)
    year_list = range(t_year-3,t_year+2)
    year_list = tuple(year_list)
    year_list = str(year_list)
    print(year_list)

    # 多条件查询可能相同内容
    check_command = 'SELECT a.proName proNameA,b.proName proNameB,a.proDesc proDescA,b.proDesc proDescB,a.id idA,b.id idB ' \
                    'FROM multisource_data a, repeatcheck_cache b ' \
                    'WHERE a.`proType_id`=b.`proType_repeid` AND a.`province_id`=b.`province_repeid` AND a.`volLevel_id`=b.`volLevel_repeid` AND a.`proImpleYear` in %s;' % (year_list)

    print(check_command)
    proname_prodesc = sqlhelper.get_list_dict(check_command)

    for item in proname_prodesc:
        NameRa = difflib.SequenceMatcher(None, item['proNameA'], item['proNameB']).ratio()
        DescRa = difflib.SequenceMatcher(None, item['proDescA'], item['proDescB']).ratio()
        # ticks3 = time.time()
        # print("3当前时间戳为:", ticks3 - ticks2)
        # if ticks3 - ticks2> maxtime:
        #     maxtime= ticks3 - ticks2
        #     myid = item['proNameA']
        AllRa = NameRa * 0.2 + DescRa * 0.8
        if AllRa>=0.6:
            # 高亮字符串准备
            # light_list = NewLight(item['proDescA'],item['proDescB'])
            light_list = NewLight1119(item['proDescA'], item['proDescB'])       #1119修改版本测试
            #获取重复文本的相对位置
            #positionRes用于给前端提供相对位置，已测试通过
            print(light_list[0])
            print(light_list[1])
            print(light_list[2])
            positionRes = wordPosition.Numlen(light_list,item['proDescA'])
            ans = [item['idB'],item['idA'],AllRa,str(light_list)]
            resvalue.append(ans)
    return resvalue




# TODO:20211119 查重高亮部分重写,加上重复句子 lhx syl
def CCsentence(src_str, aim_str):               #先找出重复语句
    seperators = ',|\.|\?|，|。|？|！'
    T1 = re.split(seperators, src_str)
    T2 = re.split(seperators, aim_str)
    list = []
    for item2 in T1:            # 输出重复的语句
        if item2 in T2:
            list.append(item2)
    return list


#lhx syl cos重复修改版
from chachong import cosrepeat

def NewLight1119(src_str, aim_str):
    CCsentenceList=cosrepeat.mainfun(src_str, aim_str)
    #CCsentenceList =  CCsentence(src_str, aim_str)
    #RepeListnew = CCsentenceList + repelist


    return CCsentenceList


#TODO:20190909 查重高亮部分重写
def NewLight(src_str,aim_str):
    jieba.load_userdict(base_dir + r"\CCDict.txt")
    source_str= re.sub(r'[\r\n\t\d]', '', src_str)
    source_str = ' '.join(jieba.cut(source_str))
    source_string =re.sub(r'[^\w\s]','',source_str)
    aim_string= re.sub(r'[\r\n\t\d]', '', aim_str)
    aim_string = ' '.join(jieba.cut(aim_string))
    aim_string =re.sub(r'[^\w\s]','',aim_string)
    aim_string = re.sub(r'[^\w\s]', '', aim_string)
    aim_string = re.sub(r'[\r\n\t]', '', aim_string)
    aim_string = re.sub('[A-Za-z]', '', aim_string)
    source_string = re.sub(r'[\r\n\t]', '', source_string)
    repeset = set(source_string.split(' '))&set(aim_string.split(' '))
    repelist = list(repeset)
    #只保留词
    repelist=[word for word in repelist if len(word)>=2]

    return str(repelist)




def CC_highlight(source_str,source_id,aim_id):
    mystoplist= ['对','的','等','不','和','共','号','串','了','已','及','并','也','其','从','让','将','为','常','往','或','后','','中','个']
    # TODO:20190726找到 ID 在文件中的位置
    first_id = linecache.getline('./chachong/cutdatas.txt',1)
    first_id = int(re.findall('\d+',first_id)[0])
    # 被查项目，缓存表中的项目(需要分词)
    jieba.load_userdict(base_dir + r"\newDict.txt")
    source_str= re.sub(r'[\r\n\t\d]', '', source_str)
    source_str = ' '.join(jieba.cut(source_str))
    # 对比项目，总库中的项目
    #TODO：防止序号不连续
    sss= 'id : %s'%aim_id
    file = open("./chachong/cutdatas.txt", "r", encoding="utf-8").readlines()
    for num, value in list(enumerate(file)):
        if sss in value:
            aim_line=num+3
            break
    # 序号连续的情况下可能
    # aim_line = (aim_id-first_id+1) * 5 - 2
    # print('aimL:',aim_line)
    source_string = source_str
    aim_string = linecache.getline('./chachong/cutdatas.txt', aim_line)[10:]
    # 正则表达，只保留汉字
    '''空白不能去掉'''
    # source_string = ''.join(list(filter(str.isalnum, source_string)))
    # aim_string = ''.join(list(filter(str.isalnum, aim_string)))
    source_string =re.sub(r'[^\w\s]','',source_string)
    aim_string = re.sub(r'[^\w\s]', '', aim_string)
    aim_string = re.sub(r'[\r\n\t]', '', aim_string)
    aim_string = re.sub('[A-Za-z]', '', aim_string)
    source_string = re.sub(r'[\r\n\t]', '', source_string)
    # print('aimS:',aim_string)
    # print('sorS:',source_string)
    repeset = set(source_string.split(' '))&set(aim_string.split(' '))
    repelist = list(repeset)
    # 删除单个字的情况
    # for word in repelist:
    #     if len(word)<=1:
    #         repelist.remove(word)
    #只保留词
    repelist=[word for word in repelist if len(word)>=2]
    # repelist.remove('')
    # for stopword in mystoplist:
    #     if stopword in repelist:
    #         repelist.remove(stopword)
    # print(str(repelist))

    # print('[表ID,库ID]',source_id,aim_id,'\n','库ID行',aim_line,'\n','重复列表',repelist)
    return str(repelist)

'''写待展示的明细表'''
def repeat_detail(pro_id):
    # for item in id_list:
    #     sqlhelper.execute('''update repeatcheck_cache set proFilename=0 where id=%d''' % item['proID'])
    sqlhelper.execute('''truncate table repe_pro''')
    sql = '''INSERT INTO repe_pro(proName,proDesc,proCode,proImpleYear,repetion,repe_word) 
             SELECT md.proName,md.proDesc,md.proCode,md.proImpleYear,pr.repetion,pr.repe_word 
             FROM pro__repe AS pr INNER JOIN multisource_data AS md ON pr.repe_id = md.id 
             WHERE pr.pro_repe_id=%d    
            ''' % (pro_id)
    sqlhelper.execute(sql)


def export_excel():
    #导出重复项目
    repeat_data = sqlhelper.get_list('''select proId,proName from repe_all''')
    cur_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    file_name = cur_time + '.xls'
    wbk = xlwt.Workbook(encoding='utf-8')  # 实例化一个Excel
    table = wbk.add_sheet('sheet1',cell_overwrite_ok=True)
    cols_name = ['proId', 'proName']
    rows = len(repeat_data)
    cols = len(repeat_data[0])
    # 写入表头
    for col_name in range(len(cols_name)):
        table.write(0, col_name, cols_name[col_name])

    for row in range(1, rows + 1):
        for col in range(cols):
            table.write(row, col, repeat_data[row-1][col])
    wbk.save(r'C:/Users/ldz/Desktop/重复项目' + file_name)
    return file_name



if __name__ == '__main__':
    # print(os.getcwd())
    # list=[]
    # with open("datas.txt",'r',encoding='utf-8') as f222:
    #     for line in f222:
    #         if 'proDesc' in line:
    #             l222 = line
    #             try:
    #                 checkfun(l222)
    #             except Exception as e:
    #                 list.append(line + '\n')
    #                 # print(e)
    #                 pass
    #             continue
    # print(len(list))
    # print(list)
    # l = 'proDesc:1.设计工作    本期项目，将延续物资集约化管理信息系统建设要求，进行需求分析、功能设计、概要设计、详细设计、数据库设计工作。2.开发工作    ERP物资管理模块，完善：完成计划管理（包含计划属性管理、物资计划提报等2个子模块）、仓储配送管理（包含库存管理和仓储管理、供应商寄售管理、储备定额管理等3个子模块）的功能的完善开发工作。    电子商务平台，新增：完成合同管理（包含合同签订逆向回退流程子模块）、供应商管理（包含分级分类管理子模块）、专家管理（包含日志管理子模块）、电子招投标投标检测认证工作（包含招标人注册、招标代理机构注册等11个子模块）等新增功能的开发工作；完善：完成采购标准管理（包含技术规范书编制、主数据维护等2个子模块）、采购管理（包含采购项目准备、发标管理、投标管理等8个子模块）、合同管理（包含合同签订、合同变更、合同履约、协议库存匹配等4个子模块）、供应商管理（包含资质业绩管理、不良行为管理、绩效管理等3个子模块）、质量监督管理（包含问题管理、供应商协同等2个子模块）、专家管理（包含专家短信管理、查询、抽取等5个子模块）、投诉管理（包含投诉录入、投诉流转等5个子模块）、技术功能优化（包含定时器改造、文件存储路径改造等4个子模块）等功能的完善开发工作。    物资辅助决策管理，完善：完成供应链整体业务统计分析、计划业务统计分析、合同业务统计分析、采购物流成本统计分析、仓储业务统计分析、专家业务统计分析、省公司用户统计模块及分权功能调整等功能的完善开发工作。3.实施工作    ERP物资管理模块，以两级部署方式，在公司总部，26个省（自治区、直辖市）电力公司（除国网西藏电力），11个直属单位（国网国际公司、鲁能集团、国网新源公司、国网通航公司、国网物资公司、中国电科院、国网经研院、国网能源院、英大传媒集团、国网中兴公司、国网技术学院）完成本项目的实施工作。    电子商务平台，以一级部署方式，在公司总部，26个省（自治区、直辖市）电力公司（除国网西藏电力），25个直属单位（国网国际公司、鲁能集团、中电装备公司、国网新源公司、国网通航公司、国网物资公司、国网运行公司、国网直流公司、国网交流公司、国网信通公司、中国电科院、国网经研院、国网能源院、国网智研院、国网英大集团公司、中国电财、英大财险、英大长安、英大信托、英大证券、英大汇通、英大传媒集团、国网中兴公司、国网管理学院、国网技术学院）完成本项目的实施工作。    物资辅助决策系统，以两级部署方式，在公司总部完成本项目的实施工作。4.集成工作    完成与基建、经法、财务、ERP、主数据管理平台、运检、IMS、国家公共服务平台等系统的本端集成开发实施工作；完成物资内部系统采购管理、合同管理、供应商管理、质量监督管理各模块间业务集成与数据共享。'
    # l = "proDesc:发线、一库三中心成上述各模块的实施工作，满与产业管控系统、基建信息管理系统、信息通信业务管理系统、后勤管理系统、营销项目管理等系统的本端集成开发实施工作。"
    # l='proDesc:华中地区新能源的现状与发展趋势，西北、西南新能源的发展状况、消纳形势，有关新能源消纳的国家政策。绿色电力交易的有关办法，市场发展趋势。'
    #nl = 'proName:国网华中分部本部2018年新能源技术培训'
    # nl = ['国网湖南输电检修公司500kV民鹤Ⅰ线复合绝缘子治理',
    #       '1、民鹤Ⅰ线全长82.6km,共231基,2007年投运。复合绝缘子运行时间超过8年,经绝缘子抽样检测,抽检绝缘子憎水性为HC5-6,表面憎水性失效,不满足运行要求。要求对不合格批次绝缘子进行更换。更换合成绝缘子民鹤Ⅰ线11基总计19串38支合成绝缘子。']
    #
    # # chachong(nl)
    # result = checkfun(nl).split('\n')
    # for i in range(len(result) // 5):
    #     ans = [1, int(result[i * 5 + 0][3:]),result[i * 5 + 2][8:],float(result[i * 5 + 4][5:])]
    #     print(ans)


    # TODO：测试，查重多选择输出格式确认：
    # get_list_dict结果为[{'A':xxx,'B':,xxsss}]
    # get_list结果为((xxx,xxx,xxx,xxx),(xxx,xxx,xxx,xxx))
    testsql ="""SELECT id,proName,proDesc,proCode FROM multisource_data;"""
    mystr = sqlhelper.get_list_dict(testsql)
    mystr = sqlhelper.get_list(testsql)
    print(mystr)
    # TODO：测试，项目在文档中的位置
    # first_id = linecache.getline('./chachong/cutdatas.txt',1)
    # # source_string = ''.join(list(filter(str.isalnum, source_string)))
    # first_id =int(re.findall('\d+',first_id)[0])
    #
    # print(first_id)
    # print(first_id)
    # txtfun(HOST, USER, PASW, DATB)
    # CHA()
    # pass
    # export_excel()
    # TODO：测试重复词表


    # aim_string = '500kV 兴咸 Ⅲ 回线 投运 时间 为 2008 年 12 月 ， 起自 兴隆 变 ， 止于 咸宁 变 ， 线路 总长度 为 176.602 km ， 杆塔 共 417 基 。 该 线路 2014 年 状态 评价 为 注意 状态 。 # 288 - # 289 跨越 新建 武深 高速公路 , # 288 塔 更换 双 悬垂 绝缘子 串 。'
    # source_string='''500kV孝浉Ⅱ回线投运时间为2007年11月，起自孝感变，止于浉河变，线路总长度为87.521km，杆塔共199基。该线路2014年状态评价为正常状态。 存在问题：根据运检二（2015）45号文，“国网运检部关于开展复合绝缘子防掉串隐患治理工作的通知”对不满足要求的复合绝缘子进行更换。 主要工作内容：1、将17#、51#、52#、60#、61#、95#、96#、115#、116#、147#共计10基直线塔的两边相单I串改为双I串； 2、原铁塔边相I串挂点原设计均为单挂点，本次需将挂线角钢进行更换，改造为独立双挂点。'''
    # jieba.load_userdict(base_dir + r"\newDict.txt")
    # source_str = re.sub(r'[\r\n\t\d]', '', source_string)
    # source_str = ' '.join(jieba.cut(source_str))
    # source_str = re.sub(r'[^\w\s]', '', source_str)
    # aim_str = re.sub(r'[^\w\s]', '', aim_string)
    # aim_str = re.sub(r'[\r\n\t]', '', aim_str)
    # aim_str = re.sub('[A-Za-z]','',aim_str)
    # repeset = set(source_str.split(' ')) & set(aim_str.split(' '))
    # print(aim_str)
    # print(source_str)
    # print(set(source_str.split(' ')))
    # print(set(aim_str.split(' ')))
    # repelist = list(repeset)
    # print(repelist)
    # ans = [word for word in repelist if len(word)>=2]
    # for word in repelist:
    #     print(len(word))
    #     if len(word)<=1 :
    #         repelist.remove(word)
    # # print(repelist)
    # print(ans)
    #TODO:索引测试
    # file = open("cutdatas.txt", "r",encoding="utf-8").readlines()
    # # print(list(enumerate(file)))
    #
    # for num, value in list(enumerate(file)):
    #     # print(num)
    #     if 'id : 80' in value:
    #         print(num)

    #TODO：分词测试
    #
    # source_str = "500kV凤凰山变电站1982年正式建成投运。2#主变压器及其套管,厂家为日本日立公司，生产日期1980年，投运日期1982年，运行时间长达33年。存在的问题：2016年4月检修中发现B相变压器出现低压套管末屏绝缘电阻不合格、中性点套管存在外壳破损、中压套管介质损耗超标等缺陷，其安全可靠性指标难以达到要求，影响安全运行，且高压套管属于同厂家同批次的产品，产品性能影响安全稳定运行，需对套管进行大修。主要工作内容：拆除500kV凤凰山变电站2#主变B相套管1组（5只）进行返厂大修并复装。"
    # jieba.load_userdict(base_dir + r"\newDict.txt")
    # source_str= re.sub(r'[\r\n\t\d]', '', source_str)
    # source_str = ' '.join(jieba.cut(source_str))
    # print(source_str)

