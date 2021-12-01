from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request,"index.html")

from django.shortcuts import HttpResponse

import json

def pachong(request):
    zhengce = [
        ['2020-11-11','政策1','内容1','附件'],
        ['2020-1-1','政策2','内容1','附件'],
        ['2011-32-12','政策3','内容3']
    ]
    return render(request, "zhengce.html",{'zhengce':zhengce})

def testjson(request):
    data={
        'patient_name': '张三',
        'age': '25',
        'patient_id': '19000347',
        '诊断': '上呼吸道感染',
    }
    return HttpResponse(json.dumps(data))