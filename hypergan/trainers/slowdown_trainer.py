import tensorflow as tf
from hypergan.util.globals import *
from .common import *
TINY = 1e-12

def initialize(config, d_vars, g_vars):
    d_loss = gan.graph.d_loss
    g_loss = gan.graph.g_loss
    g_lr = np.float32(config['trainer.adam.generator.lr'])
    g_beta1 = np.float32(config['trainer.adam.generator.beta1'])
    g_beta2 = np.float32(config['trainer.adam.generator.beta2'])
    g_epsilon = np.float32(config['trainer.adam.generator.epsilon'])
    d_lr = np.float32(config['trainer.rmsprop.discriminator.lr'])
    set_tensor("lr_value", d_lr)
    d_lr = tf.get_variable('lr', [], trainable=False, initializer=tf.constant_initializer(d_lr,dtype=config['dtype']),dtype=config['dtype'])
    set_tensor("lr", d_lr)

    #g_optimizer = tf.train.AdamOptimizer(g_lr, beta1=g_beta1, beta2=g_beta2, epsilon=g_epsilon).minimize(g_loss, var_list=g_vars)
    #d_optimizer = tf.train.AdamOptimizer(d_lr).minimize(d_loss, var_list=d_vars)
    g_optimizer = capped_optimizer(tf.train.AdamOptimizer,g_lr, g_loss, g_vars)
    d_optimizer = tf.train.RMSPropOptimizer(d_lr).minimize(d_loss, var_list=d_vars)
    return g_optimizer, d_optimizer

iteration = 0
def train(gan):
    sess = gan.sess
    config = gan.config
    x_t = gan.graph.x
    g_t = gan.graph.g
    g_loss = gan.graph.g_loss_sig
    d_loss = gan.graph.d_loss
    d_fake_loss = gan.graph.d_fake_loss
    d_real_loss = gan.graph.d_real_loss
    g_optimizer = gan.graph.g_optimizer
    d_optimizer = gan.graph.d_optimizer
    d_class_loss = gan.graph.d_class_loss
    g_class_loss = gan.graph.g_class_loss
    lr_value = gan.graph.lr_value
    lr = gan.graph.lr

    _, d_cost = sess.run([d_optimizer, d_loss], feed_dict={lr:lr_value})
    _, g_cost,d_fake,d_real,d_class = sess.run([g_optimizer, g_loss, d_fake_loss, d_real_loss, d_class_loss])
    print("%2d: d_lr %.1e g cost %.2f d_fake %.2f d_real %.2f d_class %.2f" % (iteration, lr_value, g_cost,d_fake, d_real, d_class ))

    slowdown = 1
    bounds_max = config['trainer.slowdown.discriminator.d_fake_max']
    bounds_min = config['trainer.slowdown.discriminator.d_fake_min']
    bounds_slow = config['trainer.slowdown.discriminator.slowdown']
    max_lr = config['trainer.rmsprop.discriminator.lr']
    if(d_fake < bounds_min):
        slowdown = 1/(bounds_slow)
    elif(d_fake > bounds_max):
        slowdown = 1
    else:
        percent = 1 - (d_fake - bounds_min)/(bounds_max-bounds_min)
        slowdown = 1/(percent * bounds_slow + TINY)
        if(slowdown > 1):
            slowdown=1
    new_lr = max_lr*slowdown
    set_tensor("lr_value", new_lr)

    global iteration
    iteration+=1

    return d_cost, g_cost


