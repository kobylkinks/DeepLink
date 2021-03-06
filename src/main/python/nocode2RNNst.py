# -*- coding: UTF-8 -*-
from gensim.models import word2vec
from preprocessor import preprocessor

import tensorflow as tf
import numpy as np
import logging
import os
import json

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

VECTOR_SIZE = 100
TRAIN_ITERS = 200
BATCH_SIZE = 20
HIDDEN_SIZE = 100
N_INPUTS = 100
LEARNING_RATE = 0.001

wordModel = word2vec.Word2Vec.load('test/nocode50904245-1-2.model')


# text data
def text2vec(text, isHtml):
    if isHtml:
        seqs = preprocessor.processHTMLNoCamel(text)
    else:
        seqs = preprocessor.preprocessNoCamel(text)
    res = []
    for seq in seqs:
        for word in seq:
            try:
                res.append(wordModel[word])
            except KeyError:
                res.append(np.zeros(VECTOR_SIZE))
    return res


#  shape = [None, seq len, Vec size]
def read_data(path='./train1'):
    X1 = []
    X2 = []
    T = []
    L1 = []
    L2 = []
    LT = []
    Y = []
    filelist = os.listdir(path)
    for i in range(0, len(filelist)):
    # for i in range(0, 1):
        filepath = os.path.join(path, filelist[i])
        logging.info("Loaded the file:"+filepath)
        if os.path.isfile(filepath):
            file = open(filepath, 'rb')
            testlist = json.loads(file.read())
            for map in testlist:
                commit = text2vec(map['commit'], False)
                issue = text2vec(map['issue'], True)
                title = text2vec(map['issuetitle'], False)
                L1.append(len(commit))
                X1.append(commit)
                L2.append(len(issue))
                X2.append(issue)
                LT.append(len(title))
                T.append(title)
                Y.append(float(map['type']))
            file.close()
    return X1, X2, T, L1, L2, LT, Y


# shape=[batch_size, None]
def make_batches(data, batch_size):
    X1, X2, T, L1, L2, LT, Y = data
    num_batches = len(Y) // batch_size
    data1 = np.array(X1[: batch_size*num_batches])
    data1 = np.reshape(data1, [batch_size, num_batches])
    data_batches1 = np.split(data1, num_batches, axis=1)  #  list
    data_batches1_rs = []
    for d1 in data_batches1:
        sub_batch = []
        maxD = 0
        for d in d1:
            for dt in d:
                maxD = max(maxD, len(dt))
        for d in d1:
            for dt in d:
                todo = maxD - len(dt)
                for index in range(todo):
                    dt.append(np.zeros(VECTOR_SIZE))
                sub_batch.append(np.array(dt))
        data_batches1_rs.append(np.array(sub_batch))

    data2 = np.array(X2[: batch_size*num_batches])
    data2 = np.reshape(data2, [batch_size, num_batches])
    data_batches2 = np.split(data2, num_batches, axis=1)
    data_batches2_rs = []
    for d2 in data_batches2:
        sub_batch = []
        maxD = 0
        for d in d2:
            for dt in d:
                maxD = max(maxD, len(dt))
        for d in d2:
            for dt in d:
                todo = maxD - len(dt)
                for index in range(todo):
                    dt.append(np.zeros(VECTOR_SIZE))
                sub_batch.append(np.array(dt))
        data_batches2_rs.append(np.array(sub_batch))

    dataT = np.array(T[: batch_size*num_batches])
    dataT = np.reshape(dataT, [batch_size, num_batches])
    data_batchesT = np.split(dataT, num_batches, axis=1)  #  list
    data_batchesT_rs = []
    for d3t in data_batchesT:
        sub_batch = []
        maxD = 0
        for d in d3t:
            for dt in d:
                maxD = max(maxD, len(dt))
        for d in d3t:
            for dt in d:
                todo = maxD - len(dt)
                for index in range(todo):
                    dt.append(np.zeros(VECTOR_SIZE))
                sub_batch.append(np.array(dt))
        data_batchesT_rs.append(np.array(sub_batch))

    len1 = np.array(L1[: batch_size*num_batches])
    len1 = np.reshape(len1, [batch_size, num_batches])
    len_batches1 = np.split(len1, num_batches, axis=1)
    len_batches1 = np.reshape(np.array(len_batches1), [num_batches, BATCH_SIZE])

    len2 = np.array(L2[: batch_size * num_batches])
    len2 = np.reshape(len2, [batch_size, num_batches])
    len_batches2 = np.split(len2, num_batches, axis=1)
    len_batches2 = np.reshape(np.array(len_batches2), [num_batches, BATCH_SIZE])

    lenT = np.array(LT[: batch_size * num_batches])
    lenT = np.reshape(lenT, [batch_size, num_batches])
    len_batchesT = np.split(lenT, num_batches, axis=1)
    len_batchesT = np.reshape(np.array(len_batchesT), [num_batches, BATCH_SIZE])

    label = np.array(Y[: batch_size*num_batches])
    label = np.reshape(label, [batch_size, num_batches])
    label_batches = np.split(label, num_batches, axis=1)
    return list(zip(data_batches1_rs, data_batches2_rs, data_batchesT_rs, len_batches1, len_batches2, len_batchesT, label_batches))


input1 = tf.placeholder(tf.float64, [BATCH_SIZE, None, VECTOR_SIZE])
input2 = tf.placeholder(tf.float64, [BATCH_SIZE, None, VECTOR_SIZE])
inputT = tf.placeholder(tf.float64, [BATCH_SIZE, None, VECTOR_SIZE])
len1 = tf.placeholder(tf.int64, [BATCH_SIZE, ])
len2 = tf.placeholder(tf.int64, [BATCH_SIZE, ])
lent = tf.placeholder(tf.int64, [BATCH_SIZE, ])
target = tf.placeholder(tf.float64, [BATCH_SIZE, 1])


def RNN(input_data, seq_len):
    rnn_cell = tf.nn.rnn_cell.MultiRNNCell([tf.nn.rnn_cell.BasicLSTMCell(HIDDEN_SIZE) for _ in range(3)])
    outputs, state = tf.nn.dynamic_rnn(rnn_cell, input_data, sequence_length=seq_len, dtype=tf.float64)
    return outputs, state


# initializer = tf.random_uniform_initializer(-0.5, 0.5, dtype=tf.float32)
with tf.variable_scope("commit", reuse=tf.AUTO_REUSE):
    outputs1, states1 = RNN(input1, len1)
with tf.variable_scope("issue", reuse=tf.AUTO_REUSE):
    outputs2, states2 = RNN(input2, len2)
with tf.variable_scope("title", reuse=tf.AUTO_REUSE):
    outputs3, states3 = RNN(inputT, lent)

newoutput1 = states1[-1].h
newoutput2 = states2[-1].h
newoutput3 = states3[-1].h


def getScore(state1, state2):
    pooled_len_1 = tf.sqrt(tf.reduce_sum(state1 * state1, 1))
    pooled_len_2 = tf.sqrt(tf.reduce_sum(state2 * state2, 1))
    pooled_mul_12 = tf.reduce_sum(state1 * state2, 1)
    score = tf.div(pooled_mul_12, pooled_len_1 * pooled_len_2 + 1e-8, name="scores")  # +1e-8 avoid 'len_1/len_2 == 0'
    score = tf.reshape(score, [BATCH_SIZE, 1])
    return score


def getLoss(score, t):
    rs = t - score
    rs = tf.abs(rs)
    return tf.reduce_mean(rs)


def getFinalScore(score1, score2):
    score = tf.concat([score1, score2], 1)
    score = tf.reduce_max(score, 1)
    return tf.reshape(score, [BATCH_SIZE, 1])


# Define loss and optimizer
cos_score1 = getScore(newoutput1, newoutput2)
loss_op1 = getLoss(cos_score1, target)
cos_score2 = getScore(newoutput1, newoutput3)
loss_op2 = getLoss(cos_score2, target)

final_score = getFinalScore(cos_score1, cos_score2)

optimizer = tf.train.AdamOptimizer(learning_rate=LEARNING_RATE)
train_op1 = optimizer.minimize(loss_op1)
train_op2 = optimizer.minimize(loss_op2)


def get_correct(score, target):
    rs = target - score
    rs = np.abs(rs)
    result = 0
    for i in range(len(rs)):
        if score[i][0] < 0 and target[i][0] == 0:
            result = result + 1
        elif rs[i][0] < 0.5:
            result = result + 1
    return result


# writer = tf.summary.FileWriter('log/graphlog', tf.get_default_graph())
# writer.close()
# Initialize the variables (i.e. assign their default value)
init = tf.global_variables_initializer()
train_batches = make_batches(read_data(), BATCH_SIZE)
test_batches = make_batches(read_data(path="./testset1"), BATCH_SIZE)
total_tests = len(test_batches) * BATCH_SIZE
with tf.Session() as sess:
    saver = tf.train.Saver()
    sess.run(init)

    for step in range(TRAIN_ITERS):
        logging.info("Step: " + str(step))
        for x1, x2, t, l1, l2, lt, y in train_batches:
            loss1, loss2, _, _ = sess.run([loss_op1, loss_op2, train_op1, train_op2], feed_dict={input1: x1, input2: x2, inputT: t, len1: l1, len2: l2, lent: lt, target: y})

        if step % 1 == 0:
            temp1 = []
            temp2 = []
            total_correct = 0
            for x1, x2, t, l1, l2, lt, y in test_batches:
                score, loss1, loss2 = sess.run([final_score, loss_op1, loss_op2], feed_dict={input1: x1, input2: x2, inputT: t, len1: l1, len2: l2, lent: lt, target: y})
                temp1.append(loss1)
                temp2.append(loss2)
                total_correct = total_correct + get_correct(score, y)
            logging.info("At the step %d, the avg loss is %f|%f, the accuracy is %f" % (step, np.mean(np.array(temp1)), np.mean(np.array(temp2)), float(total_correct)/total_tests))
    saver.save(sess, 'rnnmodel/adam/rnn', global_step=TRAIN_ITERS)
    logging.info("Optimization Finished!")
