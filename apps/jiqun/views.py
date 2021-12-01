from django.shortcuts import render
from utils import sqlhelper
from django.http import HttpResponse
import json


# Create your views here.
# coding: utf-8

def findclurele(request):

    if request.method == 'POST':
        request_data = json.loads(request.body)
        print(request_data)

        if request_data:
            proType = int(request_data.get('proType'))
            proAddr = int(request_data.get('proAddr'))
            cluType = int(request_data.get('cluType'))

            sqlhelper.execute('''truncate clu_rele''')
            try:
                mycom = '''insert into clu_rele(cluType,proType,proName ,proCode,proImpleYear) select  cluType_id,proType_id,proName,proCode,proImpleYear from multisource_data where '''

                if proAddr==0 and proType!=0:
                    print("hfueihf")
                    mand = '''(cluType_id=%s and proType_id=%s)''' % (cluType, proType)

                elif proAddr!=0 and proType==0:
                    mand = '''(cluType_id=%s and province_id=%s)''' % (cluType, proAddr)
                elif proAddr==0 and proType==0:
                    mand = '''(cluType_id=%s)''' % (cluType)

                else:
                    print("Hfuihui")
                    mand = '''(cluType_id=%s and proType_id=%s and province_id=%s)''' % (cluType,proType,proAddr)
                sqlhelper.execute(mycom+mand)
                print(mycom+mand)
            except Exception as e:
                print(e)

            response = HttpResponse('''[{"STATE": 0}]''')
            response["Access-Control-Allow-Origin"] = "*"
            response["Content-Type"] = "application/json;charset=UTF-8"
            return response
        response = HttpResponse('''[{"STATE": 1}]''')
        response["Access-Control-Allow-Origin"] = "*"
        response["Content-Type"] = "application/json;charset=UTF-8"
        return response
    response = HttpResponse('''[{"STATE": 2}]''')
    response["Access-Control-Allow-Origin"] = "*"
    response["Content-Type"] = "application/json;charset=UTF-8"
    return response

# from __future__ import print_function
# import os
# import tensorflow as tf
# import tensorflow.contrib.keras as kr
# from jiqun.cnn_model import TCNNConfig, TextCNN
# from jiqun.data.cnews_loader import read_category, read_vocab
#
# try:
#     bool(type(unicode))
# except NameError:
#     unicode = str
#
# base_dir = './jiqun/data/cnews'
# vocab_dir = os.path.join(base_dir, 'cnews.vocab.txt')
#
# save_dir = './jiqun/checkpoints/textcnn'
# save_path = os.path.join(save_dir, 'best_validation')  # 最佳验证结果保存路径
#                                                        # model_checkpoint_path: "best_validation"
#                                                        # all_model_checkpoint_paths: "best_validation"
#
# class CnnModel:
#     def __init__(self):
#         self.config = TCNNConfig()
#         self.categories, self.cat_to_id = read_category()
#         self.words, self.word_to_id = read_vocab(vocab_dir)
#         self.config.vocab_size = len(self.words)
#         self.model = TextCNN(self.config)
#         self.session = tf.Session()
#         self.session.run(tf.global_variables_initializer())
#         saver = tf.train.Saver()
#         saver.restore(sess=self.session, save_path=save_path)  # 读取保存的模型
#
#     def predict(self, message):
#         # 支持不论在python2还是python3下训练的模型都可以在2或者3的环境下运行
#         content = unicode(message)
#         data = [self.word_to_id[x] for x in content if x in self.word_to_id]
#
#         feed_dict = {
#             self.model.input_x: kr.preprocessing.sequence.pad_sequences([data], self.config.seq_length),
#             self.model.keep_prob: 1.0
#         }
#
#         y_pred_cls = self.session.run(self.model.y_pred_cls, feed_dict=feed_dict)
#         return self.categories[y_pred_cls[0]]
#
# def JQ(proDesc):
#     cnn_model = CnnModel()
#     #return('集群类别：',cnn_model.predict(proDesc))
#     return (cnn_model.predict(proDesc))


