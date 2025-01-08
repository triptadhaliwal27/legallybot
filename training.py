import nltk
# import ssl

# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context

# nltk.download()

import random
import json
import pickle
import numpy as np

from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

import tensorflow as tf
Sequential = tf.keras.models.Sequential
Dense = tf.keras.layers.Dense
Activation = tf.keras.layers.Activation
Dropout = tf.keras.layers.Dropout
SGD = tf.keras.optimizers.SGD

def train_model(intents_file='intents.json', model_file='chatbot_model.keras'):
    lemmatizer = WordNetLemmatizer()
    intents = json.loads(open(intents_file).read())

    words = []
    classes = [] #each class represents a single indent
    documents = [] #will contain a list of 
    ignore_letters = ['?', '!', '.', ',', '-', '@', '#', '$', '%', '&', '*', '(', ')', ':', ';', '"', "'"]
    stop_words = set(stopwords.words('english'))

    for intent in intents['intents']:
        for pattern in intent['patterns']:
            word_list = nltk.word_tokenize(pattern) #splits the text into indv tokens
            word_list = [lemmatizer.lemmatize(word.lower()) for word in word_list if word not in ignore_letters] #lemmatize and remove special char
            words.extend(word_list)
            documents.append((word_list, intent['tag'])) #to document that the word list of tokens is associated with that intent (denoted by the tag)
            if intent['tag'] not in classes:
                classes.append(intent['tag'])


    new_words = []
    for word in words:
        if word not in ignore_letters:
            new_words.append(lemmatizer.lemmatize(word.lower()))

    words = new_words
    words = sorted(set(words))

    classes = sorted(set(classes))

    pickle.dump(words, open('words.pkl', 'wb'))
    pickle.dump(classes, open('classes.pkl', 'wb'))

    training = []
    output_empty = [0] * len(classes)

    for document in documents:
        bag = [] 
        word_patterns = document[0]
        word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]
        for word in words:
            if word in word_patterns:
                bag.append(1)
            else:
                bag.append(0)
        output_row = list(output_empty) #copying output empty
        output_row[classes.index(document[1])] = 1 #sets the entry for the corresponding intent (current interation) to 1, indication
        training.append([bag, output_row]) #adding a tuple of the bag with the one-hot encoded label

    for i, (bag, output_row) in enumerate(training):
        if len(bag) != len(words):  # Check if the bag length is consistent
            print(f"Bag length mismatch at index {i}: Expected {len(words)}, Got {len(bag)}")
        if len(output_row) != len(classes):  # Check if the one-hot vector length is consistent
            print(f"Output row mismatch at index {i}: Expected {len(classes)}, Got {len(output_row)}")
            
    random.shuffle(training) #must shuffle the model to prevent creating biases
    training = np.array(training, dtype=object) #numPy array where basically its a 2D array, where each row has two elements (first is bag, second is the one-hot encoded list)

    train_x = list(training[:, 0]) #slices array to extract first column (list of all of the bags)
    train_y = list(training[:, 1]) #slice, extracts list of output row vectors

    #basically input is a bag of words and the output is the intent that the model thinks it is; 
    #as we add intents, need to add more layers and neurons
    model = Sequential()
    model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))# input shape set to be equal to number of bags (how may features in the input sample_)
    model.add(Dropout(0.5)) #drop out 50% of the neurons to generalize the model
    model.add(Dense(64, activation='relu')) #add another fully connected layer, 64 neurons (reduce neuron to learn hierarchy) 
    model.add(Dropout(0.5)) #regularize
    model.add(Dense(len(train_y[0]), activation='softmax')) #this new layer will match the number of output row vectors (the one-hot encoded list)

    sgd = SGD(learning_rate=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
    hist = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1) #trains the model for 200 complete passes
    model.save(model_file, hist)
    print(f"Model trained and saved as {model_file}")
    return model;

if __name__ == "__main__":
    train_model();