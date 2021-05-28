from celery import Celery

import pandas as pd
import json
import pickle

# Celery configuration
CELERY_BROKER_URL = 'amqp://rabbitmq:rabbitmq@rabbit:5672/'
CELERY_RESULT_BACKEND = 'rpc://'
# Initialize Celery
celery = Celery('workerA', broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)

model_json_file = './model.pkl'
data_file = './repos.json'
number_repos = 8


def load_data():
    with open('repos.json') as json_file:
        repos = json.load(json_file)

    df_repos = pd.DataFrame(repos.values())
    df_repos = df_repos.sample(n=number_repos)

    X = df_repos.drop(['owner', 'name', 'id', 'full_name', 'created_at',
                      'last_commit', 'main_language', 'stargazer_count'], axis=1)
    y = df_repos['stargazer_count']
    y = y.astype('int')

    return X, y


def load_model():
    with open("model.pkl", 'rb') as file:
        pickle_model = pickle.load(file)

    return pickle_model


@celery.task
def get_predictions():
    results = {}
    X, y = load_data()
    loaded_model = load_model()
    predictions = loaded_model.predict(X)
    results['actual'] = y.tolist()
    results['predicted'] = []
    for i in range(len(results['actual'])):
        results['predicted'].append(int(predictions[i]))
    return results
