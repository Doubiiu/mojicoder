import tensorflow as tf
import numpy as np

#data = np.load('../NR-ER/NR-ER-train/names_onehots.npy')
#data = data.item()

data = np.load('../NR-ER/NR-ER-train/names_onehots.npy', allow_pickle = True)
m = np.atleast_1d(data)
dictionary = dict(m[0])
onehotArr = dictionary['onehots']
dictlength = len(onehotArr[0]) #72， inputs
datalength = len(onehotArr)#

onelength = len(onehotArr[0][0]) #300，
batch = 100
size = 100

labels = np.genfromtxt('../NR-ER/NR-ER-train/names_labels.csv',delimiter=',',dtype=None)
label = []
for m in range(0, datalength):
    label.append([])
    label[m].append(labels[m][1])
    #print(label[m])
    if label[m] == [0]:
        #print(000)
        label[m] = [1, 0]
    else:
        label[m] = [0, 1]


def compute_accuracy(v_xs,v_ys,size):
    global prediction
    v_xs = np.reshape(v_xs, (size,dictlength*onelength))
    v_ys = np.reshape(v_ys, (size,2))
    #batch_ys = np.reshape(batch_ys, (90,2))
    y_pre = sess.run(prediction, feed_dict={xs:v_xs,keep_prob:1})
    correct_prediction = tf.equal(tf.argmax(y_pre,1),tf.argmax(v_ys,1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction,tf.float32))
    result = sess.run(accuracy, feed_dict={xs:v_xs,ys:v_ys,keep_prob:1})

    return result

def next_batch(train_data, train_target, batch_size):

    index = [ i for i in range(0,len(train_target)) ]
    np.random.shuffle(index);

    batch_data = [];
    batch_target = [];

    for i in range(0,batch_size):
        batch_data.append(train_data[index[i]]);
        batch_target.append(train_target[index[i]])
    return batch_data, batch_target



def weight_variable(shape):
    initial = tf.truncated_normal(shape,stddev=0.1)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.0,shape=shape)
    return tf.Variable(initial)

def conv2d(x,W):
    #strides [1,x_movement,y_movement,1]
    #Must have strides[0] = strides[3] =1
    return tf.nn.conv2d(x,W,strides=[1,1,1,1],padding='SAME')

def max_pool_2x2(x):
    #strides [1,x_movement,y_movement,1]
    return tf.nn.max_pool(x,ksize=[1,2,2,1],strides=[1,2,2,1],padding='SAME')

#tf.reset_default_graph()
#define placeholder for inouts to network
xs = tf.placeholder(tf.float32,[None,dictlength*onelength])#28*28 402x72
ys = tf.placeholder(tf.float32,[None,2])

keep_prob = tf.placeholder(tf.float32)
x_image = tf.reshape(xs,[-1,72,398,1])#1 b&w

#print(x_image.shape)#[n_samples,28,28,1]

## conv1 layer ##
W_conv1 = weight_variable([19,19,1,32]) #patch 5x5, in size 1, out size 32
b_conv1 = bias_variable([32])
h_conv1 = tf.nn.relu(conv2d(x_image,W_conv1)+b_conv1)
h_pool1 = max_pool_2x2(h_conv1)

## conv2 layer ##
W_conv2 = weight_variable([19,19,32,64]) #patch 5x5, in size 32, out size 64
b_conv2 = bias_variable([64])
h_conv2 = tf.nn.relu(conv2d(h_pool1,W_conv2)+b_conv2) #14x14x64
h_pool2 = max_pool_2x2(h_conv2)  #7x7x64

## func1 layer ##
W_fc1 = weight_variable([18*100*64,2048])
b_fc1 = bias_variable([2048])
h_pool2_flat = tf.reshape(h_pool2,[-1,18*100*64])
h_fc1 = tf.nn.sigmoid(tf.matmul(h_pool2_flat,W_fc1)+b_fc1)
h_fc1_drop = tf.nn.dropout(h_fc1,keep_prob)

## func2 layer ##
W_fc2 = weight_variable([2048,2])
b_fc2 = bias_variable([2])
prediction = tf.nn.softmax(tf.matmul(h_fc1_drop,W_fc2)+b_fc2)

#the error between prediction and real data
cross_entropy = tf.reduce_mean(-tf.reduce_sum(ys * tf.log(prediction+ 1e-10),reduction_indices=[1]))#loss
train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)

sess = tf.Session()
init = tf.global_variables_initializer()
sess.run(init)
#merged = tf.summary.merge_all()

for i in range(10):

    batch_xs,batch_ys = next_batch(onehotArr,label,batch)
    batch_xs = np.reshape(batch_xs, (batch,dictlength*onelength))
    batch_ys = np.reshape(batch_ys, (batch,2))
    #v_xs = np.reshape(onehotArr[:size], (size,dictlength*onelength))
    #v_ys = np.reshape(label[:size], (size,2))
    sess.run(train_step,feed_dict={xs:batch_xs,ys:batch_ys,keep_prob:1})#0.5 change to 1
    if i % 5 == 0:
        print(compute_accuracy(onehotArr[:size],label[:size],size))

saver = tf.train.Saver()
saver.save(sess,'./my_model',global_step=1)
