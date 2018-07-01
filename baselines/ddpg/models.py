import tensorflow as tf
import tensorflow.contrib as tc

#HAS_SCOPE = {}
HAS_SCOPE = False

class Model(object):
    def __init__(self, name):
        self.name = name

    @property
    def vars(self):
        if self.name == 'critic' or self.name == 'actor':
            result = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope=self.name) + tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope='sharefirst')# + tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope=self.first_scope)
        else:
            result = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope=self.name)
        return result

    @property
    def trainable_vars(self):
        if self.name == 'critic' or self.name == 'actor':
            result = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name) + tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope='sharefirst')# + tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.first_scope)
        else:
            result = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)
        return result

    @property
    def perturbable_vars(self):
        return [var for var in self.trainable_vars if 'LayerNorm' not in var.name]


class Actor(Model):
    def __init__(self, nb_actions, name='actor', layer_norm=True):
        super(Actor, self).__init__(name=name)
        self.nb_actions = nb_actions
        self.layer_norm = layer_norm
        self.first_scope = 'general_scope'

    def __call__(self, obs, reuse=False, FS=False):
        global HAS_SCOPE
        '''with tf.variable_scope(self.first_scope) as scope:
            if self.first_scope in HAS_SCOPE:
                scope.reuse_variables()
            else:
                HAS_SCOPE[self.first_scope] = True

            x = obs
            x = tf.layers.dense(x, 64)
            if self.layer_norm:
                x = tc.layers.layer_norm(x, center=True, scale=True)
            x = tf.nn.relu(x)'''
        if FS:
            with tf.variable_scope('sharefirst') as scope:
                if HAS_SCOPE:
                    scope.reuse_variables()
                else:
                    HAS_SCOPE = True
                x = obs
                x = tf.layers.dense(x, 64)
                if self.layer_norm:
                    x = tc.layers.layer_norm(x, center=True, scale=True)
                x = tf.nn.relu(x)

            with tf.variable_scope(self.name) as scope:
                if reuse:
                    scope.reuse_variables()

                x = tf.layers.dense(x, 64)
                if self.layer_norm:
                    x = tc.layers.layer_norm(x, center=True, scale=True)
                x = tf.nn.relu(x)
                
                x = tf.layers.dense(x, self.nb_actions, kernel_initializer=tf.random_uniform_initializer(minval=-3e-3, maxval=3e-3))
                x = tf.nn.tanh(x)
        else:
            with tf.variable_scope(self.name) as scope:
                if reuse:
                    scope.reuse_variables()
                x = obs
                x = tf.layers.dense(x, 64)
                if self.layer_norm:
                    x = tc.layers.layer_norm(x, center=True, scale=True)
                x = tf.nn.relu(x)

            
        # with tf.variable_scope(self.name) as scope:
        #     if reuse:
        #         scope.reuse_variables()

                x = tf.layers.dense(x, 64)
                if self.layer_norm:
                    x = tc.layers.layer_norm(x, center=True, scale=True)
                x = tf.nn.relu(x)
                
                x = tf.layers.dense(x, self.nb_actions, kernel_initializer=tf.random_uniform_initializer(minval=-3e-3, maxval=3e-3))
                x = tf.nn.tanh(x)

        return x


class Critic(Model):
    def __init__(self, name='critic', layer_norm=True):
        super(Critic, self).__init__(name=name)
        self.layer_norm = layer_norm
        self.first_scope = 'general_scope'

    def __call__(self, obs, action, reuse=False):
        global HAS_SCOPE
        '''with tf.variable_scope(self.first_scope) as scope:
            if self.first_scope in HAS_SCOPE:
                scope.reuse_variables()
            else:
                HAS_SCOPE[self.first_scope] = True

            x = obs
            x = tf.layers.dense(x, 64)
            if self.layer_norm:
                x = tc.layers.layer_norm(x, center=True, scale=True)
            x = tf.nn.relu(x)'''
        if FS:
            with tf.variable_scope('sharefirst') as scope:
                if HAS_SCOPE:
                    scope.reuse_variables()
                else:
                    HAS_SCOPE = True
                x = obs
                x = tf.layers.dense(x, 64)
                if self.layer_norm:
                    x = tc.layers.layer_norm(x, center=True, scale=True)
                x = tf.nn.relu(x)

            with tf.variable_scope(self.name) as scope:
                if reuse:
                    scope.reuse_variables()

                x = tf.concat([x, action], axis=-1)
                x = tf.layers.dense(x, 64)
                if self.layer_norm:
                    x = tc.layers.layer_norm(x, center=True, scale=True)
                x = tf.nn.relu(x)

                x = tf.layers.dense(x, 1, kernel_initializer=tf.random_uniform_initializer(minval=-3e-3, maxval=3e-3))

        else:
            with tf.variable_scope(self.name) as scope:
                if reuse:
                    scope.reuse_variables()
                x = obs
                x = tf.layers.dense(x, 64)
                if self.layer_norm:
                    x = tc.layers.layer_norm(x, center=True, scale=True)
                x = tf.nn.relu(x)


        # with tf.variable_scope(self.name) as scope:
        #     if reuse:
        #         scope.reuse_variables()

                x = tf.concat([x, action], axis=-1)
                x = tf.layers.dense(x, 64)
                if self.layer_norm:
                    x = tc.layers.layer_norm(x, center=True, scale=True)
                x = tf.nn.relu(x)

                x = tf.layers.dense(x, 1, kernel_initializer=tf.random_uniform_initializer(minval=-3e-3, maxval=3e-3))
        return x

    @property
    def output_vars(self):
        output_vars = [var for var in self.trainable_vars if 'output' in var.name]
        return output_vars
