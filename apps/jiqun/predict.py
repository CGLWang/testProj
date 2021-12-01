# coding: utf-8

from __future__ import print_function
import os
import tensorflow as tf
import tensorflow.contrib.keras as kr
from jiqun.cnn_model import TCNNConfig, TextCNN
#from cnn_model import TCNNConfig, TextCNN
from jiqun.data.cnews_loader import read_category, read_vocab
import sys
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


try:
    bool(type(unicode))
except NameError:
    unicode = str

#base_dir = r'./jiqun/data/cnews'
base_dir= os.path.split(os.path.realpath(__file__))[0]+'/data/cnews'
vocab_dir = os.path.join(base_dir, 'cnews.vocab.txt')

save_dir =  os.path.split(os.path.realpath(__file__))[0]+r'/checkpoints/textcnn'
save_path = os.path.join(save_dir, 'best_validation')  # 最佳验证结果保存路径
                                                       # model_checkpoint_path: "best_validation"
                                                       # all_model_checkpoint_paths: "best_validation"

class CnnModel:
    def __init__(self):
        self.config = TCNNConfig()
        self.categories, self.cat_to_id = read_category()
        self.words, self.word_to_id = read_vocab(vocab_dir)
        self.config.vocab_size = len(self.words)
        self.model = TextCNN(self.config)
        self.session = tf.Session()
        self.session.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        saver.restore(sess=self.session, save_path=save_path)  # 读取保存的模型

    def predict(self, message):
        # 支持不论在python2还是python3下训练的模型都可以在2或者3的环境下运行
        content = unicode(message)
        data = [self.word_to_id[x] for x in content if x in self.word_to_id]

        feed_dict = {
            self.model.input_x: kr.preprocessing.sequence.pad_sequences([data], self.config.seq_length),
            self.model.keep_prob: 1.0
        }

        y_pred_cls = self.session.run(self.model.y_pred_cls, feed_dict=feed_dict)
        return self.categories[y_pred_cls[0]]
def initt():
    cnn_model = CnnModel()
    return cnn_model

def JQ(proDesc,model =initt()):
    #cnn_model = CnnModel()
    #return('集群类别：',cnn_model.predict(proDesc))
    return(model.predict(proDesc))



#     proDesc1 = "500kV双玉一回起点为双河变电站,终点是玉贤变电站,本工程沿途经过湖北省京山、应城、天门、汉川、蔡甸。该线路全长194.181公里,总杆塔数511基。本次改造新建2基耐张塔、1基直线塔,并更换三相导线。存在问题:500kV双玉一回于1982年投运,500kV双玉一回18#-19#在双河镇周家冲跨越襄荆高速公路,交叉角约为79°;500kV双玉一回19#-20#在双河镇周家冲跨越焦柳铁路,交叉角约为66°;原线路在设计时,上述两区段未采用独立耐张段设计,不满足国网现行相关规范要求,存在安全隐患。主要工作内容:新建2基5A2-J1G型耐张塔(新18#、新20#)、1基5A1-ZB3型直线塔"
#     # proDesc2 ="艾鹤Ⅰ线、艾鹤Ⅱ线、复艾Ⅰ线、岗艾线、民鹤Ⅰ线共5回在运线路的三跨档段耐张线夹未进行X光检测,共计30处跨越点的耐张线夹未进行X光检测。现500kV艾鹤Ⅰ线等5回线路共计30处跨越点的耐张线夹未进行X光检测,不满足国家电网公司关于印发架空输电线路“三跨”运维管理补充规定的通知(国家电网运检【2016】777号)标准要求,需对12回线路共计51处跨越点的耐张线夹进行检测。对500kV艾鹤Ⅰ线等5回线路共计30处跨越点的耐张线夹总计828个进行X光检测。"
#     print(JQ(proDesc1))
#     # print(jiqun(proDesc2))