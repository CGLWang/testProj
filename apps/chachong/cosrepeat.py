# coding=utf-8

import re, sys, datetime
import jieba
jieba.setLogLevel(jieba.logging.INFO)
import difflib
import os




def msplit(s, seperators=',|\.|\?|，|。|？|！'):               #划分句子
     return re.split(seperators, s)

def compare(str1,str2):                                      #比较文本
    list = yuchuli(str1,str2)
    doc1 = msplit(str1)
    doc2 = msplit(str2)
    for item in list:                                             #把文档1和2中的重复语句移除，形成两个完全不同的新文档
        doc1.remove(item)
        doc2.remove(item)
    str1 = ''
    for item1 in doc1:
        str1 += item1
    str2 = ''
    for item2 in doc2:
        str2 += item2

    # T1=jieba.lcut(str1, cut_all=False)
    # T2 = jieba.lcut(str2, cut_all=False)
    T1 = fenci(str1)
    T2 = fenci(str2)
    T3 = find(T1,T2)
    return T3

def  fenci(item):                         # 对语句进行分词
    print(os.getcwd())
    with open('apps/chachong/stopwords.txt', 'r', encoding='utf-8') as f:
        str = f.read()
        stop_words  =  str.splitlines()
        result = [k for k in jieba.lcut(item, cut_all=False) if k not in stop_words]
    return result

def find(list1,list2):                    # 找出两个列表都存在的元素
    a = [x for x in list1 if x in list2]
    return a

def yuchuli(str1,str2):                    #预处理先找出两个文本完全重复的句子
    list = []
    doc1 = msplit(str1)
    doc2 = msplit(str2)
    for item2 in doc2:  # 输出重复的语句
        if item2 in doc1:
            list.append(item2)
    return list

def string_similar(doc1,doc2):
    s1 = ''
    for item1 in doc1:
        s1 += item1
    s2 = ''
    for item2 in doc2:
        s2 += item2
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()

def mainfun(doc1,doc2):
    list1 = yuchuli(doc1,doc2)
    list2 = compare(doc1,doc2)
    list = []
    sim = string_similar(doc1, doc2)
    list = list1 + list2
    print(sim)
    return list









































