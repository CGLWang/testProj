#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import sys
import time
from datetime import timedelta
import numpy as np
import tensorflow as tf
from sklearn import metrics
from jiqun.cnn_model import TCNNConfig, TextCNN
from jiqun.data.cnews_loader import read_vocab, read_category, batch_iter, process_file, build_vocab

base_dir = os.path.split(os.path.realpath(__file__))[0]+r'\data\cnews'
train_dir = os.path.join(base_dir, 'cnews.train.txt')  # 返回./data/cnews/cnews.train.txt
test_dir = os.path.join(base_dir, 'cnews.test.txt')
val_dir = os.path.join(base_dir, 'cnews.val.txt')
#vocab_dir = os.path.join(base_dir, 'cnews.vocab.txt')
vocab_dir = base_dir+r'\cnews.vocab.txt'
print('vocab_dir',vocab_dir)

save_dir = os.path.split(os.path.realpath(__file__))[0]+r'\checkpoints\textcnn'
save_path = os.path.join(save_dir, 'best_validation')  # 最佳验证结果保存路径


def get_time_dif(start_time):
    """获取已使用时间"""
    end_time = time.time()
    time_dif = end_time - start_time
    return timedelta(seconds=int(round(time_dif)))
    # ===================================================
    # round(number,digits)
    # 参数
    #   number,要四舍五入的数，digits是要小数点后保留的位数
    #   如果 digits 大于 0，则四舍五入到指定的小数位。
    #   如果 digits 等于 0，则四舍五入到最接近的整数。
    #   如果 digits 小于 0，则在小数点左侧进行四舍五入。
    #   如果round函数只有参数number,等同于digits 等于 0。
    # 返回值
    #   四舍五入后的值
    # ====================================================


def feed_data(x_batch, y_batch, keep_prob):
    feed_dict = {
        model.input_x: x_batch,
        model.input_y: y_batch,
        model.keep_prob: keep_prob
    }
    return feed_dict


def evaluate(sess, x_, y_):
    """评估在某一数据上的准确率和损失"""
    data_len = len(x_)
    batch_eval = batch_iter(x_, y_, 128)
    total_loss = 0.0
    total_acc = 0.0
    for x_batch, y_batch in batch_eval:
        batch_len = len(x_batch)
        feed_dict = feed_data(x_batch, y_batch, 1.0)
        loss, acc = sess.run([model.loss, model.acc], feed_dict=feed_dict)
        total_loss += loss * batch_len
        total_acc += acc * batch_len

    return total_loss / data_len, total_acc / data_len


def train():
    print("Configuring TensorBoard and Saver...")
    # 配置 Tensorboard，重新训练时，请将tensorboard文件夹删除，否则图会覆盖
    tensorboard_dir = os.path.split(os.path.realpath(__file__))[0]+r'\tensorboard\textcnn'
    if not os.path.exists(tensorboard_dir):   # exists存在，判断括号里的文件是否存在
        os.makedirs(tensorboard_dir)    # os.makedirs() 方法用于递归创建目录

    # ====================================================================================================
    # 函数原型:
    #       def scalar(name, tensor, collections=None, family=None)
    # 函数说明：
    #       [1]输出一个含有标量值的Summary protocol（协议） buffer（缓冲区），这是一种能够被tensorboard模块解析的【结构化数据格式】
    #       [2]用来显示标量信息
    #       [3]用来可视化标量信息
    #       [4]其实，tensorflow中的所有summmary操作都是对计算图中的某个tensor产生的单个summary protocol buffer，而
    #          summary protocol buffer又是一种能够被tensorboard解析并进行可视化的结构化数据格式
    #       虽然，上面的四种解释可能比较正规，但是我感觉理解起来不太好，所以，我将tf.summary.scalar()函数的功能理解为：
    #       [1]将【计算图】中的【标量数据】写入TensorFlow中的【日志文件】，以便为将来tensorboard的可视化做准备
    # 参数说明：
    #       [1]name  :一个节点的名字，如下图红色矩形框所示
    #       [2]tensor:要可视化的数据、张量
    # 主要用途：
    #       一般在画loss曲线和accuary曲线时会用到这个函数。
    # ====================================================================================================
    tf.summary.scalar("loss", model.loss)
    tf.summary.scalar("accuracy", model.acc)
    merged_summary = tf.summary.merge_all()  # merged合并、融合/merge_all 可以将所有summary全部保存到磁盘，以便tensorboard显示。如果没有特殊要求，一般用这一句就可一显示训练时的各种信息了。
    writer = tf.summary.FileWriter(tensorboard_dir)  # 指定一个文件用来保存图

    # 配置 Saver
    saver = tf.train.Saver() # 变量的保存是通过tf.train.Saver()方法创建一个Saver管理器，来保存计算图模型中的所有变量
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    print("Loading training and validation data...")
    # 载入训练集与验证集
    start_time = time.time()  # 返回当前时间的时间戳
    x_train, y_train = process_file(train_dir, word_to_id, cat_to_id, config.seq_length)  # 将文件转换为id表示
    x_val, y_val = process_file(val_dir, word_to_id, cat_to_id, config.seq_length)
    # print(x_train.shape)
    time_dif = get_time_dif(start_time)
    print("Time usage:", time_dif)

    # 创建session
    session = tf.Session()
    session.run(tf.global_variables_initializer())
    writer.add_graph(session.graph)  # 将当前参数的graph写入到tensorboard中。sess.graph指当前的网络结构图

    print('Training and evaluating...')
    start_time = time.time()
    total_batch = 0  # 总批次
    best_acc_val = 0.0  # 最佳验证集准确率
    last_improved = 0  # 记录上一次提升批次
    require_improvement = 1000  # 如果超过1000轮未提升，提前结束训练

    flag = False
    for epoch in range(config.num_epochs):  # epoch：迭代次数
        print('Epoch:', epoch + 1)
        batch_train = batch_iter(x_train, y_train, config.batch_size)
        for x_batch, y_batch in batch_train:
            feed_dict = feed_data(x_batch, y_batch, config.dropout_keep_prob)

            if total_batch % config.save_per_batch == 0:
                # 每多少轮次将训练结果写入tensorboard scalar
                s = session.run(merged_summary, feed_dict=feed_dict)
                writer.add_summary(s, total_batch)

            if total_batch % config.print_per_batch == 0:
                # 每多少轮次输出在训练集和验证集上的性能
                feed_dict[model.keep_prob] = 1.0
                loss_train, acc_train = session.run([model.loss, model.acc], feed_dict=feed_dict)
                loss_val, acc_val = evaluate(session, x_val, y_val)  # todo

                if acc_val > best_acc_val:
                    # 保存最好结果
                    best_acc_val = acc_val
                    last_improved = total_batch
                    saver.save(sess=session, save_path=save_path)
                    improved_str = '*'
                else:
                    improved_str = ''

                time_dif = get_time_dif(start_time)
                msg = 'Iter: {0:>6}, Train Loss: {1:>6.2}, Train Acc: {2:>7.2%},' \
                      + ' Val Loss: {3:>6.2}, Val Acc: {4:>7.2%}, Time: {5} {6}'
                print(msg.format(total_batch, loss_train, acc_train, loss_val, acc_val, time_dif, improved_str))

            session.run(model.optim, feed_dict=feed_dict)  # 运行优化
            total_batch += 1

            if total_batch - last_improved > require_improvement:
                # 验证集正确率长期不提升，提前结束训练
                print("No optimization for a long time, auto-stopping...")
                flag = True
                break  # 跳出循环
        if flag:  # 同上
            break


def test():
    print("Loading test data...")
    start_time = time.time()
    x_test, y_test = process_file(test_dir, word_to_id, cat_to_id, config.seq_length)

    session = tf.Session()
    session.run(tf.global_variables_initializer())
    saver = tf.train.Saver()
    saver.restore(sess=session, save_path=save_path)  # 读取保存的模型

    print('Testing...')
    loss_test, acc_test = evaluate(session, x_test, y_test)
    msg = 'Test Loss: {0:>6.2}, Test Acc: {1:>7.2%}'
    print(msg.format(loss_test, acc_test))

    batch_size = 32
    data_len = len(x_test)
    num_batch = int((data_len - 1) / batch_size) + 1

    y_test_cls = np.argmax(y_test, 1)
    y_pred_cls = np.zeros(shape=len(x_test), dtype=np.int32)  # 保存预测结果
    for i in range(num_batch):  # 逐批次处理
        start_id = i * batch_size
        end_id = min((i + 1) * batch_size, data_len)
        feed_dict = {
            model.input_x: x_test[start_id:end_id],
            model.keep_prob: 1.0
        }
        y_pred_cls[start_id:end_id] = session.run(model.y_pred_cls, feed_dict=feed_dict)

    # 评估
    print("Precision, Recall and F1-Score...")
    # print(metrics.classification_report(y_test_cls, y_pred_cls, target_names=categories))

    # 混淆矩阵
    print("Confusion Matrix...")
    cm = metrics.confusion_matrix(y_test_cls, y_pred_cls)
    print(cm)

    time_dif = get_time_dif(start_time)
    print("Time usage:", time_dif)


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in ['train', 'test']:
        raise ValueError("""usage: python run_cnn.py [train / test]""")

    print('Configuring CNN model...')
    config = TCNNConfig()
    if not os.path.exists(vocab_dir):  # 如果不存在词汇表，重建
        build_vocab(train_dir, vocab_dir, config.vocab_size)
    categories, cat_to_id = read_category()
    words, word_to_id = read_vocab(vocab_dir)
    config.vocab_size = len(words)
    model = TextCNN(config)

    if sys.argv[1] == 'train':
        train()
    else:
        test()

# if __name__=='__main__':
#     base_dir = os.getcwd() + r'\data\cnews'
#     vocab_dir = os.path.join(base_dir, 'cnews.vocab.txt')
#     print(vocab_dir)