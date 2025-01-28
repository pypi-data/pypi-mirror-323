def p1():
    lab_1_code = ''' 
# Lab 1: Implementing a Simple Perceptron using TensorFlow
import numpy as np
import tensorflow as tf

# Define OR and XOR datasets
X_OR = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=np.float32)
y_OR = np.array([[0], [1], [1], [1]], dtype=np.float32)
X_XOR = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=np.float32)
y_XOR = np.array([[0], [1], [1], [0]], dtype=np.float32)

# Function to create and train a single-layer perceptron with improved accuracy
def train_perceptron(X, y, epochs=100, learning_rate=0.1):
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(1, activation='sigmoid', input_shape=(2,))
    ])
    model.compile(optimizer=tf.keras.optimizers.SGD(learning_rate=learning_rate),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
    model.fit(X, y, epochs=epochs, verbose=0)
    return model

# Train on OR gate with improved accuracy
model_OR = train_perceptron(X_OR, y_OR, epochs=500, learning_rate=0.5)
# Evaluate on OR
loss_OR, accuracy_OR = model_OR.evaluate(X_OR, y_OR)
print(f"OR Gate Accuracy: {accuracy_OR}")

# Train on XOR gate with improved accuracy (not possible with a single-layer perceptron)
model_XOR = train_perceptron(X_XOR, y_XOR, epochs=1000, learning_rate=0.8)
# Evaluate on XOR
loss_XOR, accuracy_XOR = model_XOR.evaluate(X_XOR, y_XOR)
print(f"XOR Gate Accuracy: {accuracy_XOR}")

# Make a prediction using model_OR
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
# Lab 2: Building a Multilayer Perceptron (MLP)
from tensorflow.keras.datasets import fashion_mnist
import matplotlib.pyplot as plt

# Load dataset
(X_train, y_train), (X_test, y_test) = fashion_mnist.load_data()
# Normalize data
X_train, X_test = X_train / 255.0, X_test / 255.0

# Define the MLP model with batch normalization and dropout
model = tf.keras.Sequential([
    tf.keras.layers.Flatten(input_shape=(28, 28)),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(10, activation='softmax')
])
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Implement learning rate scheduling
lr_schedule = tf.keras.callbacks.LearningRateScheduler(lambda epoch: 1e-3 * 10 ** (epoch / 20))
history = model.fit(X_train, y_train, epochs=10, validation_data=(X_test, y_test), callbacks=[lr_schedule])

# Plot training and validation performance
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
# Load CIFAR-10 dataset
(X_train, y_train), (X_test, y_test) = cifar10.load_data()
# Normalize pixel values to be between 0 and 1
X_train = X_train.astype('float32') / 255.0
X_test = X_test.astype('float32') / 255.0
# Convert class vectors to binary class matrices (one-hot encoding)
y_train = tf.keras.utils.to_categorical(y_train, num_classes=10)
y_test = tf.keras.utils.to_categorical(y_test, num_classes=10)
2. Define a deeper CNN model:
# Define the CNN model
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
# Compile the model
model.compile(optimizer='adam',
loss='categorical_crossentropy',metrics=['accuracy'])
3. Evaluate the model using precision, recall, and confusion matrix:
# Train the model
model.fit(X_train, y_train, epochs=10, batch_size=64,
validation_data=(X_test, y_test))
# Evaluate the model
loss, accuracy = model.evaluate(X_test, y_test)
print('Test accuracy:', accuracy)
# Make predictions on the test set
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
# 1. Load the IMDB dataset:
from tensorflow.keras.datasets import imdb
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Load dataset
(X_train, y_train), (X_test, y_test) = imdb.load_data(num_words=10000)

# Pad sequences to ensure equal length inputs
X_train = pad_sequences(X_train, maxlen=200)
X_test = pad_sequences(X_test, maxlen=200)

# 2. Define the LSTM model with an embedding layer:
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(input_dim=10000, output_dim=128, input_length=200),
    tf.keras.layers.LSTM(128, return_sequences=False),
    tf.keras.layers.Dense(1, activation='sigmoid')
])
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# 3. Train the model on the IMDB dataset:
history = model.fit(X_train, y_train, epochs=10, batch_size=64, validation_data=(X_test, y_test))

# 4. Visualize training progress: Plot accuracy and loss for both training and validation sets.
import matplotlib.pyplot as plt

# Plot accuracy
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

# 5. Evaluate the model using precision, recall, and F1 score:
from sklearn.metrics import precision_score, recall_score, f1_score

# Get predictions and round them to nearest integer
y_pred = (model.predict(X_test) > 0.5).astype("int32")

# Evaluate performance
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
# Get user input
user_input = input("Enter a movie review: ")
# Preprocess the user input
processed_input = preprocess_input(user_input)
# Make prediction
prediction = model.predict(processed_input)
sentiment = "Positive" if prediction[0][0] > 0.5 else "Negative"
# Output the result
print(f"Predicted Sentiment: {sentiment} (Probability: {prediction[0]
[0]:.2f})")

    """

    print(lab_4_code)


def p5():
    lab_5_code = """
# 1. Load and preprocess the CIFAR-10 dataset:
from tensorflow.keras.datasets import cifar10
# Load dataset
(X_train, _), (X_test, _) = cifar10.load_data()
# Normalize the data
X_train = X_train.astype('float32') / 255.0
X_test = X_test.astype('float32') / 255.0

# 2. Add noise to the CIFAR-10 images:
import numpy as np
noise_factor = 0.5
X_train_noisy = X_train + noise_factor * np.random.normal(loc=0.0, scale=1.0, size=X_train.shape)
X_test_noisy = X_test + noise_factor * np.random.normal(loc=0.0, scale=1.0, size=X_test.shape)
# Clip to keep pixel values between 0 and 1
X_train_noisy = np.clip(X_train_noisy, 0., 1.)
X_test_noisy = np.clip(X_test_noisy, 0., 1.)

# 3. Define the convolutional autoencoder (CAE):
model = tf.keras.Sequential([
    # Encoder
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=(32, 32, 3)),
    tf.keras.layers.MaxPooling2D((2, 2), padding='same'),
    tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
    tf.keras.layers.MaxPooling2D((2, 2), padding='same'),
    # Decoder
    tf.keras.layers.Conv2DTranspose(64, (3, 3), activation='relu', padding='same'),
    tf.keras.layers.UpSampling2D((2, 2)),
    tf.keras.layers.Conv2DTranspose(32, (3, 3), activation='relu', padding='same'),
    tf.keras.layers.UpSampling2D((2, 2)),
    tf.keras.layers.Conv2D(3, (3, 3), activation='sigmoid', padding='same')
])
model.compile(optimizer='adam', loss='mse')

# 4. Train the autoencoder on noisy CIFAR-10 images:
history = model.fit(X_train_noisy, X_train, epochs=50, batch_size=128, validation_data=(X_test_noisy, X_test))

# 5. Visualize original, noisy, and reconstructed images:
import matplotlib.pyplot as plt
# Reconstruct images
decoded_imgs = model.predict(X_test_noisy)
# Display original, noisy, and reconstructed images
n = 10
plt.figure(figsize=(20, 6))
for i in range(n):
    # Display original
    ax = plt.subplot(3, n, i + 1)
    plt.imshow(X_test[i])
    plt.title("Original")
    plt.axis('off')
    # Display noisy
    ax = plt.subplot(3, n, i + 1 + n)
    plt.imshow(X_test_noisy[i])
    plt.title("Noisy")
    plt.axis('off')
    # Display reconstruction
    ax = plt.subplot(3, n, i + 1 + 2*n)
    plt.imshow(decoded_imgs[i])
    plt.title("Reconstructed")
    plt.axis('off')
plt.show()
    """

    print(lab_5_code)
