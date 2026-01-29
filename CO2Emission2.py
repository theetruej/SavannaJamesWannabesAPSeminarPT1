import json
import ast
import math
import numpy as np
import pandas as pd
import random
import matplotlib as mpl
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
import requests
from tensorflow import keras
from keras import Sequential
from keras.layers import Dense, LSTM, Dropout


#Load API Key
API_dir = './.env.txt'


def pullAPIKEY():
    try:
        with open(API_dir, 'r') as file:
            Key = file.read().strip()
            return Key
    except FileNotFoundError:
        print(f"FileNotFoundError{API_dir}")
    except PermissionError:
        print(f"PermissionError{API_dir}")
#Load Json Data from EIA API into a DataFrame
emissionResponse = requests.get(f"https://api.eia.gov/v2/international/data/?api_key={pullAPIKEY()}&frequency=annual&data[0]=value&facets[countryRegionId][]=USA&facets[unit][]=MMTCD&facets[productId][]=4008&facets[activityId][]=8&start=1949&end=2025&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000")
raw_content = emissionResponse.json()
while isinstance(raw_content,str):
    try:
        raw_content = ast.literal_eval(raw_content)
    except (ValueError, SyntaxError):
        print("Decoding JSON has failed")
        break
emissionData = raw_content['response']['data']

df = pd.DataFrame(emissionData)[['period', 'value']]

#Preparing and Scaling Data

np.random.seed(42)
tf.random.set_seed(42)
random.seed(42)

emissions = df['value'].astype(float).values.reshape(-1,1)
scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(emissions)

window_size = 6
X, y = [], []
target_dates = df.index[window_size:]
for i in range(window_size, len(scaled_data)):
    X.append(scaled_data[i-window_size:i, 0])
    y.append(scaled_data[i, 0])

X, y = np.array(X), np.array(y)

X_train, X_test, y_train, y_test, dates_train, dates_test = train_test_split(X, y, target_dates, test_size=0.2, shuffle=False)

X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

#Building it
model = Sequential()
model.add(LSTM(units = 16, return_sequences=True, input_shape=(X_train.shape[1], 1)))
model.add(Dropout(0.1))
model.add(LSTM(units = 16))
model.add(Dropout(0.1))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mean_squared_error')

#Training it
history = model.fit(X_train, y_train, epochs = 150, batch_size=4,validation_split=0.1,verbose=1)

predictions = model.predict(X_test)
predictions = scaler.inverse_transform(predictions).flatten()

y_test = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()

rmse = np.sqrt(np.mean((predictions - y_test) ** 2))
print(f"Root Mean Squared Error: {rmse}")

max_year = 2028

last_window = scaled_data[-window_size:].reshape(1, window_size, 1)

future_predictions_scaled = []

for i in range(int(df.iloc[-1]['period']) + 1, max_year + 1):
    next_pred_scaled = model.predict(last_window)
    future_predictions_scaled.append(next_pred_scaled[0, 0])
    next_pred_reshaped = next_pred_scaled.reshape(1, 1, 1)
    last_window = np.append(last_window[:, 1:, :], next_pred_reshaped, axis=1)

future_predictions = scaler.inverse_transform(np.array(future_predictions_scaled).reshape(-1, 1)).flatten()






years = df['period'].astype(int).values
target_years = df['period'].astype(int).values[window_size:]
train_years = target_years[:len(y_train)]
test_years = target_years[len(y_train):]
future_years = np.arange(int(df.iloc[-1]['period']) + 1, max_year + 1)
last_real_year = years[-1]

plt.figure(figsize=(14, 7))


plt.plot(
    years,
    df['value'].astype(float),
    label="Observed Emissions",
    linewidth=2
)


plt.plot(
    test_years,
    predictions,
    label="LSTM Predictions (Test)",
    linestyle="--"
)


plt.plot(
    future_years,
    future_predictions,
    label="LSTM Forecast (Future)",
    linestyle="dotted",
    linewidth=2
)



plt.xlabel("Year")
plt.ylabel("CO₂ Emissions (MMTCD)")
plt.title("Observed and Forecasted U.S. CO₂ Emissions (LSTM Model)")
plt.legend()
plt.grid(True)
plt.show()
