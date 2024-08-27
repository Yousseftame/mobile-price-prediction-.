# -*- coding: utf-8 -*-
"""mobile price prediction .ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1EwNdL80FciiqENZBkYXfTOOxdgd-o5cv

## Summary

Problem Type : Classification (outcome had 4 options, dataset outcome has equal proportions).  
Dataset : Balanced    
Missing value : None  
Imputation : None    
Evaluation Metric : Accuracy  
Goodness of Fit : The final model had a test set accuracy of 95%.  
Model Used : Linear Discriminat Analysis with standard scaling and recursive feature elimination  
Model Parameters:  Linear Disciminant Analysiso (solver='svd'), RFE (estimator=LinearDiscriminantAnalysis(), n_features_to_select=8), StandardScaler() scaling  
Link: https://www.kaggle.com/datasets/mbsoroush/mobile-price-range  

This notebook analyzed mbile price range data. Using recursive feature elimination with lda and scale, it was determined that the best features were were : **'battery_power', 'int_memory', 'mobile_wt', 'px_height', 'px_width','ram', 'sc_h', 'wifi'**.
"""



import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import make_column_transformer, ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.feature_selection import RFECV, RFE

def pred_stats(pipe_):
    print('Train Cross Validation Accuracy Score:',cross_val_score(pipe_, X_train, y_train, cv=5,scoring='accuracy', n_jobs=-1).mean().round(2))
    pipe_.fit(X_train, y_train)
    y_test_pred = pipe_.predict(X_test)
    print('Test Accuracy Score:', pipe_.score(X_test, y_test))

    ConfusionMatrixDisplay.from_predictions(y_test, y_test_pred, labels=[0,1,2,3])
    plt.show()

# pred_stats(pipe)

url_train = '/kaggle/input/mobile-price-range/train.csv'
url_test = '/kaggle/input/mobile-price-range/test.csv'
df = pd.read_csv(url_train)
df_new = pd.read_csv(url_test)

df.head()

df['price_range'].value_counts(normalize=True)

"""The dataset is balanced as the outcomes of 0, 1, 2, 3 are occuring equally.

## Examine Missing Values
"""

df.isnull().mean()

df_new.isnull().mean()

"""Since there are no missing values in train or test set, there is no need for data imputation.

## Split Dataset
"""

df.columns

features = ['battery_power', 'blue', 'clock_speed', 'dual_sim', 'fc', 'four_g',
       'int_memory', 'm_dep', 'mobile_wt', 'n_cores', 'pc', 'px_height',
       'px_width', 'ram', 'sc_h', 'sc_w', 'talk_time', 'three_g',
       'touch_screen', 'wifi']
target = 'price_range'

X = df[features]
y = df[target]

print(f'X shape {X.shape}, y shape {y.shape}')

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, stratify=y,random_state=42)

print(f'X train shape {X_train.shape}, y train shape {y_train.shape}')
print(f'X test shape {X_test.shape}, y test shape {y_test.shape}')

scaler_std = StandardScaler().set_output(transform='pandas')
ct = make_column_transformer(('passthrough',features))
display(ct)
# ct.fit_transform(X_train, y_train)

"""## Using Logistic Regression"""

logreg = LogisticRegression(solver='liblinear',random_state=42)
pipe = Pipeline([('ct', ct),('scale',None),('clf',logreg)])

pipe.fit(X_train, y_train)
print ('Accuracy Score for Testing Dataset', pipe.score(X_test, y_test))

pred_stats(pipe)

"""## Accuracy

Logistic Regression (all features, no scaling, no tuning) : 0.752

### Using LDA to Determine Score
"""

# Examined the named sets and update the clf from Logistic Regression to Linear Discriminant Analays
pipe.named_steps

lda = LinearDiscriminantAnalysis()
pipe.set_params(clf = lda)

pred_stats(pipe)

"""## Accuracy
Linear Discriminat Analysis (all features, no scaling, no tuning): 0.95  
Logistic Regression (all features, no scaling, no tuning) : 0.752

## Linear Discriminat Analysis - Determine Optimal Features
"""

clf = LinearDiscriminantAnalysis()
min_features_to_select = 1  # Minimum number of features to consider
rfecv = RFECV(
    estimator=clf,
    step=1,
    cv=5,
    scoring="accuracy",
    min_features_to_select=min_features_to_select,
    n_jobs=-1,
)


rfecv.fit(X_train, y_train)
print(f"Optimal number of features: {rfecv.n_features_}")

cv_results = pd.DataFrame(rfecv.cv_results_)
cv_results.index += 1

plt.figure()
plt.xlabel("Number of features selected")
plt.ylabel("Mean test accuracy")
plt.errorbar(
    x=cv_results.index,
    y=cv_results["mean_test_score"],
    yerr=cv_results["std_test_score"],
)
plt.title("Recursive Feature Elimination \nwith correlated features")

print(X_train.columns[rfecv.support_])
print('Mean Accuracy',rfecv.cv_results_['mean_test_score'].max())

plt.show()

"""When Recursive Featue Elimination is done with cross validation on training dataset, it takes into account all the features to determine the highest mean test accuracy.

## Ideally, without tuning, LDA would require all the features for max accuracy

## Tune Pipeline with LDA Model
"""

# Revisit the column transformer
ct = make_column_transformer(('passthrough',features))
display(ct)

scaler_std = StandardScaler().set_output(transform='pandas')
lda = LinearDiscriminantAnalysis()
rfe = RFE(lda, n_features_to_select=2)
pipe = Pipeline([('ct', ct),('scale',None),('feature_sel', None), ('clf',lda)])
pipe

# svd solver does not support shrinkage

params0 = {}
params0['scale'] = [None, scaler_std]
params0['feature_sel'] = [None, rfe]
params0['clf__solver'] = ['svd', 'lsqr', 'eigen']

params1 = {}
params1['scale'] = [None, scaler_std]
params1['feature_sel'] = [rfe]
params1['feature_sel__n_features_to_select'] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
params1['clf__solver'] = ['svd', 'lsqr', 'eigen']

params2 = {}
params2['scale'] = [None, scaler_std]
params2['feature_sel'] = [rfe]
params2['feature_sel__n_features_to_select'] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
params2['clf__solver'] = ['lsqr', 'eigen']
params2['clf__shrinkage'] = [None, 'auto', 0.1,0.2, 0.4, 0.6, 0.8, 0.9, 1]

params3 = {}
params3['scale'] = [None, scaler_std]
params3['feature_sel'] = [None, rfe]
params3['clf__solver'] = ['lsqr', 'eigen']
params3['clf__shrinkage'] = [None, 'auto', 0.1,0.2, 0.4, 0.6, 0.8, 0.9, 1]

params_all = [params0,params1, params2, params3]

grid = GridSearchCV(pipe, params_all, scoring='accuracy', cv=5, n_jobs=-1, verbose=True, error_score='raise')

# Commented out IPython magic to ensure Python compatibility.
grid.fit(X_train, y_train)
# %time

print(grid.best_score_)
print(grid.best_params_)
pd.DataFrame(grid.cv_results_).sort_values('rank_test_score')

grid.best_estimator_

# Best Features According to the Estimator
print(grid.best_estimator_.named_steps.feature_sel.get_feature_names_out())
print('\n Best Features are as follows: \n \n', X_train.columns[grid.best_estimator_.named_steps.feature_sel.get_support()])

# Best Estimator Accuracy on Testing Set
grid.best_estimator_.score(X_test, y_test)

pred_stats(grid.best_estimator_)

# Save the best estimator
final_estimator = grid.best_estimator_

# Train the final estimator of entire dataset (train.csv)
final_estimator.fit(X,y)

"""## Accuracy
Linear Discriminat Analysis(tunned - scaled, 8 features): 0.95  
Linear Discriminat Analysis (all features, no scaling, no tuning): 0.95  
Logistic Regression (all features, no scaling, no tuning) : 0.752

## Final Prediction on test.csv
"""

# Use the final estimator to predict on actual testing dataset (test.csv)
# Drop the id column and pridict
df_new.drop(columns=['id'])

final_id = df_new['id'].copy()

final_prediction = final_estimator.predict(df_new.drop(columns=['id']))
final_prediction

final_df = pd.DataFrame({'ID':final_id, 'Predictions': final_prediction})
final_df.head()  ## This can be shared with shareholders for evaluation.



