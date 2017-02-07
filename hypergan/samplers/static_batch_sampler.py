
from hypergan.util.ops import *
from hypergan.util.globals import *

from hypergan.samplers.common import *

#mask_noise = None
z = None
y = None
def sample(gan, sample_file):
    sess = gan.sess
    config = gan.config
    global z, y
    generator = gan.graph.g[0]
    y_t = gan.graph.y
    z_t = gan.graph.z

    x = np.linspace(0,1, 4)

    if z is None:
        z = sess.run(z_t)
        y = sess.run(y_t)


    g=tf.get_default_graph()
    with g.as_default():
        tf.set_random_seed(1)
        sample = sess.run(generator, feed_dict={z_t: z, y_t: y})
        #plot(self.config, sample, sample_file)
        stacks = [np.hstack(sample[x*8:x*8+8]) for x in range(4)]
        plot(config, np.vstack(stacks), sample_file)

    return [{'image':sample_file, 'label':'grid'}]
