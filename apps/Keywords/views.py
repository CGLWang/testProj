# from django.http import HttpResponse
# from guanlian import FillReleTable
# import json
# # Create your views here.
# def FinishFillKeyWords(request):
#     if request.method == 'POST':
#         per = json.loads(request.body)
#         print(per)
#         if per:
#             proType = per.get('proType')
#             proAddr = per.get('proAddr')
#             relaObject = per.get('relaObject')
#             relaClass = per.get('relaClass')
#             relaType = per.get('relaType')
#         #TODO:写各种关联表
#             FillReleTable.fillReleTable(proType, proAddr, relaClass, relaType, relaObject)
#             response = HttpResponse('''[{"STATE": 0}]''')
#             response["Access-Control-Allow-Origin"] = "*"
#             response["Content-Type"] = "application/json;charset=UTF-8"
#             return response
#         finished = 1
#         response = HttpResponse('''[{"STATE": 1}]''')
#         response["Access-Control-Allow-Origin"] = "*"
#         response["Content-Type"] = "application/json;charset=UTF-8"
#         return response
#     #返回结束信号
#     response = HttpResponse('''[{"STATE": 2}]''')
#     response["Access-Control-Allow-Origin"] = "*"
#     response["Content-Type"] = "application/json;charset=UTF-8"
#     return response



