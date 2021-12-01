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

# �����ݿ��ж�ȡ���ݲ����뵽datas.txt��
# ��datas.txt�ļ��е����ݷִʺ󣬷���cutdatas.txt��
def txtfun(path1, path2, path3, path4):
    # db = pymysql.connect("127.0.0.1", "root", "123456", "guowang") # �����ݿ�����
    """�ɵ����ӷ�ʽ"""
    # db = pymysql.connect(path1, path2, path3, path4)  # �����ݿ�����
    # cursor = db.cursor()
    # sql = "SELECT * FROM multisource_data"
    # cursor.execute(sql)  # �α�.ִ��
    # datas1 = cursor.fetchall()

    #TODO:20190726�޸����ӷ�ʽ
    # ���ȷ��Ϊ[{'A':xxx,'B':,xxsss}]
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

            #TODO:20190726�޸ĶԱ����ݣ�����Ϊ�յ���Ŀ��Ҫ�ر�����в���
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

    path = DATAS_PATH  # ѵ�����Ͽ�
    cutpath = base_dir+r"\cutdatas.txt"  # ���Ϸִ�
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


# ���غ���
def checkfun(listNP):
    weight_name, weight_desc = 0.2, 0.8
    # proName={}  # ��¼���ؽ������ֵ�ԣ�ԭ��+�ظ���
    # proDesc={}
    proNP = {}
    # 1 �ҵ��Աȿ����ʷ����
    checkpath = CUTDATAS_PATH   # ���ݿ��жԱ���Ŀ���Ͽ�
    with open(checkpath,"r",encoding="utf-8") as f:
        checklist = [line[:] for line in f.readlines()]
    proNamename = [name for name in checklist if "proName" in name]  # ����checklist�����"proName"��sub�У�����sub.��Ŀ����
    proDescname = [desc for desc in checklist if "proDesc" in desc]  # ��Ŀ���
    proType = [ptype for ptype in checklist if "proType" in ptype ]  # ������Ŀר��

    outreslut = ""
    list1 = []
    with open(DATAS_PATH, 'r', encoding='utf-8') as f3:
        for line in f3:
            list1.append(line)
    for i in range(len(proNamename)):
        # �õ����е�ÿһ����Ŀ��ר��ID��
        sheettype = int(re.findall('\d+', proType[i])[1])
        #TODO:������һ������ж��Ƿ�Ϊͬһר��
        if sheettype==int(listNP[3]):
            line1 = ''.join(str(proNamename[i]).split(' ')[2:])
            line2 = ''.join(str(proDescname[i]).split(' ')[2:])
            sub1 = difflib.SequenceMatcher(None, listNP[0].split('\n')[0].replace('proName:',''),line1).ratio()
            sub2 = difflib.SequenceMatcher(None, listNP[1].split('\n')[0].replace('proDesc:', ''), line2).ratio()
            sub11 = sub1 * weight_name + sub2 * weight_desc
            sub12 = float('%.4f' % (sub11))
            proNP[proNamename[i]] = sub12
    sort1 = sorted(proNP.items(), key=lambda e: e[1], reverse=True)  # ����
    for item in sort1[0:4]:
        if item[1] >= 0.6:
            item1 = item[0].replace(' ', '')
            for line in list1:
                if item1 in line:
                    l1 = list1.index(line)
            outreslut += list1[l1 - 1] + list1[l1] + list1[l1 + 1] + list1[l1 + 2] + "������Ϊ��" + str(item[1]) + "\n"
    return outreslut


def CHA():
    # д�ִ��ļ�
    txtfun(HOST, USER, PASW, DATB)  # ���ݿ⣺(IP��ַ���û��������룬���ݿ�����)
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
    # ����ȡ��һ����
    for np in listNP:
        # �����ظ��ʵĺ���
        result = checkfun(np).split('\n')
        #����result�Ƿ�Ϊ['']�ж��Ƿ��ظ������ظ���Ϊ0������Ϊ1
        # if result[0] == '':
        #     sqlhelper.execute('''update repeatcheck_cache set proFilename=0 where id=%d''' % np[2])
        # else:
        #     sqlhelper.execute('''update repeatcheck_cache set proFilename=1 where id=%d''' % np[2])
        #print(result)

        for i in range(len(result)//5):
            #ans = [getID,int(result[i * 5 + 0][3:]),float(result[i * 5 + 4][5:])]
            # result[i * 5 + 0]Ϊ�ĵ��� id��type��һ��
            databaseid = int(re.findall('\d+', result[i * 5 + 0])[0])
            ans = [np[2],databaseid,float(result[i * 5 + 4][5:]),CC_highlight(np[1],np[2],databaseid)]
            value.append(ans)
    # print(value)
    return value

# TODO:20190909 ��д���ع��ܺ���
import time
import datetime
import time #��ȡ��ǰʱ��, �����а�����year, month, hour, ��Ҫimport datetime
from chachong import wordPosition

def NewCHA():
    resvalue = []
    today = datetime.date.today()
    t_year = int(today.year)
    year_list = range(t_year-3,t_year+2)
    year_list = tuple(year_list)
    year_list = str(year_list)
    print(year_list)

    # ��������ѯ������ͬ����
    check_command = 'SELECT a.proName proNameA,b.proName proNameB,a.proDesc proDescA,b.proDesc proDescB,a.id idA,b.id idB ' \
                    'FROM multisource_data a, repeatcheck_cache b ' \
                    'WHERE a.`proType_id`=b.`proType_repeid` AND a.`province_id`=b.`province_repeid` AND a.`volLevel_id`=b.`volLevel_repeid` AND a.`proImpleYear` in %s;' % (year_list)

    print(check_command)
    proname_prodesc = sqlhelper.get_list_dict(check_command)

    for item in proname_prodesc:
        NameRa = difflib.SequenceMatcher(None, item['proNameA'], item['proNameB']).ratio()
        DescRa = difflib.SequenceMatcher(None, item['proDescA'], item['proDescB']).ratio()
        # ticks3 = time.time()
        # print("3��ǰʱ���Ϊ:", ticks3 - ticks2)
        # if ticks3 - ticks2> maxtime:
        #     maxtime= ticks3 - ticks2
        #     myid = item['proNameA']
        AllRa = NameRa * 0.2 + DescRa * 0.8
        if AllRa>=0.6:
            # �����ַ���׼��
            # light_list = NewLight(item['proDescA'],item['proDescB'])
            light_list = NewLight1119(item['proDescA'], item['proDescB'])       #1119�޸İ汾����
            #��ȡ�ظ��ı������λ��
            #positionRes���ڸ�ǰ���ṩ���λ�ã��Ѳ���ͨ��
            print(light_list[0])
            print(light_list[1])
            print(light_list[2])
            positionRes = wordPosition.Numlen(light_list,item['proDescA'])
            ans = [item['idB'],item['idA'],AllRa,str(light_list)]
            resvalue.append(ans)
    return resvalue




# TODO:20211119 ���ظ���������д,�����ظ����� lhx syl
def CCsentence(src_str, aim_str):               #���ҳ��ظ����
    seperators = ',|\.|\?|��|��|��|��'
    T1 = re.split(seperators, src_str)
    T2 = re.split(seperators, aim_str)
    list = []
    for item2 in T1:            # ����ظ������
        if item2 in T2:
            list.append(item2)
    return list


#lhx syl cos�ظ��޸İ�
from chachong import cosrepeat

def NewLight1119(src_str, aim_str):
    CCsentenceList=cosrepeat.mainfun(src_str, aim_str)
    #CCsentenceList =  CCsentence(src_str, aim_str)
    #RepeListnew = CCsentenceList + repelist


    return CCsentenceList


#TODO:20190909 ���ظ���������д
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
    #ֻ������
    repelist=[word for word in repelist if len(word)>=2]

    return str(repelist)




def CC_highlight(source_str,source_id,aim_id):
    mystoplist= ['��','��','��','��','��','��','��','��','��','��','��','��','Ҳ','��','��','��','��','Ϊ','��','��','��','��','','��','��']
    # TODO:20190726�ҵ� ID ���ļ��е�λ��
    first_id = linecache.getline('./chachong/cutdatas.txt',1)
    first_id = int(re.findall('\d+',first_id)[0])
    # ������Ŀ��������е���Ŀ(��Ҫ�ִ�)
    jieba.load_userdict(base_dir + r"\newDict.txt")
    source_str= re.sub(r'[\r\n\t\d]', '', source_str)
    source_str = ' '.join(jieba.cut(source_str))
    # �Ա���Ŀ���ܿ��е���Ŀ
    #TODO����ֹ��Ų�����
    sss= 'id : %s'%aim_id
    file = open("./chachong/cutdatas.txt", "r", encoding="utf-8").readlines()
    for num, value in list(enumerate(file)):
        if sss in value:
            aim_line=num+3
            break
    # �������������¿���
    # aim_line = (aim_id-first_id+1) * 5 - 2
    # print('aimL:',aim_line)
    source_string = source_str
    aim_string = linecache.getline('./chachong/cutdatas.txt', aim_line)[10:]
    # �����ֻ��������
    '''�հײ���ȥ��'''
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
    # ɾ�������ֵ����
    # for word in repelist:
    #     if len(word)<=1:
    #         repelist.remove(word)
    #ֻ������
    repelist=[word for word in repelist if len(word)>=2]
    # repelist.remove('')
    # for stopword in mystoplist:
    #     if stopword in repelist:
    #         repelist.remove(stopword)
    # print(str(repelist))

    # print('[��ID,��ID]',source_id,aim_id,'\n','��ID��',aim_line,'\n','�ظ��б�',repelist)
    return str(repelist)

'''д��չʾ����ϸ��'''
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
    #�����ظ���Ŀ
    repeat_data = sqlhelper.get_list('''select proId,proName from repe_all''')
    cur_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    file_name = cur_time + '.xls'
    wbk = xlwt.Workbook(encoding='utf-8')  # ʵ����һ��Excel
    table = wbk.add_sheet('sheet1',cell_overwrite_ok=True)
    cols_name = ['proId', 'proName']
    rows = len(repeat_data)
    cols = len(repeat_data[0])
    # д���ͷ
    for col_name in range(len(cols_name)):
        table.write(0, col_name, cols_name[col_name])

    for row in range(1, rows + 1):
        for col in range(cols):
            table.write(row, col, repeat_data[row-1][col])
    wbk.save(r'C:/Users/ldz/Desktop/�ظ���Ŀ' + file_name)
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
    # l = 'proDesc:1.��ƹ���    ������Ŀ�����������ʼ�Լ��������Ϣϵͳ����Ҫ�󣬽������������������ơ���Ҫ��ơ���ϸ��ơ����ݿ���ƹ�����2.��������    ERP���ʹ���ģ�飬���ƣ���ɼƻ����������ƻ����Թ������ʼƻ��ᱨ��2����ģ�飩���ִ����͹�������������Ͳִ�������Ӧ�̼��۹���������������3����ģ�飩�Ĺ��ܵ����ƿ���������    ��������ƽ̨����������ɺ�ͬ����������ͬǩ���������������ģ�飩����Ӧ�̹��������ּ����������ģ�飩��ר�ҹ���������־������ģ�飩��������Ͷ��Ͷ������֤�����������б���ע�ᡢ�б�������ע���11����ģ�飩���������ܵĿ������������ƣ���ɲɹ���׼�������������淶����ơ�������ά����2����ģ�飩���ɹ����������ɹ���Ŀ׼�����������Ͷ������8����ģ�飩����ͬ����������ͬǩ������ͬ�������ͬ��Լ��Э����ƥ���4����ģ�飩����Ӧ�̹�����������ҵ������������Ϊ������Ч�����3����ģ�飩�������ල�����������������Ӧ��Эͬ��2����ģ�飩��ר�ҹ�������ר�Ҷ��Ź�����ѯ����ȡ��5����ģ�飩��Ͷ�߹�������Ͷ��¼�롢Ͷ����ת��5����ģ�飩�����������Ż���������ʱ�����졢�ļ��洢·�������4����ģ�飩�ȹ��ܵ����ƿ���������    ���ʸ������߹������ƣ���ɹ�Ӧ������ҵ��ͳ�Ʒ������ƻ�ҵ��ͳ�Ʒ�������ͬҵ��ͳ�Ʒ������ɹ������ɱ�ͳ�Ʒ������ִ�ҵ��ͳ�Ʒ�����ר��ҵ��ͳ�Ʒ�����ʡ��˾�û�ͳ��ģ�鼰��Ȩ���ܵ����ȹ��ܵ����ƿ���������3.ʵʩ����    ERP���ʹ���ģ�飬����������ʽ���ڹ�˾�ܲ���26��ʡ����������ֱϽ�У�������˾�����������ص�������11��ֱ����λ���������ʹ�˾��³�ܼ��š�������Դ��˾������ͨ����˾���������ʹ�˾���й����Ժ����������Ժ��������ԴԺ��Ӣ��ý���š��������˹�˾����������ѧԺ����ɱ���Ŀ��ʵʩ������    ��������ƽ̨����һ������ʽ���ڹ�˾�ܲ���26��ʡ����������ֱϽ�У�������˾�����������ص�������25��ֱ����λ���������ʹ�˾��³�ܼ��š��е�װ����˾��������Դ��˾������ͨ����˾���������ʹ�˾���������й�˾������ֱ����˾������������˾��������ͨ��˾���й����Ժ����������Ժ��������ԴԺ����������Ժ������Ӣ���Ź�˾���й���ơ�Ӣ����ա�Ӣ�󳤰���Ӣ�����С�Ӣ��֤ȯ��Ӣ���ͨ��Ӣ��ý���š��������˹�˾����������ѧԺ����������ѧԺ����ɱ���Ŀ��ʵʩ������    ���ʸ�������ϵͳ������������ʽ���ڹ�˾�ܲ���ɱ���Ŀ��ʵʩ������4.���ɹ���    ��������������������ERP�������ݹ���ƽ̨���˼졢IMS�����ҹ�������ƽ̨��ϵͳ�ı��˼��ɿ���ʵʩ��������������ڲ�ϵͳ�ɹ�������ͬ������Ӧ�̹��������ල�����ģ���ҵ�񼯳������ݹ���'
    # l = "proDesc:���ߡ�һ�������ĳ�������ģ���ʵʩ�����������ҵ�ܿ�ϵͳ��������Ϣ����ϵͳ����Ϣͨ��ҵ�����ϵͳ�����ڹ���ϵͳ��Ӫ����Ŀ�����ϵͳ�ı��˼��ɿ���ʵʩ������"
    # l='proDesc:���е�������Դ����״�뷢չ���ƣ���������������Դ�ķ�չ״�����������ƣ��й�����Դ���ɵĹ������ߡ���ɫ�������׵��йذ취���г���չ���ơ�'
    #nl = 'proName:�������зֲ�����2018������Դ������ѵ'
    # nl = ['�������������޹�˾500kV��ע��߸��Ͼ�Ե������',
    #       '1����ע���ȫ��82.6km,��231��,2007��Ͷ�ˡ����Ͼ�Ե������ʱ�䳬��8��,����Ե�ӳ������,����Ե����ˮ��ΪHC5-6,������ˮ��ʧЧ,����������Ҫ��Ҫ��Բ��ϸ����ξ�Ե�ӽ��и����������ϳɾ�Ե����ע���11���ܼ�19��38֧�ϳɾ�Ե�ӡ�']
    #
    # # chachong(nl)
    # result = checkfun(nl).split('\n')
    # for i in range(len(result) // 5):
    #     ans = [1, int(result[i * 5 + 0][3:]),result[i * 5 + 2][8:],float(result[i * 5 + 4][5:])]
    #     print(ans)


    # TODO�����ԣ����ض�ѡ�������ʽȷ�ϣ�
    # get_list_dict���Ϊ[{'A':xxx,'B':,xxsss}]
    # get_list���Ϊ((xxx,xxx,xxx,xxx),(xxx,xxx,xxx,xxx))
    testsql ="""SELECT id,proName,proDesc,proCode FROM multisource_data;"""
    mystr = sqlhelper.get_list_dict(testsql)
    mystr = sqlhelper.get_list(testsql)
    print(mystr)
    # TODO�����ԣ���Ŀ���ĵ��е�λ��
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
    # TODO�������ظ��ʱ�


    # aim_string = '500kV ���� �� ���� Ͷ�� ʱ�� Ϊ 2008 �� 12 �� �� ���� ��¡ �� �� ֹ�� ���� �� �� ��· �ܳ��� Ϊ 176.602 km �� ���� �� 417 �� �� �� ��· 2014 �� ״̬ ���� Ϊ ע�� ״̬ �� # 288 - # 289 ��Խ �½� ���� ���ٹ�· , # 288 �� ���� ˫ ���� ��Ե�� �� ��'
    # source_string='''500kVТ�������Ͷ��ʱ��Ϊ2007��11�£�����Т�б䣬ֹ�ڛ��ӱ䣬��·�ܳ���Ϊ87.521km��������199��������·2014��״̬����Ϊ����״̬�� �������⣺�����˼����2015��45���ģ��������˼첿���ڿ�չ���Ͼ�Ե�ӷ�����������������֪ͨ���Բ�����Ҫ��ĸ��Ͼ�Ե�ӽ��и����� ��Ҫ�������ݣ�1����17#��51#��52#��60#��61#��95#��96#��115#��116#��147#����10��ֱ�����������൥I����Ϊ˫I���� 2��ԭ��������I���ҵ�ԭ��ƾ�Ϊ���ҵ㣬�����轫���߽Ǹֽ��и���������Ϊ����˫�ҵ㡣'''
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
    #TODO:��������
    # file = open("cutdatas.txt", "r",encoding="utf-8").readlines()
    # # print(list(enumerate(file)))
    #
    # for num, value in list(enumerate(file)):
    #     # print(num)
    #     if 'id : 80' in value:
    #         print(num)

    #TODO���ִʲ���
    #
    # source_str = "500kV���ɽ���վ1982����ʽ����Ͷ�ˡ�2#����ѹ�������׹�,����Ϊ�ձ�������˾����������1980�꣬Ͷ������1982�꣬����ʱ�䳤��33�ꡣ���ڵ����⣺2016��4�¼����з���B���ѹ�����ֵ�ѹ�׹�ĩ����Ե���費�ϸ����Ե��׹ܴ������������ѹ�׹ܽ�����ĳ����ȱ�ݣ��䰲ȫ�ɿ���ָ�����ԴﵽҪ��Ӱ�찲ȫ���У��Ҹ�ѹ�׹�����ͬ����ͬ���εĲ�Ʒ����Ʒ����Ӱ�찲ȫ�ȶ����У�����׹ܽ��д��ޡ���Ҫ�������ݣ����500kV���ɽ���վ2#����B���׹�1�飨5ֻ�����з������޲���װ��"
    # jieba.load_userdict(base_dir + r"\newDict.txt")
    # source_str= re.sub(r'[\r\n\t\d]', '', source_str)
    # source_str = ' '.join(jieba.cut(source_str))
    # print(source_str)

