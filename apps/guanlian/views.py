from django.http import HttpResponse
from guanlian import FillReleTable, guanlianStatistics,guanlianShow

import json
# Create your views here.
def FinishFillStatistics(request):
    if request.method == 'POST':
        per = json.loads(request.body)
        print(per)
        # TODO：接口改PER
        if per:
            # proType = per.get('proType')
            # proAddr = per.get('proAddr')
            # relaObject = per.get('relaObject')
            releClass = per.get('relaClass')
            releType = per.get('relaType')

            #TODO： 写统计表、
            print('写统计表.....')
            guanlianStatistics.writeRele_statistics(releType)

            # 写各种关联表
            # FillReleTable.fillReleTable(proType, proAddr, relaClass, relaType, relaObject)
            response = HttpResponse('''[{"STATE": 0}]''')
            response["Access-Control-Allow-Origin"] = "*"
            response["Content-Type"] = "application/json;charset=UTF-8"
            return response
        finished = 1
        response = HttpResponse('''[{"STATE": 1}]''')
        response["Access-Control-Allow-Origin"] = "*"
        response["Content-Type"] = "application/json;charset=UTF-8"
        return response
    #返回结束信号
    response = HttpResponse('''[{"STATE": 2}]''')
    response["Access-Control-Allow-Origin"] = "*"
    response["Content-Type"] = "application/json;charset=UTF-8"
    return response


def FinishFillShow(request):
    if request.method == 'POST':
        per = json.loads(request.body)
        print(per)
        # TODO：接口改PER
        """
        {
            "releType":"1",
            "proType": "6",
            "proAddr":"1",
            "relaClass":"1",
            "SEtime":[2017,2018],
            "relaObject":"1",
        }
        """
        if per:
            releType1 = per.get('relaClass')
            releType2 = per.get('relaType')
            proType = per.get('proType')
            proAddr = per.get('proAddr')
            releObject = str(per.get('relaObject'))
            SEtime = per.get('SEtime')
            startYear = str(SEtime[0])
            endYear = str(SEtime[1])

            # TODO： 写各种关联表
            guanlianShow.writeReleTable(releType1,releType2,proType,proAddr,releObject,startYear,endYear)
            response = HttpResponse('''[{"STATE": 0}]''')
            response["Access-Control-Allow-Origin"] = "*"
            response["Content-Type"] = "application/json;charset=UTF-8"
            return response

        finished = 1
        response = HttpResponse('''[{"STATE": 1}]''')
        response["Access-Control-Allow-Origin"] = "*"
        response["Content-Type"] = "application/json;charset=UTF-8"
        return response
    # 返回结束信号
    response = HttpResponse('''[{"STATE": 2}]''')
    response["Access-Control-Allow-Origin"] = "*"
    response["Content-Type"] = "application/json;charset=UTF-8"
    return response