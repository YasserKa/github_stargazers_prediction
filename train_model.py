from dask.distributed import Client
from sklearn.ensemble import RandomForestRegressor
from sklearn import linear_model, decomposition
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
import pickle
import joblib
import json
import numpy as np
import pandas as pd


c = Client('tcp://localhost:8786')
c.restart()
with open('repos.json') as json_file:
    repos = json.load(json_file)

df = pd.DataFrame(repos.values())

df = df.drop(['owner', 'name', 'id', 'full_name', 'created_at',
             'last_commit', 'main_language'], axis=1)
X_pd = df.drop(['stargazer_count'], axis=1)
y_pd = df['stargazer_count']

X_train, X_test, y_train, y_test = train_test_split(
    X_pd, y_pd, test_size=0.3, random_state=0)

X_train = X_train.to_numpy()
y_train = y_train.to_numpy()

grid = dict(pca__n_components=[5, 10],
            forest__n_estimators=[50, 100],
            forest__max_depth=[5, 10],
            forest__ccp_alpha=[0.001, 0.01],
            )

forest = RandomForestRegressor()
pca = decomposition.PCA()

pipe = Pipeline(steps=[('pca', pca),
                       ('forest', forest)])

grid_search = GridSearchCV(pipe,
                           param_grid=grid,
                           n_jobs=-1)

with joblib.parallel_backend('dask', scatter=[X_train, y_train]):
    grid_search.fit(X_train, y_train)

with open("model.pkl", 'wb') as file:
    pickle.dump(grid_search, file)
