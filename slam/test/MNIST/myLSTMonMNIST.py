import tensorflow as tf
from tensorflow.models.rnn import rnn, rnn_cell

import numpy as np
import input_data
import lstm_model
import cnn_model

# configuration
#                        O * W + b -> 10 labels for each image, O[? 28], W[28 10], B[10]
#                       ^ (O: output 28 vec from 28 vec input)
#                       |
#      +-+  +-+       +--+
#      |1|->|2|-> ... |28| time_step_size = 28
#      +-+  +-+       +--+
#       ^    ^    ...  ^
#       |    |         |
# img1:[28] [28]  ... [28]
# img2:[28] [28]  ... [28]
# img3:[28] [28]  ... [28]
# ...
# img128 or img256 (batch_size or test_size 256)
#      each input size = input_vec_size=lstm_size=28

# configuration variables
lstm_layers = 1
#input_vec_size = lstm_size = 28
input_vec_size = 28
time_step_size = 28
lstm_size = 28

batch_size = 128
test_size = 256

def init_weights(shape):
    return tf.Variable(tf.random_normal(shape, stddev=0.01))


def model(X, lstm_size, lstm_layers):
    '''

    # X, input shape: (batch_size, input_vec_size, time_step_size)
    XT = tf.transpose(X, [1, 0, 2])  # permute time_step_size and batch_size
    # XT shape: (input_vec_size, batch_size, time_step_size)
    XR = tf.reshape(XT, [-1, input_vec_size]) # each row has input for each lstm cell (lstm_size)
    # XR shape: (input vec_size, batch_size)
    X_split = tf.split(0, time_step_size, XR) # split them to time_step_size (28 arrays)
    # Each array shape: (batch_size, input_vec_size)
    '''

    graph = lstm_model.LSTMmodel(X, time_step_size, input_vec_size, 100, 2, 10)
    return graph.build_graph()

mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
trX, trY, teX, teY = mnist.train.images, mnist.train.labels, mnist.test.images, mnist.test.labels
trX = trX.reshape(-1, 28, 28)
teX = teX.reshape(-1, 28, 28)


X = tf.placeholder("float", [None, 28, 28])
Y = tf.placeholder("float", [None, 10])

print X.get_shape()[1]
#py_x, state_size = model(X, W, B, init_state, lstm_size, lstm_layers)
py_x, state_size, init_state = model(X, batch_size, lstm_layers)
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(py_x, Y))
train_op = tf.train.RMSPropOptimizer(0.001, 0.9).minimize(cost)
predict_op = tf.argmax(py_x, 1)

# Launch the graph in a session
with tf.Session() as sess:
    # you need to initialize all variables
    tf.initialize_all_variables().run()

    for i in range(100):
        for start, end in zip(range(0, len(trX), batch_size), range(batch_size, len(trX), batch_size)):
            sess.run(train_op, feed_dict={X: trX[start:end], Y: trY[start:end],
                                          init_state: np.zeros((batch_size, state_size))})

        test_indices = np.arange(len(teX))  # Get A Test Batch
        np.random.shuffle(test_indices)
        test_indices = test_indices[0:test_size]

        print(i, np.mean(np.argmax(teY[test_indices], axis=1) ==
                         sess.run(predict_op, feed_dict={X: teX[test_indices],
                                                         Y: teY[test_indices],
                                                         init_state: np.zeros((test_size, state_size))})))