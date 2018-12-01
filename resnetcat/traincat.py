from keras.applications.resnet50 import ResNet50
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy
import json
import os
import PIL
from PIL import Image

RATIO = 0.75
NUM_EPOCHS = 200
BATCH_SIZE = 50

numpy.random.seed(12345)

# returns (x_data, y_data). Returns all data - segment it into train / test afterwards
def loadData():
    #momo is label 0, mimi is label 1
    labeldirs = ["compressedmomo", "compressedmimi"]
    x_data = []
    y_data = []
    for i in range(2):
        d = labeldirs[i]
        allfiles = os.listdir(d)
        for filename in allfiles:
            filedir = d + "/" + filename
            im = Image.open(filedir)
            pix = numpy.array(im)
            x_data.append(pix)
            y_data.append(i)
    x_data = numpy.asarray(x_data)
    y_data = numpy.asarray(y_data)
    return (x_data, y_data)

#takes (x_data, y_data) and returns (x_train, y_train, x_test, y_test)
def train_and_test(x_data, y_data):
    x_train = numpy.empty((0,224,224,3))
    y_train = numpy.empty((0))
    x_test = numpy.empty((0,224,224,3))
    y_test = numpy.empty((0))
    for i in range(2):
        indices_label = numpy.nonzero(y_data == i)[0]
        num_train_label = int(0.7 * len(indices_label))
        indices_label_train = numpy.random.choice(indices_label, size=num_train_label, replace=False)
        indices_label_test = numpy.setdiff1d(indices_label, indices_label_train)
        data_label_train = x_data[indices_label_train]
        data_label_test = x_data[indices_label_test]
        x_train = numpy.concatenate((x_train, data_label_train))
        y_train = numpy.concatenate((y_train, numpy.array([i]*len(data_label_train))))
        x_test = numpy.concatenate((x_test, data_label_test))
        y_test = numpy.concatenate((y_test, numpy.array([i]*len(data_label_test))))
    #RESHAPE the y data to fit as an incidence matrix instead of array of scalars
    y_train = numpy.array(list(map(lambda z : (0,1) if z else (1,0), y_train)))
    y_test = numpy.array(list(map(lambda z : (0,1) if z else (1,0), y_test)))
    return (x_train, y_train, x_test, y_test)

(x_data, y_data) = loadData()
(x_train, y_train, x_test, y_test) = train_and_test(x_data, y_data)

# Now, we run the classifier!
model = ResNet50(include_top=True, weights=None, classes=2)

model.compile(loss='mean_squared_error', optimizer='sgd')

history = model.fit(x_train, y_train,
          epochs=NUM_EPOCHS,
          batch_size=BATCH_SIZE,
          shuffle=True,
          validation_data=(x_test, y_test))
