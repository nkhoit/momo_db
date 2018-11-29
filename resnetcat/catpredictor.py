from keras.applications.resnet50 import ResNet50
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np
import json
import os

model = ResNet50(weights='imagenet')



# e.g. classify everything in the compressedMomo folder and leave a compressedMomoLabel.txt file
def classifyCategory(category):
    categories = {}
    os.stat(category) # will throw if the folder doesn't exist
    # We're going to naively load each image as 224 x 224
    img_prefix = category + '/'
    files = os.listdir(category)
    for fileName in files:
        img_path = img_prefix + fileName
        img = image.load_img(img_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        preds = model.predict(x)
        categories[fileName] = (decode_predictions(preds)[0][0][1])
    with open(img_prefix + category + '.json', 'w') as file:
        file.write(json.dumps(categories)) # use `json.loads` to do the reverse 

classifyCategory('momo')