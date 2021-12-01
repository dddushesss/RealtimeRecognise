import ast

import numpy as np
from sklearn import svm
import pandas as pd
from sklearn.model_selection import train_test_split


def strListToFloat(ls: str):
    res = []
    ls = deleteBrackets(ls)
    for val in ls.split(" "):
        if val != "":
            res.append(float(val))
    return res


def deleteBrackets(ls: str):
    return ls.replace("[", "").replace("]", "")


ls = pd.read_csv("Data/data.csv")
res = []
for i in range(0, len(ls.Char)):

    res.append([strListToFloat(ls.x.values[i]), strListToFloat(ls.y.values[i]),
                strListToFloat(ls.dis.values[i]), strListToFloat(ls.time.values[i])])

clf = svm.LinearSVC()


X_train, X_test, y_train, y_test = train_test_split([row[0] for row in res], ls.Char.values.tolist(), test_size=0.2)

clf.fit(X_train, y_train)
