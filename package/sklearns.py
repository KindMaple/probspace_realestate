# coding: utf-8

import numpy as np
import pandas as pd

from optgbm.sklearn import OGBMRegressor
from lightgbm import LGBMRegressor

from sklearn.metrics import mean_squared_error
from sklearn.model_selection import KFold

train_path = "../input/train_data.csv"
test_path = "../input/test_data.csv"

""" load raw data"""
train = pd.read_csv(train_path)
test = pd.read_csv(test_path)

""" Preprocessing"""
import preprocess as pr
import impute as im

import copy

df = train["y"]

predata = pd.concat([train.drop("y", axis=1), test], ignore_index=True)
predata_copy = copy.deepcopy(predata)
predata_onehot = pr.Preprocessor(predata).all("onehot")
predata_label = pr.Preprocessor(predata_copy).all("label")

""" missing values imputation"""
num_list = [
    "TimeToNearestStation", "TotalFloorArea", "Area", "Frontage", "BuildingYear", "BuildingAge", 
    "Breadth", "CoverageRatio", "FloorAreaRatio", "Period"
    ]
predata_onehot = im.Imputer(predata_onehot).num_imputer(num_list)
print(predata_onehot[num_list].isnull().sum( ))

prep_train_onehot = pd.concat([df, predata_onehot.iloc[:len(train), :]], axis=1)
prep_test_onehot = predata_onehot.iloc[len(train):, :]

prep_train_label = pd.concat([df, predata_label.iloc[:len(train), :]], axis=1)
prep_test_label = predata_label.iloc[len(train):, :]

prep_train_onehot.to_csv("prep_train_onehot.csv", index=False)
prep_test_onehot.to_csv("prep_test_onehot.csv", index=False)

""" define data"""
train_X = prep_train_label.drop(["y", "id", "Prefecture", "Municipality"], axis=1)
train_y = prep_train_label["y"]
test_X = prep_test_label.drop(["id", "Prefecture", "Municipality"], axis=1)

""" target encoding"""
"""from feature_selection import FeatureSelector as FS, cross_validator
train_X_te, test_X_te = FS(train_X, train_y).target_encoder(test_X)"""

""" feature selection"""
"""selected = FS(train_X, train_y).greedy_forward_selection()
selected_te = FS(train_X_te, train_y).greedy_forward_selection()
print("selected features:"+ str(selected))
print("selected target encoding features:"+ str(selected_te))"""

""" check cross validation score"""
"""cv1 = cross_validator(train_X, train_y)
cv2 = cross_validator(train_X[selected], train_y)
cv3 = cross_validator(train_X_te, train_y)
cv4 = cross_validator(train_X_te[selected_te], train_y)

print("base rmse:"+ str(cv1))
print("feature_selected rmse:"+ str(cv2))
print("target encoding rmse:"+ str(cv3))
print("target encoding and feature selection rmse:"+ str(cv4))"""


""" model train & predict"""
reg = OGBMRegressor(random_state=71)
reg.fit(train_X, train_y)

res = reg.predict(test_X)

""" check feature importances"""
importances = pd.DataFrame(
    reg.feature_importances_, index=train_X.columns, 
    columns=["importance"]
    )
importances = importances.sort_values("importance",
    ascending=False
    )
"""importances.to_csv("feature_importance.csv")"""
print(importances)

""" export submit file"""
result = pd.DataFrame(test.index, columns=["id"])
result["y"] = res
result.to_csv("../output/result_realestate_20200426_02.csv", index=False)