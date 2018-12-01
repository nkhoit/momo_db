from keras.applications.resnet50 import ResNet50
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input, decode_predictions
from keras.models import load_model
import numpy
import json
import os
import PIL
from PIL import Image

RATIO = 0.75
NUM_EPOCHS = 200
BATCH_SIZE = 50

numpy.random.seed(12345)


#turns a momobot url into a filename
def getFilenameFromUrl(url):
    return url[url.rindex('/')+1:]

def ignoreFiles():
    content = []
    with open('ignore.txt') as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content] 
    return list(map(lambda x : getFilenameFromUrl(x), content))


# returns (x_data, y_data). Returns all data - segment it into train / test afterwards
def loadData():
    #momo is label 0, mimi is label 1
    labeldirs = ["compressedmomo", "compressedmimi"]
    x_data = []
    y_data = []
    for i in range(2):
        d = labeldirs[i]
        allfiles = os.listdir(d)
        allfiles = list(set(allfiles).difference(ignoreFiles()))
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

#returns (model, history)
def buildModel():
    # Now, we run the classifier!
    model = ResNet50(include_top=True, weights=None, classes=2)

    model.compile(loss='mean_squared_error', optimizer='sgd')

    history = model.fit(x_train, y_train,
            epochs=NUM_EPOCHS,
            batch_size=BATCH_SIZE,
            shuffle=True,
            validation_data=(x_test, y_test))
    return (model, history)

#returns model
def loadModel():
    return load_model('200epoch.h5')

# returns (true_positive, false_positive, true_negative, false_negative)
def calculate_accuracy(res_labels, res_labels_true):
    true_negative = 0
    true_positive = 0
    false_negative = 0
    false_positive = 0
    for i in range(0,len(res_labels)):
        if res_labels[i] == 1 and res_labels_true[i] == True:
            true_positive = true_positive + 1
        if res_labels[i] == 1 and res_labels_true[i] == False:
            false_positive = false_positive + 1
        if res_labels[i] == 0 and res_labels_true[i] == True:
            true_negative = true_negative + 1
        if res_labels[i] == 0 and res_labels_true[i] == False:
            false_negative = false_negative + 1
    return (true_positive, false_positive, true_negative, false_negative)

#returns (sensitivity, specificity, accuracy)
def calculate_accuracy_on_x_test(model, x_test):
    res = model.predict(x_test)
    l = len(x_test)
    res_labels = list(map(lambda x : 0 if x[0] > x[1] else 1,res))
    res_correct = [0]*l
    for i in range(0,l):
        is_correct = res_labels[i] == y_test[i][1]
        res_correct[i] = is_correct
    (true_positive, false_positive, true_negative, false_negative) = calculate_accuracy(res_labels, res_correct)
    sensitivity = true_positive / (true_positive + false_negative)
    specificity = true_negative / (true_negative + false_positive)
    accuracy = (true_positive + true_negative) / (true_positive + true_negative + false_positive + false_negative)
    return (sensitivity, specificity, accuracy)

(x_data, y_data) = loadData()
(x_train, y_train, x_test, y_test) = train_and_test(x_data, y_data)

model = loadModel()
# (model, history) = buildModel()

(sensitivity, specificity, accuracy) = calculate_accuracy_on_x_test(model, x_test)
print("sensitivity: %s, specificity: %s, accuracy: %s" % (sensitivity, specificity, accuracy))