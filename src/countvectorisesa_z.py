# -*- coding: utf-8 -*-
"""CountVectorisesA-Z.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1u7US-uIIsvGK1AZjF_Sg4ceFyloEoqBv
"""

!pip install fastaparser

#Positive 
import random
import fastaparser
import pandas as pd

k_low = 3
k_high = 8

with open("/content/Human_promoter.fa") as fasta_file:
        parser = fastaparser.Reader(fasta_file, parse_method='quick')
        Dic = dict()
        for seq in parser:
           s = seq.sequence
           for i in range(len(s)):
               y = s[i:i+3]
               if y not in Dic:
                 Dic[y]=1
               else:
                 Dic[y]+=1
        count=0
        embeddings = []
        for key in Dic:
          count=count+Dic[key]
        for seq in parser:
          s = seq.sequence
          embedding = [1]
          for i in range(len(s)):
            embedding.append(float(Dic[s[i:i+3]])/float(count))
          embeddings.append(embedding)


    
print(Dic) 
print(embedding) 
print(embeddings[0:2])
pd.DataFrame(embeddings).to_csv('/content/positive_embeddings.csv')

#Synthetic Promoters
import random
import fastaparser
import pandas as pd

k_low = 3
k_high = 8

with open("/content/Human_promoter_synthetic.fa") as fasta_file:
        parser = fastaparser.Reader(fasta_file, parse_method='quick')
        Dic = dict()
        for seq in parser:
           s = seq.sequence
           for i in range(len(s)):
               y = s[i:i+3]
               if y not in Dic:
                 Dic[y]=1
               else:
                 Dic[y]+=1
        count=0
        embeddings = []
        for key in Dic:
          count=count+Dic[key]
        for seq in parser:
          s = seq.sequence
          embedding = [0]
          for i in range(len(s)):
            embedding.append(float(Dic[s[i:i+3]])/float(count))
          embeddings.append(embedding)

print(Dic) 
print(embedding) 
print(embeddings[0:2])
pd.DataFrame(embeddings).to_csv('/content/negative_embeddings.csv')

!pip install wandb
!pip install shap

# Commented out IPython magic to ensure Python compatibility.
# import the required modules
# improves output by ignoring warnings
import warnings
warnings.filterwarnings('ignore')
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, plot_confusion_matrix
from pprint import pprint
import matplotlib.pyplot as plt
# %matplotlib inline
# Bayesian optimization
from hyperopt import hp,fmin,tpe,STATUS_OK,Trials
#import wandb

positive = pd.read_csv("/content/positive_embeddings.csv")
positive.head()

negative = pd.read_csv("/content/negative_embeddings.csv")
negative.head()

dataset = positive.append(negative , ignore_index=True)
dataset.head()
dataset.shape[0]

pip install xgboost

pip install --upgrade xgboost

from numpy import loadtxt
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

#load data
import numpy as np
embeddings = dataset.drop(['Unnamed: 0','0'],axis=1)
label = dataset['0']
x = embeddings.to_numpy()
y = label.to_numpy()

# split data into train and test sets.  #three splits- there will be train data-training, test data-hyperparameter tuning, validation data- accuracy testing
def split_dataset(X, Y, train_ratio, test_ratio, validation_ratio):
    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=1 - train_ratio)
    x_val, x_test, y_val, y_test = train_test_split(x_test, y_test, test_size=test_ratio/(test_ratio + validation_ratio))
    return x_train, y_train, x_test, y_test, x_val, y_val

train_ratio = 0.70
validation_ratio = 0.15
test_ratio = 0.15

# train is now 70% of the entire data set
# test is now 15% of the initial data set
# validation is now 15% of the initial data set
x_train, y_train, x_test, y_test, x_val, y_val=split_dataset(x, y, train_ratio, test_ratio, validation_ratio)

# fit model no training data
xgbclassifier = XGBClassifier()
xgbclassifier.fit(x_train, y_train)

# predicted values from the model
y_pred=xgbclassifier.predict(x_test)
y_probas=xgbclassifier.predict_proba(x_test)

#wandb.log({'accuracy': accuracy_score(y_test, y_pred)})

# accuracy prediction
accuracy = accuracy_score(y_test, y_pred)
print("BASE MODEL")
print("Accuracy: %.2f%%" % (accuracy * 100.0))


# classification report
print("Classification report:\n")
print(classification_report(y_test, y_pred))

# confusion matrix
conf=confusion_matrix(y_test, y_pred)
print("Confusion matrix:\n", conf)

# confusion matrix plot
print("Confusion matrix plot:\n")
plot_confusion_matrix(xgbclassifier, x_test, y_test) 
plt.show()

import shap
explainer = shap.TreeExplainer(xgbclassifier)
shap_values = explainer.shap_values(x_test)

shap_values

l=shap_values[0]
len(l)

shap.summary_plot(shap_values, x_test, plot_type="bar")

len(xgbclassifier.feature_importances_)

# parameters cuurently used
print('Parameters currently in use:')
pprint(xgbclassifier.get_params())

# Hyperparameter tuning using GridsearchCV
# Setting range of parameters
#Learning rate shrinks the weights to make the boosting process more conservative
learning_rate = [0.0001,0.001, 0.01, 0.1, 1]
# Number of trees in xgboost decision tree
n_estimators = [1000, 2000, 3000, 4000, 5000]
# Number of features to consider at every split
max_features = ['auto', 'sqrt']
# Maximum number of levels in tree
max_depth = [1, 2, 3, 4, 5]
#  Percentage of columns to be randomly samples for each tree.
colsample_bytree = [i/10.0 for i in range(3,10)]
#  Gamma specifies the minimum loss reduction required to make a split
gamma = [i/10.0 for i in range(0,5)]
#  reg_alpha provides l1 regularization to the weight, higher values result in more conservative models
reg_alpha = [1e-5, 1e-2, 0.1, 1, 10, 100]
# reg_lambda provides l2 regularization to the weight, higher values result in more conservative models
reg_lambda = [1e-5, 1e-2, 0.1, 1, 10, 100]
# Create the random grid
param = {'n_estimators': n_estimators,
               'max_features': max_features,
               'max_depth': max_depth,
               'colsample_bytree': colsample_bytree,
               'gamma': gamma,
               'reg_alpha': reg_alpha,
               'reg_lambda': reg_lambda,
               'learning_rate':learning_rate
         }

print("\nGRID SEARCH MODEL")
print('Range of parameters used for hyperparameter tuning:')
pprint(param)
# implemented grid search 
classifier_grid=GridSearchCV(estimator=xgbclassifier, param_grid=param, cv = 3, verbose=2, n_jobs = 4)
# fit the training data
classifier_grid.fit(x_train,y_train)

# Best hyperparameter values
print('Best parameter values:')
print(classifier_grid.best_params_)

# predicted values from the grid search model
cl_g=classifier_grid.best_estimator_
pred=cl_g.predict(x_test)
y_probas = cl_g.predict_proba(x_test)

# accuracy prediction for grid search model
accuracy = accuracy_score(y_test, pred)
print("Accuracy: %.2f%%" % (accuracy * 100.0))

#classification report
print("Classification report:\n")
print(classification_report(y_test, y_pred))

# confusion matrix
conf_g=confusion_matrix(y_test, pred)
print("Confusion matrix\n", conf_g)

# confusion matrix plot
print("Confusion matrix plot:\n")
plot_confusion_matrix(cl_g, x_test, y_test)  
plt.show()

explainer = shap.TreeExplainer(cl_g)
shap_values = explainer.shap_values(x_test)
shap.summary_plot(shap_values, x_test, plot_type="bar")

# Random search implementation
# Module for hyperparameter tuning
# Hyperparameter tuning using RandomizedsearchCV
# Setting range of parameters
#Learning rate shrinks the weights to make the boosting process more conservative
learning_rate = [0.0001,0.001, 0.01, 0.1, 1]
# Number of trees in xgboost decision tree
n_estimators = [1000, 2000, 3000, 4000, 5000]
# Number of features to consider at every split
max_features = ['auto', 'sqrt']
# Maximum number of levels in tree
max_depth = [1, 2, 3, 4, 5]
#  Percentage of columns to be randomly samples for each tree.
colsample_bytree = [i/10.0 for i in range(3,10)]
#  Gamma specifies the minimum loss reduction required to make a split
gamma = [i/10.0 for i in range(0,5)]
#  reg_alpha provides l1 regularization to the weight, higher values result in more conservative models
reg_alpha = [1e-5, 1e-2, 0.1, 1, 10, 100]
# reg_lambda provides l2 regularization to the weight, higher values result in more conservative models
reg_lambda = [1e-5, 1e-2, 0.1, 1, 10, 100]
# Create the random grid
param = {'n_estimators': n_estimators,
               'max_features': max_features,
               'max_depth': max_depth,
               'colsample_bytree': colsample_bytree,
               'gamma': gamma,
               'reg_alpha': reg_alpha,
               'reg_lambda': reg_lambda,
               'learning_rate':learning_rate
         }
print("\nRANDOM SEARCH MODEL")
print('Range of parameters used for hyperparameter tuning:')
pprint(param)

# implemented random search
classifier_random=RandomizedSearchCV(estimator = xgbclassifier, param_distributions = param, n_iter = 100, cv = 3, verbose=2, random_state=42, n_jobs = -1)

# fit the training data in the randomized model
classifier_random.fit(x_train, y_train)

# Best hyperparameter values
print('Best parameter values:')
print(classifier_random.best_params_)

# predicted values from the random search model using best parameters
cl_r=classifier_random.best_estimator_
pred=cl_r.predict(x_test)
y_probas = cl_r.predict_proba(x_test)

# accuracy prediction for random search model
accuracy = accuracy_score(y_test, pred)
print("Accuracy: %.2f%%" % (accuracy * 100.0))

#classification report
print("Classification report:\n")
print(classification_report(y_test, y_pred))

# confusion matrix
conf_r=confusion_matrix(y_test, pred)
print("Confusion matrix\n", conf_r)

# confusion matrix plot
print("Confusion matrix plot:\n")
plot_confusion_matrix(cl_r, x_test, y_test)  
plt.show()

explainer = shap.TreeExplainer(cl_r)
shap_values = explainer.shap_values(x_test)
shap.summary_plot(shap_values, x_test, plot_type="bar", feature_names=feature_name)

# Bayesian optimization
print("\nBAYESIAN OPTIMIZATION")
from sklearn.model_selection import cross_val_score
from hyperopt import tpe, STATUS_OK, Trials, hp, fmin, STATUS_OK, space_eval
space = {
    'learning_rate': hp.choice('learning_rate', [0.0001,0.001, 0.01, 0.1, 1]),
    'max_depth' : hp.choice('max_depth', range(3,21,3)),
    'gamma' : hp.choice('gamma', [i/10.0 for i in range(0,5)]),
    'colsample_bytree' : hp.choice('colsample_bytree', [i/10.0 for i in range(3,10)]),
    'reg_alpha' : hp.choice('reg_alpha', [1e-5, 1e-2, 0.1, 1, 10, 100]),
    'reg_lambda' : hp.choice('reg_lambda', [1e-5, 1e-2, 0.1, 1, 10, 100])
}

def objective(space):
   model = XGBClassifier(seed=0, **space)
   #5 times cross validation fives 5 accuracies=>mean of these accuracies will be considered
   accuracy = cross_val_score(model, x_train, y_train, cv = 5).mean()
   # We aim to maximize accuracy, therefore we return it as a negative value
   return {'loss': -accuracy, 'status': STATUS_OK }

# Trials to track progress
bayes_trials = Trials()
# Optimize
best = fmin(fn = objective, space = space, algo = tpe.suggest, max_evals = 48, trials = bayes_trials)
# Print the index of the best parameters
print(best)
# Print the values of the best parameters
print(space_eval(space, best))
# Train model using the best parameters
xgboost_bayesian = XGBClassifier(seed=0,
                           colsample_bytree=0.4,
                           gamma=0.2,
                           learning_rate=1,
                           max_depth=12,
                           reg_alpha=1e-05,
                           reg_lambda=1
                           ).fit(x_train,y_train)

pred_b = xgboost_bayesian.predict(x_test)

# accuracy prediction
accuracy = accuracy_score(y_test, pred_b)
print("Accuracy: %.2f%%" % (accuracy * 100.0))

# classification report
print("Classification report:\n")
print(classification_report(y_test, pred_b))

# confusion matrix
conf=confusion_matrix(y_test, pred_b)
print("Confusion matrix:\n", conf)

# confusion matrix plot
print("Confusion matrix plot:\n")
plot_confusion_matrix(xgboost_bayesian, x_test, y_test)  
plt.show()

# Bayesian search
import pandas as pd

pos = pd.read_csv("/content/positive_embeddings.csv", skiprows=1, sep=" ", index_col=0, header=None)
neg = pd.read_csv("/content/negative_embeddings.csv", skiprows=1, sep=" ", index_col=0, header=None)
df = pd.concat([pos, neg])
#df.iloc[:,:0]
# this converts the index (ie k-mers) into a list
p=pos.index.tolist()
n=neg.index.tolist()
posd=pos.index
negd=neg.index
whole=posd.append(negd)
kmer=list(whole)

# use countvectorizer
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt
import numpy as np

# Load the text data
corpus=kmer

vectorizer = CountVectorizer()
docs       = vectorizer.fit_transform(corpus)
features   = vectorizer.get_feature_names()

# step 2
feature_name=np.array(features)

# step 3
sorted_idx = xgboost_bayesian.feature_importances_.argsort()#[::-1]
#feature_name = [feature_name[i] for i in sorted_idx]
n_top_features=50
plt.figure(figsize=(8,10))
plt.barh(feature_name[sorted_idx][:n_top_features ],xgbclassifier.feature_importances_[sorted_idx][:n_top_features ])
plt.xlabel("XGBoost feature Importance ")

explainer = shap.TreeExplainer(cl_r)
shap_values = explainer.shap_values(x_test)
shap.summary_plot(shap_values, x_test, plot_type="bar", feature_names=feature_name)

# Weights and biases
import wandb
wandb.init(project="XGBoost classifier_cv", name="XGBoost-base model")
# Feature importance
wandb.sklearn.plot_feature_importances(xgbclassifier)
# metrics summary
wandb.sklearn.plot_summary_metrics(xgbclassifier, x_train, y_train, x_test, y_test)
# precision recall
wandb.sklearn.plot_precision_recall(y_test, y_probas, labels=None)
# ROC curve
wandb.sklearn.plot_roc(y_test, y_probas, labels=None)
# Learning curve
wandb.sklearn.plot_learning_curve(xgbclassifier, x_train, y_train)
# class proportions
wandb.sklearn.plot_class_proportions(y_train, y_test, labels=None)
# calibration curve
wandb.sklearn.plot_calibration_curve(xgbclassifier, x, y, 'XGBoost- Base model')
#confusion matrix
wandb.sklearn.plot_confusion_matrix(y_test, y_pred, labels=None)

import wandb
wandb.init(project="XGBoost classifier_cv", name="XGBoost-gridsearch model")
# Feature importance
wandb.sklearn.plot_feature_importances(cl_g)
# metrics summary
wandb.sklearn.plot_summary_metrics(cl_g, x_train, y_train, x_test, y_test)
# precision recall
wandb.sklearn.plot_precision_recall(y_test, y_probas, labels=None)
# ROC curve
wandb.sklearn.plot_roc(y_test, y_probas, labels=None)
# Learning curve
wandb.sklearn.plot_learning_curve(cl_g, x_train, y_train)
# class proportions
wandb.sklearn.plot_class_proportions(y_train, y_test, labels=None)
# calibration curve
wandb.sklearn.plot_calibration_curve(cl_g, x, y, 'XGBoost-Grid search model')
# confusion matrix
wandb.sklearn.plot_confusion_matrix(y_test, y_pred, labels=None)

wandb.init(project="XGBoost classifier_cv", name="XGBoost-random search model")
# Feature importance
wandb.sklearn.plot_feature_importances(cl_r)
# metrics summary
wandb.sklearn.plot_summary_metrics(cl_r, x_train, y_train, x_test, y_test)
# precision recall
wandb.sklearn.plot_precision_recall(y_test, y_probas, labels=None)
# ROC curve
wandb.sklearn.plot_roc(y_test, y_probas, labels=None)
# Learning curve
wandb.sklearn.plot_learning_curve(cl_r, x_train, y_train)
# class proportions
wandb.sklearn.plot_class_proportions(y_train, y_test, labels=None)
# calibration curve
wandb.sklearn.plot_calibration_curve(cl_r, x, y, 'XGBoost-Random search model')
# confusion matrix
wandb.sklearn.plot_confusion_matrix(y_test, y_pred, labels=None)

wandb.init(project="XGBoost classifier_cv", name="XGBoost-Bayesian optimization model")
# Feature importance
wandb.sklearn.plot_feature_importances(model=xgboost_bayesian, title="XGBoost-Bayesian model")
# metrics summary
wandb.sklearn.plot_summary_metrics(xgboost_bayesian, x_train, y_train, x_test, y_test)
# precision recall
wandb.sklearn.plot_precision_recall(y_test, y_probas, labels=None)
# ROC curve
wandb.sklearn.plot_roc(y_test, y_probas, labels=None)
# Learning curve
wandb.sklearn.plot_learning_curve(xgboost_bayesian, x_train, y_train)
# class proportions
wandb.sklearn.plot_class_proportions(y_train, y_test, labels=None)
# calibration curve
wandb.sklearn.plot_calibration_curve(xgboost_bayesian, x, y, 'XGBoost-Bayesian optimization model')
# confusion matrix
wandb.sklearn.plot_confusion_matrix(y_test, y_pred, labels=None)

# Exporting metrics from a project in to a CSV file
import pandas as pd 
import wandb
api = wandb.Api()
entity, project = "tyagilab", "XGBoost classifier_cv"  # set to your entity and project 
runs = api.runs(entity + "/" + project) 

summary_list, config_list, name_list = [], [], []
for run in runs: 
    # .summary contains the output keys/values for metrics like accuracy.
    summary_list.append(run.summary._json_dict)

    # .config contains the hyperparameters.
    #  We remove special values that start with _.
    config_list.append(
        {k: v for k,v in run.config.items()
         if not k.startswith('_')})

    # .name is the human-readable name of the run.
    name_list.append(run.name)

runs_df = pd.DataFrame({
    "summary": summary_list,
    "config": config_list,
    "name": name_list
    })

runs_df.to_csv("project.csv")