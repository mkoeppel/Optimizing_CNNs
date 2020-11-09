#!/usr/bin/env python
# coding: utf-8


import logging
import random
import numpy as np
from keras.models import Sequential
from keras.layers import InputLayer, Dense, Activation, Dropout, Conv2D, MaxPooling2D, Flatten, ZeroPadding2D
from keras.datasets import cifar10
from keras.utils import to_categorical



# Setup logging.
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.DEBUG,
    filename='log.txt'
)

dataset = cifar10
no_classes = 10
batch_size = 300
validation_split = 0.2
epochs = 10
threshold = 0.9
population = 20
generations = 20
input_shape = (32, 32, 3)

padding = ZeroPadding2D()


def prepare_data(dataset):
    """
    loads a given dataset, splits into X (images) and y (labels),
    selects only the first 10000 images, splits into train and test-set

    Params:
        input: a keras dataset
        output: x_train, y_train, x_test, y_test
    """
    (train_images, train_labels), (test_images, test_labels) = dataset.load_data()
    train_images = train_images[:10000] / 255
    test_images = test_images[:10000] / 255
    train_labels = to_categorical(train_labels, 10)[:10000]
    test_labels = to_categorical(test_labels, 10)[:10000]

    return (train_images, train_labels), (test_images, test_labels)



class Network():
    def __init__(self):
        """
        parameters to be optimized:
            2d-layers: units, kernel, stride, padding, dropout
            Dense-layers: units, dropout
        """
        self._layer2D_1 = []
        self._layer2D_2 = []
        self._layerDense_1 = []
        self._layerDense_2 = []

        self._layers2D = [self._layer2D_1, self._layer2D_2]
        self._layersDense = [self._layerDense_1, self._layerDense_2]

        for layer in self._layers2D:
            units = random.choice([16,32,64,128])
            kernel = random.randint(3,5)
            stride = random.randint(1,3)
            paddding_type = random.choice(['same', 'valid'])
            dropout = random.randint(1,3)*0.1
            layer.extend([units, kernel, stride, paddding_type, dropout])

        for layer in self._layersDense:
            units = random.choice([32,64,128])
            dropout = random.randint(2,5)*0.1
            layer.extend([units, dropout])

        self._optimizer = random.choice(['rmsprop', 'adam', 'sgd', 'adagrad'])
        self._epochs = random.randint(10,15)
        """
        fixed parameters:
        """
        self._accuracy = 0
        self._loss = 'categorical_crossentropy'
        self._output_activation = 'softmax'
        self._genetic_function = 0

    def get_parameters(self):
        parameters = {

          'layer2D_1' : self._layer2D_1,
          'layer2D_2' : self._layer2D_2,
          'layerDense_1' : self._layerDense_1,
          'layerDense_2' : self._layerDense_2,
          'loss' : self._loss,
          'hidden_activation' : self._hidden_activation,
          'output_activation' : self._output_activation,
          'optimizer' : self._optimizer,
          'epochs' : self._epochs,
          }
        return parameters



def create_model(network):
    """
    generates the actual model

    Params:
      input: dictionary of parametes
      output: model containing a Pooling and a flattening layer + output for no_classes
    """

    parameters = network.get_parameters()

    layer2D_1 = parameters['layer2D_1']
    layer2D_2 = parameters['layer2D_2']
    layerDense_1 = parameters['layerDense_1']
    layerDense_2 = parameters['layerDense_2']

    loss = parameters['loss']
    hidden_activation = parameters['hidden_activation']
    output_activation = parameters['output_activation']
    optimizer = parameters['optimizer']

    model = Sequential()
    model.add(InputLayer(input_shape = input_shape))
    model.add(Conv2D(layer2D_1[0], kernel_size= layer2D_1[1], strides = layer2D_1[2], padding = layer2D_1[3], activation = hidden_activation))
    model.add(Dropout(layer2D_1[4]))
    model.add(Conv2D(layer2D_2[0], kernel_size= layer2D_2[1], strides = layer2D_2[2], padding = layer2D_2[3], activation = hidden_activation))
    model.add(Dropout(layer2D_2[4]))
    model.add(MaxPooling2D(pool_size=(2,2), strides = (2,2)))
    model.add(Flatten())
    model.add(Dense(layerDense_1[0], activation = hidden_activation))
    model.add(Dropout(layerDense_1[1]))
    model.add(Dense(layerDense_2[0], activation = hidden_activation))
    model.add(Dropout(layerDense_2[1]))
    model.add(Dense(no_classes, activation = output_activation))
    model.compile(loss = loss, optimizer = optimizer, metrics = ['accuracy'])
    model.fit(train_images, train_labels, batch_size=batch_size, epochs=epochs, verbose=0)

    return model



def init_networks(population):
    return [Network() for _ in range(population)]

def assess_networks(networks):
    for network in networks:
        try:
            model = create_model(network)
            accuracy = model.evaluate(test_images, test_labels)[1]
            network._accuracy = accuracy
            print('Accuracy: {}'.format(network._accuracy))

        except:
            network._accuracy = 0
            print ('Build failed.')
    return networks

def select_best_networks(networks):
    networks = sorted(networks, key=lambda network: network._accuracy, reverse=True)
    networks = networks[:int(0.2 * len(networks))]

    return networks


def rearrange_networks(networks):
    offsprings = []
    for _ in range(int((population - len(networks)) / 2)):
        parent1 = random.choice(networks)
        parent2 = random.choice(networks)
        offspring1 = Network()
        offspring2 = Network()

        # select mutator type
        genetic_function = random.randint(1,2)
        if genetic_function == 1:
            offspring1._genetic_function == 1
            offspring2._genetic_function == 1
            # rearrage layers
            offspring1._layer2D_1, offspring1._layer2D_2 = parent1._layer2D_1, parent2._layer2D_2
            offspring2._layer2D_1, offspring2._layer2D_2 = parent2._layer2D_1, parent1._layer2D_2
            offspring1._layerDense_1, offspring1._layerDense_2 = parent1._layerDense_1, parent2._layerDense_2
            offspring1._layerDense_3, offspring1._layerDense_4 = parent1._layerDense_3, parent2._layerDense_4
            offspring2._layerDense_1, offspring2._layerDense_2 = parent2._layerDense_1, parent1._layerDense_2
            offspring2._layerDense_3, offspring2._layerDense_4 = parent2._layerDense_3, parent1._layerDense_4

        else:
            offspring1._genetic_function == 2
            offspring2._genetic_function == 2
            #exchange parameters from the first with those of the second layer and those from the third with the forth
            for layer in offspring1._layers2D:
                layer[0] = random.choice([parent1._layer2D_1[0], parent1._layer2D_2[0], parent2._layer2D_1[0], parent2._layer2D_2[0]])
                layer[1] = random.choice([parent1._layer2D_1[1], parent1._layer2D_2[1], parent2._layer2D_1[1], parent2._layer2D_2[1]])
                layer[2] = random.choice([parent1._layer2D_1[2], parent1._layer2D_2[2], parent2._layer2D_1[2], parent2._layer2D_2[2]])
                layer[4] = random.choice([parent1._layer2D_1[4], parent1._layer2D_2[4], parent2._layer2D_1[4], parent2._layer2D_2[4]])

            for layer in offspring2._layers2D:
                layer[0] = random.choice([parent1._layer2D_1[0], parent1._layer2D_2[0], parent2._layer2D_1[0], parent2._layer2D_2[0]])
                layer[1] = random.choice([parent1._layer2D_1[1], parent1._layer2D_2[1], parent2._layer2D_1[1], parent2._layer2D_2[1]])
                layer[2] = random.choice([parent1._layer2D_1[2], parent1._layer2D_2[2], parent2._layer2D_1[2], parent2._layer2D_2[2]])
                layer[4] = random.choice([parent1._layer2D_1[4], parent1._layer2D_2[4], parent2._layer2D_1[4], parent2._layer2D_2[4]])

            for layer in offspring1._layersDense:
                layer[0] = random.choice([parent1.layerDense_1[0], parent1.layerDense_2[0], parent1.layerDense_3[0], parent1.layerDense_4[0],
                parent2.layerDense_1[0], parent2.layerDense_2[0], parent2.layerDense_3[0], parent2.layerDense_4[0]])
                layer[1] = random.choice([parent1.layerDense_1[1], parent1.layerDense_2[1], parent1.layerDense_3[1], parent1.layerDense_4[1],
                parent2.layerDense_1[1], parent2.layerDense_2[1], parent2.layerDense_3[1], parent2.layerDense_4[1]])
                layer[2] = random.choice([parent1.layerDense_1[2], parent1.layerDense_2[2], parent1.layerDense_3[2], parent1.layerDense_4[2],
                parent2.layerDense_1[2], parent2.layerDense_2[2], parent2.layerDense_3[2], parent2.layerDense_4[2]])
            for layer in offspring2._layersDense:
                layer[0] = random.choice([parent1.layerDense_1[0], parent1.layerDense_2[0], parent1.layerDense_3[0], parent1.layerDense_4[0],
                parent2.layerDense_1[0], parent2.layerDense_2[0], parent2.layerDense_3[0], parent2.layerDense_4[0]])
                layer[1] = random.choice([parent1.layerDense_1[1], parent1.layerDense_2[1], parent1.layerDense_3[1], parent1.layerDense_4[1],
                parent2.layerDense_1[1], parent2.layerDense_2[1], parent2.layerDense_3[1], parent2.layerDense_4[1]])
                layer[2] = random.choice([parent1.layerDense_1[2], parent1.layerDense_2[2], parent1.layerDense_3[2], parent1.layerDense_4[2],
                parent2.layerDense_1[2], parent2.layerDense_2[2], parent2.layerDense_3[2], parent2.layerDense_4[2]])


        offsprings.append(offspring1)
        offsprings.append(offspring2)

    networks.extend(offsprings)
    return networks



def mutate_network(networks):
    for network in networks:
        for layer in network._layers2D:
            if np.random.uniform(0, 1) <= 0.1:
                # mutate units
                layer[0] += np.random.randint(-2,4)*16
            if np.random.uniform(0, 1) <= 0.1:
                # mutate dropout
                layer[4] += np.random.randint(-2,2)*0.1
            if np.random.uniform(0, 1) <= 0.1:
                # mutate kernel_size
                layer[1] += np.random.randint(-1,1)
            if np.random.uniform(0, 1) <= 0.1:
                # mutate stride_size
                layer[2] += np.random.randint(-1,1)
        for layer in network._layersDense:
            if np.random.uniform(0, 1) <= 0.1:
                # mutate units
                layer[0] += np.random.randint(-2,4)*16
            if np.random.uniform(0, 1) <= 0.1:
                # mutate dropout
                layer[1] += np.random.randint(-2,2)*0.1

        if np.random.uniform(0, 1) <= 0.1:
            network._epochs += random.randint(-2,4)

    return networks



(train_images, train_labels), (test_images, test_labels) = prepare_data(dataset)

def optimizer():
    networks = init_networks(population)
    networks_accuracy = []
    best_network_accuracy = 0
    best_network = 0
    for generation in range(generations):
        print(f'Generation number {generation}')
        total_accuracy = 0
        networks = assess_networks(networks)
        for network in networks:
          total_accuracy += network._accuracy

        networks = select_best_networks(networks)
        networks = rearrange_networks(networks)
        networks = mutate_network(networks)

        average_accuracy = total_accuracy/len(networks)
        networks_accuracy.append(average_accuracy)

        for network in networks:
          if network._accuracy > best_network_accuracy:
              best_network_accuracy = network._accuracy
              best_network = network
              logging.info(best_network.__dict__.items())
              print('current best accuracy: ' +str(best_network_accuracy))

          if network._accuracy > threshold:
              print ('Threshold met')
              print (network.__dict__.items())
              print ('Best accuracy: {}'.format(network._accuracy))
              logging.info(network.__dict__.items())
              exit(0)
        # Print out the average accuracy each generation.
        logging.info("Generation average: %.2f%%" % (average_accuracy * 100))
        logging.info('-'*80)
        logging.info("***Doing generation %d of %d***" %
          (generation + 1, generations))


    return networks, networks_accuracy, best_network
    logging.info("***Evolving %d generations with population %d***" %
                 (generations, population))

if __name__ == '__main__':
  networks, networks_accuracy, best_network = optimizer()