from sklearn.metrics import r2_score
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


def write_prediction(table, time, pred):
    a = table['Algorithm']
    for i in range(0, len(pred)):
        if pred[i] > 200:
            res = 'win'
        else:
            res = 'lose'
        data1 = f'{a[0]}; {res}; {time[i][0]}; {round(pred[i])}\n'
        f = open(r"predicted_results.csv", 'a')
        f.write(data1)
        f.close()



df = pd.read_csv('result.csv', sep=',')
df = df.replace({True:1}).replace({False:0}).replace({"expectimax":0}).replace({"minimax":1})
df = df.set_axis(['Algorithm', 'IsWin', 'Time', 'Coins', 'Score'], axis=1)
df["Time"] = pd.to_timedelta(df['Time']).dt.total_seconds()
df.sort_values("Time")
# print(df)


X = np.array(df['Time']).reshape(-1, 1)
Y = np.array(df['Score'])
x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=1 - (len(df) - 5) / len(df), shuffle=False)
model = LinearRegression()
model.fit(x_train, y_train)

y_pred = model.predict(x_test)

plt.scatter(x_train, y_train, color='orange')
plt.scatter(x_test, y_pred, color='red')
plt.scatter(x_test, y_test, color='blue')
plt.plot(x_test,y_pred, color='r')
plt.title("Linear regression")
plt.xlabel('Total seconds')
plt.ylabel('Score')
plt.show()

write_prediction(df, x_test, y_pred)

print("Predicted: ", y_pred)
print("Actual: ", y_test)

print("k = ", model.coef_[0])