# -*- coding: utf-8 -*-
"""submission_time_series.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1q1gZSOsu81sPgC_N242_GWs47Njok5KI
"""

import numpy as np
import pandas as pd
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
import tensorflow as tf
tf.keras.backend.floatx()

# House Hold Energy Data - Time Series
df = pd.read_csv('D202.csv')
df

df.isnull().sum()

df_baru = df.drop(columns=['TYPE','START TIME','END TIME','UNITS','COST','NOTES'])
# mencari niai USAGE paling rendah
print(df_baru['USAGE'].max())
# mencari nilai USAGE paling tinggi
print(df_baru['USAGE'].min())

date = df['DATE'].values
    usage = df['USAGE'].values

    plt.figure(figsize=(20,10))
    plt.plot(date,usage)
    plt.ylabel('Usage')
    plt.title('Electric Usage from 2016-2018',
              fontsize=20);

from sklearn.model_selection import train_test_split
data_latih, data_test, label_latih, label_test = train_test_split(usage, date, test_size=0.2)

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
        series = tf.expand_dims(series, axis=-1)
        ds = tf.data.Dataset.from_tensor_slices(series)
        ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
        ds = ds.flat_map(lambda w: w.batch(window_size + 1))
        ds = ds.shuffle(shuffle_buffer)
        ds = ds.map(lambda w: (w[:-1], w[1:]))
        return ds.batch(batch_size).prefetch(1)

train_set = windowed_dataset(data_latih, window_size=60, batch_size=5000, shuffle_buffer=1000)
    val_set = windowed_dataset(data_test, window_size=60, batch_size=5000, shuffle_buffer=1000)
    model = tf.keras.models.Sequential([
      tf.keras.layers.LSTM(60, return_sequences=True),
      tf.keras.layers.LSTM(60),
      tf.keras.layers.Dense(30, activation="relu"),
      tf.keras.layers.Dense(10, activation="relu"),
      tf.keras.layers.Dense(1),
    ])

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('mae') < 0.236) :
      print("\nMAE kurang dari 10%")
      self.model.stop_training = True
callbacks = myCallback()

optimizer = tf.keras.optimizers.SGD(lr=1.0000e-04, momentum=0.9)
    model.compile(loss=tf.keras.losses.Huber(),
                  optimizer=optimizer,
                  metrics=["mae"])
    history = model.fit(train_set, epochs=30, callbacks=[callbacks], validation_data=(val_set))

import matplotlib.pyplot as plt

plt.plot(history.history['loss'])
plt.title('Model Train')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train'], loc='upper right')
plt.show()

plt.plot(history.history['val_loss'])
plt.title('Model Validasi')
plt.ylabel('loss')
plt.xlabel('Epoch')
plt.legend(['Train'], loc='upper right')
plt.show()