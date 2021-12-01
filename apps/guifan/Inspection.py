#!/usr/bin/env python
#!-*- coding:utf-8 -*-
#!time      : 2019/3/7 15:07
#!@Author   : Tang
#!@File     :.py
import xlrd
import re
import os

# 检查名字里的重复(5个字检查)
def again(example):
    repeat_flag = 0
    # example = re.sub('[电感容、，0kV#\-]', '', example)
    #example =example.replace('0kV','').replace('')
    for i in range(len(example)-4):
        remain = example[:i]+example[i+5:]
        # print('delete:',example[i:i+4])
        # print("remian:", remain)
        if example[i:i+5] in remain:
            # print('重复重复！')
            repeat_flag = 1
            break
    return repeat_flag

# 各个专项的检查函数
'''大修，技改'''
def check_DXJG(P_name):
    element_Dict={'normValue':None,'abnormRea':None}
    if again(P_name):
        return {'normValue':1,'abnormRea':'项目名称字段冗余'}
    # 项目名中类似安装字眼的是一种 pat（动宾结构）
    except_list = ['更换', '加装','安装','新增']
    # 预防少部分带有特殊字眼的 宾动结构的项目名
    if any(word in P_name for word in except_list ) and (P_name[-1] not in ['装','换','增']):
        pat = '(.*?中心|.*公司|.*?市场|.*?分部)(\d*kV|.*楼)(.*?)(新增|更换|加装|安装)(.*)'
        ans = re.match(pat, P_name)
        if re.match(pat, P_name):
            if ans.group(5)[-1] == P_name[-1]:
                element_Dict={'BO2': ans.group(1),
                              'BO3': ans.group(5),
                              'BO4': ans.group(2),
                              'BO6': ans.group(3),
                              'BO5': ans.group(4),
                              }
                error_reson = '命名符合规范'
                error_flag = 0
            else:
                error_reson = '命名结尾字段冗余'
                error_flag = 1
        else:
            pat1 = '(.*?中心|.*公司|.*?市场|.*?分部)(.*)'
            if not re.match(pat1, P_name):
                error_reson = 'BO2:项目单位不明确'
                error_flag = 1
            else:
                pat2 = '(.*?中心|.*公司|.*?市场|.*?分部)(\d*kV|.*楼)(.*)'
                if not re.match(pat2, P_name):
                    error_reson = 'BO4:调度设施或电压等级错误'
                    error_flag = 1
                else:
                    error_reson = 'BO5:项目内容简述不明'
                    error_flag = 1
    else:
        # 项目名正常语序是一种pat（宾动结构）
        P_name = re.sub('工程|项目','',P_name)
        pat = '(.*中心|.*公司|.*市场|.*分部|华中电网)(\d*kV)*(.*?站|.*?线路|.*?回|.*?线|.*?变)?(\d*V)*(.*)' \
              '(完善|整修|检修|治理|改造|更换|大修|防腐|修理|X光探伤|三维建模|升级|维修|整治|修筑' \
              '|安装|监测|建设|技改|提升|抢修|单改双|更新|加装|扩容|故障处理|应用|新增)'
        ans = re.match(pat, P_name)
        if re.match(pat, P_name):
            # 各个字段
            if ans.group(6)[-1] == P_name[-1]:
                element_Dict = {'BO2': ans.group(1),
                            'BO4': ans.group(2),
                            'BO6': ans.group(3),
                            'BO3': ans.group(5),
                            'BO5': ans.group(6),
                            }
                error_reson = '命名符合规范'
                error_flag = 0
            else:
                error_reson = 'BO5：内容简述不标准（末尾不能有括号补充，结尾用词要标准）'
                # print('项目名称冗余')
                error_flag = 1

        else:
            pat1 = '(.*?中心|.*公司|.*?市场|.*?分部)(.*)'
            if not re.match(pat1, P_name):
                error_reson = 'BO2:项目单位不明确'
                error_flag = 1
            else:
                pat2 = '(.*中心|.*公司|.*市场|.*分部)(\d*kV)*(.*?站|.*?线路|.*?回|.*?线|.*?变)?(.*)'
                if not re.match(pat2, P_name):
                    error_reson = 'BO4:调度设施或电压等级错误'
                    error_flag = 1
                else:
                    error_reson = 'BO5:项目内容简述不明'
                    error_flag = 1
    element_Dict['normValue'] = error_flag
    element_Dict['abnormRea'] = error_reson
    return element_Dict


'''研究开发，管理咨询
【B02研究内容 】+ 【B03研究性质】
'''
def check_YJGL(P_name):

    conflag = None
    element_Dict = {'normValue':None,'abnormRea':None}
    if again(P_name):
        return {'normValue': 1, 'abnormRea': '字段重复'}
    txt =re.sub('\d','',P_name)
    if len(txt) < 7:
        return {'normValue': 1, 'abnormRea': 'BO2:项目内容不明(请说明关于什么内容的研究或管理)'}
    words_list = ['研','开发','技术支持','分析','技术服务','诊','监','管','查','测']
    for word in words_list:
        if word in P_name:
            conflag = 1
            break
    if conflag != 1:
        return {'normValue': 1, 'abnormRea': 'BO3:项目性质不明(是研究是开发是管理)'}
    #pat = '(.*?)(研究|应用|分析|研制|编制|开发|诊断|技术服务|支持服务|技术支持|管控|监督|督查|审查|检测|督查服务)$'
    else:
        pat = '(.*?)(编制|研究|研制|分析|诊断|检测|管理|查|服务|支持|管控|应用|开发)$'
        ans = re.match(pat, P_name)

        if ans:
            element_Dict = {'BO2': ans.group(1),
                            'BO3': ans.group(2),

                            }
            error_reson = '命名规范'
            error_flag = 0
        else:
            error_reson = '要素结构不符合标准 (按项目内容+项目性质)'
            error_flag = 3
    element_Dict['normValue'] = error_flag
    element_Dict['abnormRea'] = error_reson
    return element_Dict

'''
信息化

[业务科目（B07）/项目所属单位（B02）]+[内容名称（B03）]+[项目性质（B05）]+[项目类别（B08）]
'''
def check_XXH(P_name):
    element_Dict = {'normValue': None, 'abnormRea': None}
    if '-' not in P_name:
        return {'normValue': 1, 'abnormRea': 'BO2/BO7：缺少所属单位或业务科目,BO5：缺少项目性质(缺少第几期信息)'}
    if '期' not in P_name and '新建' not in P_name:
        return {'normValue': 1, 'abnormRea': 'BO5：缺少项目性质(缺少第几期信息)'}
    if '项目' not in P_name:
        return {'normValue': 1, 'abnormRea': 'BO8：缺少项目类别(可能结尾漏掉"项目")'}

    # 排除BO5和BO8
    if '本性' in P_name:
        # pat = '(.*?)-(.*?)-(.*?)-(.*?)-(.*本性)'
        pat = '(.*?)-(.*?)(（.期）|-.*?)-(.*?)-(.*本性)'
    elif P_name[-1] == '目':
        # pat = '(.*?)-(.*?)-(.*?)-(.*项目)'
        pat = '(.*?)-(.*?)(（.期）|-.*?)-(.*项目)'
    else:
        pat = '(.*?)-(.*?)-(.*)(.*?)'
    ans = re.match(pat, P_name)

    if ans:
        element_Dict = {'BO7': ans.group(1),  # 业务科目
                        'BO3': ans.group(2),  # 内容名称
                        'BO5': ans.group(3),  # 项目性质
                        'BO8': ans.group(4),  # 项目类别
                        }
        error_flag = 0
        error_reson = '命名规范'
    else:
        pat = '(.*?)-(.*?)-(.*?)'
        if re.match(pat, P_name):
            error_flag = 1
            error_reson = 'BO2/BO7/BO3：可能缺少所属单位或业务科目也可能缺少内容名称'
        else:
            error_flag = 3
            error_reson = '发生未知错误'
    element_Dict['normValue'] = error_flag
    element_Dict['abnormRea'] = error_reson
    return element_Dict
'''零星购置
【项目所属单位（B02）】+【设备名称（B03）】+【项目性质（B05）】
'''
def check_LXGZ(P_name):
    error_flag = None
    error_reson = None
    element_Dict = {'normValue':None,'abnormRea':None}
    if again(P_name):
        element_Dict = {'normValue': 1, 'abnormRea': '存在重复字段'}
    pat = '(.*中心|.*楼|.*公司|.*分部)(\d*年)*(.*)(购置|更新)'
    ans = re.match(pat, P_name)
    if ans:
        if ans.group(4)[-1] == P_name[-1]:
            element_Dict = {'BO2': ans.group(1),
                        'BO3': ans.group(3),
                        'BO5': ans.group(4),
                        }
            error_flag = 0
            error_reson = '命名正确'

        else:
            error_reson = '命名结尾字段冗余'
            error_flag = 1
    else:
        pat1 = '(.*中心|.*楼|.*公司|.*分部)(\d*年)*(.*)'
        if not re.match(pat1, P_name):
            error_flag = 1
            error_reson = 'BO2：所属单位不明'
        else:
            error_flag = 1
            error_reson = 'BO5：项目性质不明'
    element_Dict['normValue'] = error_flag
    element_Dict['abnormRea'] = error_reson
    return element_Dict

'''非生产技改项目'''
def check_FSCDX(P_name):
    error_flag = None
    error_reson = None
    element_Dict = {'normValue':None,'abnormRea':None}
    if again(P_name):
        element_Dict = {'normValue': 1, 'abnormRea': '名称字段重复'}
    pat = '(.*?中心|.*楼|.*?公司|.*?分部)(.*系统|.*小区)*(.*)(改造|维修|物业分离|大修|供水分离|供热分离|更换|供电分离)'
    P_name = re.sub('项目','',P_name)
    ans = re.match(pat, P_name)
    if ans:
        if ans.group(4)[-1] == P_name[-1]:
            element_Dict = {'BO2': ans.group(1),
                        'BO3': ans.group(3),
                        'BO5': ans.group(4),
                        }
            error_reson = '命名符合规范'
            error_flag = 0

        else:
            error_reson = '命名结尾字段冗余'
            error_flag = 1
    else:
        pat1 = '(.*?中心|.*公司|.*?市场|.*?分部)(.*)'
        if not re.match(pat1, P_name):
            error_reson = 'BO2:项目单位不明确'
            error_flag = 1
        else:
            pat2 = '(.*?中心|.*楼|.*?公司|.*?分部)(.*系统|.*小区)*(.*)'
            if not re.match(pat2, P_name):
                error_reson = 'BO3:项目内容不明'
                error_flag = 1
            else:
                error_reson = 'BO5:项目性质不明'
                error_flag = 1
    element_Dict['normValue'] = error_flag
    element_Dict['abnormRea'] = error_reson
    return element_Dict


'''教育培训
【单位名称（B02）】+【项目内容（B03）】+【项目性质（B05）】
'''
def check_JYPX(P_name):
    element_Dict = {'normValue':None,'abnormRea':None}
    if again(P_name):
        return  {'normValue':1,'abnormRea':'字段重复'}
    pat = '(.*?本部|.*?公司|.*?分部)(.*)(培训|竞赛|调考|评选|认证)(包)*'
    ans = re.match(pat, P_name)
    if ans:

        element_Dict = {'BO2': ans.group(1),
                    'BO3': ans.group(2),
                    'BO5': ans.group(3),
                    }
        error_reson = '命名符合规范'
        error_flag = 0
    else:
        pat1 = '(.*?本部|.*?公司|.*?分部)(.*)'
        if not re.match(pat1, P_name):
            error_flag = 1
            error_reson = 'BO2：所属单位不明确'
        else:
            error_flag = 1
            error_reson = 'BO5：项目性质不明确（培训还是竞赛还是评选等性质不明）'
    element_Dict['normValue'] = error_flag
    element_Dict['abnormRea'] = error_reson
    return element_Dict


# '''电网小型基建（暂时使用教育培训的模板）'''
# def check_XXJJ(P_name):
#     element_Dict = {'normValue': None, 'abnormRea': None}
#     if again(P_name):
#         return {'normValue': 1, 'abnormRea': '字段重复'}
#     pat = '(.*?本部|.*?公司|.*?分部)(.*)(改造|维修|扩建)*'
#     ans = re.match(pat, P_name)
#     if ans:
#
#         element_Dict = {'BO2': ans.group(1),
#                         'BO3': ans.group(2),
#                         }
#         error_reson = '命名符合规范'
#         error_flag = 0
#     else:
#         error_flag = 1
#         error_reson = 'BO2：所属单位不明确'
#     element_Dict['normValue'] = error_flag
#     element_Dict['abnormRea'] = error_reson
#     return element_Dict
'''电网小型基建（暂时使用教育培训的模板）'''
#todo:20191922修改了小型基建内容
def check_XXJJ(P_name):
    element_Dict = {'normValue': None, 'abnormRea': None}
    if again(P_name):
        return {'normValue': 1, 'abnormRea': '字段重复'}
    cls_list = ['改造','维修','扩建','建设']
    if P_name[-2:] in cls_list:
        pat = '(.*?本部|.*?公司|.*?分部|.*?）|.*?中心|.*?电科院|.*?电业局|.*学校)(.*)(改造|维修|扩建|建设)'
        ans = re.match(pat, P_name)
        if ans:

            element_Dict = {'BO2': ans.group(1),
                            'BO3': ans.group(2),
                            'BO5': ans.group(3)
                            }
            # print(element_Dict)
            error_reson = '命名符合规范'
            error_flag = 0
        else:
            error_flag = 1
            error_reson = 'BO2：所属单位不明确'
        element_Dict['normValue'] = error_flag
        element_Dict['abnormRea'] = error_reson
    else:
        pat = '(.*?本部|.*?公司|.*?分部|.*?）|.*?中心|.*?电科院|.*?电业局|.*学校)(.*)'
        ans = re.match(pat, P_name)
        if ans:

            element_Dict = {'BO2': ans.group(1),
                            'BO3': ans.group(2),
                            }
            # print(element_Dict)
            error_reson = '命名符合规范'
            error_flag = 0
        else:
            error_flag = 1
            error_reson = 'BO2：所属单位不明确'
        element_Dict['normValue'] = error_flag
        element_Dict['abnormRea'] = error_reson
    return element_Dict

#todo:20191022修改了电网基建内容
'''电网基建'''
def check_DWJJ(P_name):

    error_flag = 0
    error_reson = '命名符合规范'
    ans =0
    element_Dict = {'normValue':None,'abnormRea':None}
    if again(P_name):
        error_flag = 1
        error_reson = '项目名称字段冗余'
        #print('AGAIN!')
    if ('～' in P_name or '~' in P_name) and '送出' not in P_name:
        P_name = P_name.replace('至', '～')
        P_name = P_name.replace('~', '～')
        # 纯线路
        # pat = '([\u4E00-\u9FA5]{2})([\u4E00-\u9FA5]+～[\u4E00-\u9FA5]+)(π入|改接|T接)*(.*)(\d+kV)?(线路工程|线路改造工程|线路新建工程)'
        pat = '([\u4E00-\u9FA5]+)((\d+kV)*[\u4E00-\u9FA5]+～(\d+kV)*[\u4E00-\u9FA5]+)(π入|改接|T接)*(.*?)(\d+kV)(线路工程|线路改造工程|线路新建工程)'
        ans = re.match(pat, P_name)
        if ans:
            if ans.group(8)[-1] == P_name[-1]:

                element_Dict = {'BO1': ans.group(1),
                                'BO3': ans.group(2),
                                'BO4': ans.group(7),
                                'BO8': ans.group(8),
                                }
                # print(element_Dict)
            else:
                error_reson = '命名结尾字段冗余'
                error_flag = 1
        else:
            pat1 = '([\u4E00-\u9FA5]+)((\d+kV)*[\u4E00-\u9FA5]+～(\d+kV)*[\u4E00-\u9FA5]+)(π入|改接|T接)*(.*?)(\d+kV)(.*)'
            if re.match(pat1, P_name):
                error_flag = 1
                error_reson = 'BO8：项目性质表述不规范'
            else:
                pat2 = '([\u4E00-\u9FA5]+)((\d+kV)*[\u4E00-\u9FA5]+～(\d+kV)*[\u4E00-\u9FA5]+)(π入|改接|T接)*(.*?)(线路工程|线路改造工程|线路新建工程)'
                if re.match(pat2, P_name):
                    error_flag = 1
                    error_reson = 'BO4：线路电压等级不明确'
                else:
                    pat3 = '(.+～.+)(π入|改接|T接)*(.*?)(\d+kV)(线路工程|线路改造工程|线路新建工程)'
                    if re.match(pat3, P_name):
                        error_flag = 1
                        error_reson = 'BO1：项目省份不明确'
                    else:
                        error_flag = 1
                        error_reson = '缺少电压等级，缺少省份或地区信息'

    #线路改造工程：
    elif '线路工程' in P_name or '线路改造工程' in P_name:

        pat = '(.*?)(\d+kV.*变)*(\d+kV|低压)(.+线|.+变|.+分支)*(线路工程|线路改造工程)'
        ans = re.match(pat, P_name)
        if ans:
            if ans.group(5)[-1] == P_name[-1]:

                element_Dict = {'BO1': ans.group(1),
                                'BO3': ans.group(2),
                                'BO4': ans.group(3),
                                'BO8': ans.group(5),
                                }
            else:
                error_reson = '命名结尾字段冗余'
                error_flag = 1
        else:
            pat2 = '(.*?)(\d+kV.*变)*(.+线|.+变|.+分支)*(线路工程|线路改造工程)'
            if re.match(pat2, P_name):
                error_flag = 1
                error_reson = 'BO4：电压等级有误'
            else:
                pat1 = '(.*?)(\d+kV.*变)*(\d+kV|低压)(.*)'
                if re.match(pat1, P_name):
                    error_flag = 1
                    error_reson = 'BO5：项目类型有误'

    #TODO:20191015建设改造工程
    elif '建设改造' in P_name:
        pat = '(\d{4}年)*(.+?)(\d+kV.*变)(\d+kV|10kV及以下)(线路)*(建设改造工程)'
        ans = re.match(pat, P_name)
        if ans:
            if ans.group(6)[-1] == P_name[-1]:
                element_Dict = {'BO1': ans.group(2),
                                'BO3': ans.group(3),
                                'BO5': ans.group(6),
                                }
                # print(element_Dict)
            else:
                error_reson = '命名结尾字段冗余'
                error_flag = 1
        else:
            pat2 = '(\d{4}年)*(.+?)(\d+kV.*变)(\d+kV|10kV及以下)*(线路)*(建设改造工程)'
            if re.match(pat2, P_name):
                error_flag = 1
                error_reson = 'BO3：项目电压等级缺失'
            else:
                pat1 = '(\d{4}年)*(.+?)(\d+kV.*变)(\d+kV|10kV及以下)(线路)*(.*)'
                if re.match(pat1, P_name):
                    error_flag = 1
                    error_reson = 'BO5：项目类型表述不当'



    elif '送出' in P_name or '外送' in P_name:
        # 送出工程
        pat =  "(.*?)(\d+kV)(变电站(\d+kV)|线路)*(送出工程)"
        if re.match(pat, P_name):
            ans = re.match(pat, P_name)
            if ans.group(5)[-1] == P_name[-1]:
                element_Dict = {'BO1': ans.group(1),
                                'BO3': ans.group(2),
                                'BO4': ans.group(3),
                                'BO8': ans.group(5),
                            }
            else:
                error_reson = '命名结尾字段冗余'
                error_flag = 1
        else:
            pat1 = '(.{2})(.*?)(\d+kV)(.*)'
            if not re.match(pat1,P_name):
                error_flag = 1
                error_reson = 'BO4：电压等级不明确'
            else:
                error_flag = 1
                error_reson = 'BO8：项目类别不明确'


    elif '供电工程' in P_name:
        # 铁路供电
        pat = "(.+铁路)([\u4E00-\u9FA5]{2})(.*)(\d{3}kV)(.+供电工程)"
        if re.match(pat, P_name):
            ans = re.match(pat, P_name)
            if ans.group(5)[-1] == P_name[-1]:
                element_Dict = {'BO3': ans.group(1),
                                'BO1': ans.group(2),
                                'BO4': ans.group(4),
                                'BO8': ans.group(5),
                            }
            else:
                error_reson = '命名结尾字段冗余'
                error_flag = 1
        else:
            pat1 = '(.+铁路)(.*)'
            if not re.match(pat1, P_name):
                error_flag = 1
                error_reson = 'BO3：铁路公司不明确'
            else:
                pat2 = '(.+铁路)([\u4E00-\u9FA5]{2})(.*)(\d{3}kV)(.*)'
                if not re.match(pat2, P_name):
                    error_flag = 1
                    error_reson = 'BO4：电压等级不明确'
                else:
                    error_flag = 1
                    error_reson = 'BO8：项目类别不明确'


    elif '项目包' in P_name:
        pat ="(\d+年)(.*?)(\d+kV.*?)(（第.批）项目包)"
        if re.match(pat, P_name):
            ans = re.match(pat, P_name)
            if ans.group(4)[-1] == P_name[-1]:
                element_Dict = {'BOA': ans.group(1),
                            'BO1': ans.group(2),
                            'BO4': ans.group(3),
                            'BO3': ans.group(4),
                            }
            else:
                error_reson = '命名结尾字段冗余'
                error_flag = 1
        else:
            pat1 ='(\d+年)(.*)$'
            if not re.match(pat1, P_name):
                error_flag = 1
                error_reson = 'BOA：年份不明确'
            else:
                pat2 = '(\d+年)(.*?)(\d+kV.*?)(.*)'
                if not re.match(pat2, P_name):
                    error_flag = 1
                    error_reson = 'BO4：电压等级不明确'
                else:
                    error_flag = 1
                    error_reson = 'BO3：项目包批次不明确'

    # elif '10kV' in P_name:
    #     #10kV
    #     pat = '(.*)(10kV)(.*)((新建|配套送出|更换|改造)工程)'
    #     if re.match(pat, P_name):
    #         ans = re.match(pat, P_name)
    #         if ans.group(4)[-1] == P_name[-1]:
    #             element_Dict = {'BO1': ans.group(1),
    #                         'BO4': ans.group(2),
    #                         'BO3': ans.group(3),
    #                         'BO5': ans.group(4),
    #                         }
    #         else:
    #             error_reson = '命名结尾字段冗余'
    #             error_flag = 1
    #     else:
    #         pat1 ='(.*)(10kV)(.*)$'
    #         if not re.match(pat1, P_name):
    #             error_flag = 1
    #             error_reson = 'BO4：电压等级有误'
    #         else:
    #             error_flag = 1
    #             error_reson = 'BO5：项目类型错误'

    #TODO:农网改造20191015
    #农网没有结构直接过
    elif '农网' in P_name or '整村' in P_name or '行政村' in P_name :
        pass

    # 其他项目
    elif 'kV' not in P_name:
        # 独立二次
        if '千伏' in P_name:
            error_reson = 'B04:电压等级有误'
            error_flag = 1
        else:
            pat = "(.*?)((配电|光|省级|地县|调度|通).*)(建设工程|改造工程|新建工程)"
            if re.match(pat, P_name):
                ans = re.match(pat, P_name)
                if ans.group(4)[-1] == P_name[-1]:
                    element_Dict = {'BO1': ans.group(1),
                                'BO3': ans.group(2),
                                'BO5': ans.group(4),
                                }
                else:
                    error_reson = '命名结尾字段冗余'
                    error_flag = 1

            else:
                pat1 = '(.*?)((配电|光|省级|地县|调度|通).*)(.*)$'
                if re.match(pat1, P_name):
                    error_flag = 1
                    error_reson = 'BO5：项目类型错误'
                else:
                    pat2 = '(.*?)(建设工程|改造工程|新建工程)'
                    if re.match(pat2, P_name):
                        error_flag = 1
                        error_reson = '项目内容或者电压等级有误'


    else:
        # 输变电，纯变电,升、降压工程
        # todo:大小模板修改 10191014
        pat = '(\d{4}年)*(.*?)(\d+kV)(.*主变|.*间隔|.*变电站|开关站|.*线|线路|.*变|.*输变电)*(.*改造工程|扩建工程|增容工程|新建工程|升压工程|降压工程|优化工程|输变电工程)'
        if re.match(pat, P_name):
            ans = re.match(pat, P_name)
            if ans.group(5)[-1] == P_name[-1]:
                element_Dict = {'BO1': ans.group(1),
                                'BO3': ans.group(2),
                                'BO4': ans.group(3),
                                'BO8': ans.group(4),
                                'BO5': ans.group(5),
                                }
                if ans.group(2) == '':
                    error_reson = 'B03:项目地点缺失'
                    error_flag = 1
                # print(element_Dict)
            else:
                error_reson = '命名结尾字段冗余'
                error_flag = 1
        else:

            pat1 = '(\d{4}年)*(.+?)(\d+kV)(.*主变|.*间隔|变电站|开关站|.*线|线路|.*变|.*输变电)*(.*)$'
            if re.match(pat1, P_name):
                error_flag = 1
                error_reson = 'BO5：项目类型有误'
            else:
                pat0 = '(\d{4}年)*(.+?)(\d+kV)(.*)(.*改造工程|扩建工程|增容工程|新建工程|升压工程|降压工程|优化工程|输变电工程)'
                if re.match(pat0, P_name):
                    error_flag = 1
                    error_reson = 'BO8：建设对象描述有误'
                else:
                    pat2 = '(\d{4}年)*(.+?)(.*主变|.*间隔|变电站|开关站|.*线|.*输变电)*(.*改造工程|扩建工程|增容工程|新建工程|升压工程|降压工程|优化工程|输变电工程)'
                    if re.match(pat2, P_name):
                        error_flag = 1
                        error_reson = 'BO4：电压等级有误'
                    else:
                        error_flag = 1
                        error_reson = 'BO1：项目地区有误'
    element_Dict['normValue'] = error_flag
    element_Dict['abnormRea'] = error_reson
    return element_Dict


# 总检查函数
'''总检查函数'''
def checkALL(P_name,P_class):
    element_Dict = {'normValue':None,'abnormRea':None}
    if P_class =='信息化项目':
        element_Dict = check_XXH(P_name)
    if P_class == '零星购置专业项目':
        element_Dict = check_LXGZ(P_name)
    if P_class in ['非生产技改项目','非生产大修项目']:
        element_Dict = check_FSCDX(P_name)
    if P_class =='教育培训项目':
        element_Dict = check_JYPX(P_name)
    if P_class == '小型基建项目':
        element_Dict = check_XXJJ(P_name)
    if P_class == '电网基建项目':
        element_Dict = check_DWJJ(P_name)
    if P_class in ['管理咨询项目','研究开发项目']:
        element_Dict = check_YJGL(P_name)
    if P_class in ['生产技改项目','生产大修项目']:
        element_Dict = check_DXJG(P_name)
    return element_Dict

def findProvince(P_name):
    #print('Pname::',P_name)
    Province_list = ['湖北','湖南','河南','江西','重庆','跨省']
    province_number = 0
    mylist = []
    for i in range(len(Province_list)-1):

        if Province_list[i] in P_name:
            Province_ans = i+1
            mylist.append(i+1)
            province_number +=1
            # break
    # print(Province_ans)
    if province_number==0 or province_number>1:
        return 6
    else:
        return Province_ans

# print(findProvince('国网江西检修公司500kV磁永线江西段防舞治理'))
if __name__ =='__main__':
    # ans = checkALL('2017年各单位数据中心软硬件购置项目',"信息化项目")
    print(findProvince('2017年各单湖北位数据湖南中心软硬江西件购置项目'))
