def p1():
    lab_1_code = ''' 

import numpy as np
import tensorflow as tf


X_OR = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=np.float32)
y_OR = np.array([[0], [1], [1], [1]], dtype=np.float32)
X_XOR = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=np.float32)
y_XOR = np.array([[0], [1], [1], [0]], dtype=np.float32)

def train_perceptron(X, y, epochs=100, learning_rate=0.1):
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(1, activation='sigmoid', input_shape=(2,))
    ])
    model.compile(optimizer=tf.keras.optimizers.SGD(learning_rate=learning_rate),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
    model.fit(X, y, epochs=epochs, verbose=0)
    return model


model_OR = train_perceptron(X_OR, y_OR, epochs=500, learning_rate=0.5)

loss_OR, accuracy_OR = model_OR.evaluate(X_OR, y_OR)
print(f"OR Gate Accuracy: {accuracy_OR}")


model_XOR = train_perceptron(X_XOR, y_XOR, epochs=1000, learning_rate=0.8)

loss_XOR, accuracy_XOR = model_XOR.evaluate(X_XOR, y_XOR)
print(f"XOR Gate Accuracy: {accuracy_XOR}")


input1 = 0
input2 = 0
user_input = np.array([[input1, input2]])
prediction = model_OR.predict(user_input)
if prediction > 0.5:
    print("The model predicts 1 for your input.")
else:
    print("The model predicts 0 for your input.") '''

    print(lab_1_code)


def p2():
    lab_2_code = ''' 

from tensorflow.keras.datasets import fashion_mnist
import matplotlib.pyplot as plt


(X_train, y_train), (X_test, y_test) = fashion_mnist.load_data()

X_train, X_test = X_train / 255.0, X_test / 255.0


model = tf.keras.Sequential([
    tf.keras.layers.Flatten(input_shape=(28, 28)),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(10, activation='softmax')
])
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])


lr_schedule = tf.keras.callbacks.LearningRateScheduler(lambda epoch: 1e-3 * 10 ** (epoch / 20))
history = model.fit(X_train, y_train, epochs=10, validation_data=(X_test, y_test), callbacks=[lr_schedule])


plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.show()
'''
    print(lab_2_code)


def p3():
    lab_3_code = '''
import numpy as np
import tensorflow as tf
from tensorflow.keras.datasets import cifar10
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from sklearn.metrics import accuracy_score, precision_score, recall_score

(X_train, y_train), (X_test, y_test) = cifar10.load_data()

X_train = X_train.astype('float32') / 255.0
X_test = X_test.astype('float32') / 255.0

y_train = tf.keras.utils.to_categorical(y_train, num_classes=10)
y_test = tf.keras.utils.to_categorical(y_test, num_classes=10)

model = Sequential()
model.add(Conv2D(32, (3, 3), activation='relu', padding='same',
input_shape=(32, 32, 3)))
model.add(Conv2D(32, (3, 3), activation='relu', padding='same'))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(64, (3, 3), activation='relu', padding='same'))
model.add(Conv2D(64, (3, 3), activation='relu', padding='same'))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(128, (3, 3), activation='relu', padding='same'))
model.add(Conv2D(128, (3, 3), activation='relu', padding='same'))
model.add(MaxPooling2D((2, 2)))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dense(10, activation='softmax'))

model.compile(optimizer='adam',
loss='categorical_crossentropy',metrics=['accuracy'])

model.fit(X_train, y_train, epochs=10, batch_size=64,
validation_data=(X_test, y_test))

loss, accuracy = model.evaluate(X_test, y_test)
print('Test accuracy:', accuracy)

y_pred_prob = model.predict(X_test)
y_pred = np.argmax(y_pred_prob, axis=1)
y_true = np.argmax(y_test, axis=1)
# Calculate precision and recall
precision = precision_score(y_true, y_pred, average='macro')
recall = recall_score(y_true, y_pred, average='macro')
print('Precision:', precision)
print('Recall:', recall)
'''
    print(lab_3_code)


def p4():
    lab_4_code = """

from tensorflow.keras.datasets import imdb
from tensorflow.keras.preprocessing.sequence import pad_sequences


(X_train, y_train), (X_test, y_test) = imdb.load_data(num_words=10000)


X_train = pad_sequences(X_train, maxlen=200)
X_test = pad_sequences(X_test, maxlen=200)


model = tf.keras.Sequential([
    tf.keras.layers.Embedding(input_dim=10000, output_dim=128, input_length=200),
    tf.keras.layers.LSTM(128, return_sequences=False),
    tf.keras.layers.Dense(1, activation='sigmoid')
])
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])


history = model.fit(X_train, y_train, epochs=10, batch_size=64, validation_data=(X_test, y_test))


import matplotlib.pyplot as plt


plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.show()


from sklearn.metrics import precision_score, recall_score, f1_score


y_pred = (model.predict(X_test) > 0.5).astype("int32")


precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
print(f"Precision: {precision}, Recall: {recall}, F1 Score: {f1}")


def preprocess_input(text):
 tokenizer = Tokenizer(num_words=max_features)
 tokenizer.fit_on_texts([text]) # Fit only on the user input
 sequence = tokenizer.texts_to_sequences([text])
 padded_sequence = pad_sequences(sequence, maxlen=maxlen)
 return padded_sequence

user_input = input("Enter a movie review: ")

processed_input = preprocess_input(user_input)

prediction = model.predict(processed_input)
sentiment = "Positive" if prediction[0][0] > 0.5 else "Negative"

print(f"Predicted Sentiment: {sentiment} (Probability: {prediction[0]
[0]:.2f})")

    """

    print(lab_4_code)


def p5():
    lab_5_code = """

from tensorflow.keras.datasets import cifar10

(X_train, _), (X_test, _) = cifar10.load_data()

X_train = X_train.astype('float32') / 255.0
X_test = X_test.astype('float32') / 255.0


import numpy as np
noise_factor = 0.5
X_train_noisy = X_train + noise_factor * np.random.normal(loc=0.0, scale=1.0, size=X_train.shape)
X_test_noisy = X_test + noise_factor * np.random.normal(loc=0.0, scale=1.0, size=X_test.shape)


X_train_noisy = np.clip(X_train_noisy, 0., 1.)
X_test_noisy = np.clip(X_test_noisy, 0., 1.)


model = tf.keras.Sequential([
    # Encoder
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=(32, 32, 3)),
    tf.keras.layers.MaxPooling2D((2, 2), padding='same'),
    tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
    tf.keras.layers.MaxPooling2D((2, 2), padding='same'),
    
    tf.keras.layers.Conv2DTranspose(64, (3, 3), activation='relu', padding='same'),
    tf.keras.layers.UpSampling2D((2, 2)),
    tf.keras.layers.Conv2DTranspose(32, (3, 3), activation='relu', padding='same'),
    tf.keras.layers.UpSampling2D((2, 2)),
    tf.keras.layers.Conv2D(3, (3, 3), activation='sigmoid', padding='same')
])
model.compile(optimizer='adam', loss='mse')


history = model.fit(X_train_noisy, X_train, epochs=50, batch_size=128, validation_data=(X_test_noisy, X_test))


import matplotlib.pyplot as plt

decoded_imgs = model.predict(X_test_noisy)

n = 10
plt.figure(figsize=(20, 6))
for i in range(n):
    
    ax = plt.subplot(3, n, i + 1)
    plt.imshow(X_test[i])
    plt.title("Original")
    plt.axis('off')
    
    ax = plt.subplot(3, n, i + 1 + n)
    plt.imshow(X_test_noisy[i])
    plt.title("Noisy")
    plt.axis('off')
    
    ax = plt.subplot(3, n, i + 1 + 2*n)
    plt.imshow(decoded_imgs[i])
    plt.title("Reconstructed")
    plt.axis('off')
plt.show()

mse = np.mean(np.square(X_test - decoded_imgs))
print(f"Reconstruction MSE: {mse}")
    """

    print(lab_5_code)
