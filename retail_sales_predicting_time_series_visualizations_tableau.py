# -*- coding: utf-8 -*-
"""Retail Sales Predicting Time Series Visualizations Tableau

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qDyCp2jGx02AQbtUxz_FoQRSxGueoDQV

### Connect to BQ
"""

from google.colab import auth
auth.authenticate_user()
print('Authenticated')

"""## Optional: Enable data table display
There is ``google.colab.data_table``library in Colab that enables table display, useful for large pandas dataframes, will show the data as interactive table. It can be enabled using the code below:
"""

# Commented out IPython magic to ensure Python compatibility.
# %load_ext google.colab.data_table

"""#BigQuery via google-cloud-bigquery

### Declaring the id of the cloud project that will be used in this notebook.
"""

project_id = 'my-project-dec9'

# Commented out IPython magic to ensure Python compatibility.
from google.cloud import bigquery

client = bigquery.Client(project=project_id)

sample_count = 10000
row_count = client.query('''
  SELECT 
    COUNT(*) as total
  FROM `my-project-dec9.Demo.Outputnew`''').to_dataframe().total[0]

df = client.query('''
  SELECT
    *
  FROM
    `my-project-dec9.Demo.Outputnew`
#  WHERE RAND() < %d/%d
'''
# % (sample_count, row_count)).to_dataframe()

print('Full dataset has %d rows' % row_count)

df.head()

"""### Describe the sampled data"""

df.describe()

from google.colab import data_table
data_table.DataTable(df, include_index=True, num_rows_per_page=5)

!pip install -U dataprep
#After installing, if there are any errors, run pip install line again

from dataprep.eda import *

plot(df)

#Checking correlation
plot_correlation(df)

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import math

plt.figure(figsize = (20,10))
sns.heatmap(df.corr(),annot = True)

"""We can see high correlation between cost and discount, also between profit and discount. These features are interconnected, so we did not receive any new information from this correlation, we will remove these features when building the model."""

#Pandas Profiling
!pip install https://github.com/pandas-profiling/pandas-profiling/archive/master.zip
#After installing, if there are any errors, run pip install line again

from pandas_profiling import ProfileReport
profile=ProfileReport(df, title="Pandas Profiling Report", html={'style':{'full_width':True}})
profile.to_notebook_iframe()

profile.to_file("PandasProfile.html")



"""#**Conclusions**

1. 	ABC analysis has shown that there are only items from categories B and C present in our dataset.
2.	XYZ analysis has shown that there are only category Y items present in our shop.
3.	The discount value in 92% of orders is between USD 0 and USD 146.
4.	There are 8 categories of items being sold:
???	Sportswear is 26% of all items in the shop;
???	Kid???s clothes, men???s and women???s clothes are 14% each;
???	The rest of the categories have less than 10% each.
5.	The largest bin for transaction values is for the bin with translations varying from USD 2 to USD 877, we can observe it in 87% of all sales cases. The next bin for sales is for transaction values varying between USD 877 and USD 1752, this bin represents 13% of all cases.
6.	Profit for our shop lies between 0 and USD 232 in majority of cases (84%). 
7.	We can see that the majority of sales happened in 2012, 48% of all sales are date back to 2012. It would be interesting to check if the sales values correlate to the amount of transaction in 2012 and if the sales in monetary value are also the highest in 2012.
8.	Main suppliers of the goods presented in our shop are USA, Germany, Australia, UK.
9. We can see high correlation between cost and discount, also between profit and discount. These features are interconnected, so we did not receive any new information from this correlation, we will remove these features when building the model.
"""

!pip install pycaret #After installing, run again the file loading and libraries initiating

df.info()

from pycaret.regression import *

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
import statsmodels.api as sm
import numpy as np 
import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error
import imageio
import os
from statsmodels.graphics.tsaplots import plot_acf

df['OrderDate'] = pd.to_datetime(df['OrderDate'], infer_datetime_format=True)

df.to_csv('/content/Case3_TS.csv') # Dataset for visualization

df2_ds = df[['OrderID','OrderDate', 'Sales']]

df2_ds = df[['OrderDate', 'Sales']]
df2_ds = df2_ds.sort_values(by=['OrderDate'], ascending=[True])

from google.colab import drive
drive.mount('/content/drive')

df2_ds

aggregated=df2_ds.groupby('OrderDate',as_index=True).sum() # for aggregated output, returns the object with group labels as an index

aggregated.head()

aggregated['OrderDate'] = aggregated.index

aggregated.head()

print(min(aggregated.index))
print(max(aggregated.index))

from google.colab import auth
auth.authenticate_user()
print('Authenticated')

#Dataset with Table name variable
BqDatasetwithtable='Demo.Case3_TS'
#BQproject name variable
BqProject='my-project-dec9'
# pandas-gbq method to load data
# append data if data table exists in BQ project 
# set chunk size of records to be inserted
aggregated.to_gbq(BqDatasetwithtable, BqProject, chunksize=20000, if_exists='append' )

"""#Create Features for work in PyCaret"""

df = df[['OrderDate', 'Sales']]

def create_features(df):
    """
    Creates time series features from datetime index
    """
    df['OrderDate'] = df.index
    df['dayofweek'] = df['OrderDate'].dt.dayofweek
    df['quarter'] = df['OrderDate'].dt.quarter
    df['month'] = df['OrderDate'].dt.month
    df['year'] = df['OrderDate'].dt.year
    df['dayofyear'] = df['OrderDate'].dt.dayofyear
    df['dayofmonth'] = df['OrderDate'].dt.day
    df['weekofyear'] = df['OrderDate'].dt.weekofyear
  
    
    X = df[['dayofweek','quarter','month','year',
           'dayofyear','dayofmonth','weekofyear','Sales']]
    X.index=df.index
    return X

def split_data(data, split_date):
    return data[data.index <= split_date].copy(), \
           data[data.index >  split_date].copy()

aggregated=create_features(aggregated)
train, test = split_data(aggregated, '2012-01-01') # splitting the data for training before 2012-01-01

plt.figure(figsize=(20,10))
plt.xlabel('OrderDate')
plt.ylabel('Sales')
plt.plot(train.index,train['Sales'],label='train')
plt.plot(test.index,test['Sales'],label='test')
plt.legend()
plt.show()

aggregated

"""There are a lot of variations in each separate date, also the dates are not consequitive, there are mising dates. There are two options in this situation: we can add the missing dates or leave the data as is. We will chose the latter option (not inserting the dates, leave the data as is) and the main reason for choosing the second option is that we are using this dataset for predictive modeling and not for time Series modeling. In predictive modeling the data does not take into account simply historic data with the dates/sales, but it also takes into account additional features."""

train.tail(4)

test.head()

test.tail()

"""#Run PyCaret"""

reg = setup(data = train, 
             target = 'Sales',
             numeric_imputation = 'mean',
             categorical_features = ['dayofweek','quarter','month','year','dayofyear','dayofmonth','weekofyear']  , 
            transformation = True,
            transform_target_method = 'yeo-johnson',
            transform_target = True, 
                  combine_rare_levels = True, rare_level_threshold = 0.1,
                  remove_multicollinearity = True, multicollinearity_threshold = 0.95,
            feature_selection = True,
             silent = True)

# returns best models
top = compare_models() #n_select = 3

n_select = 3

"""#Creating baseline model"""

#creating a model using lightgbm
lightgbm = create_model('lightgbm')

tuned_lightgbm = tune_model(lightgbm)

tuned_lightgbm

#creating a model using br
br = create_model('br')

tuned_br = tune_model(br)

tuned_br

#creating a model using lasso
lasso = create_model('lasso')

tuned_lasso = tune_model(lasso)

tuned_lasso

plot_model(lightgbm)

plot_model(lightgbm, plot = 'error')

plot_model(tuned_lightgbm, plot='feature')

predict_model(tuned_lightgbm);

final_lightgbm = finalize_model(tuned_lightgbm)

#Final Light Gradient Boosting Machine parameters for deployment
print(final_lightgbm)

predict_model(final_lightgbm);

unseen_predictions = predict_model(final_lightgbm, data=test)
unseen_predictions.head()
unseen_predictions.loc[unseen_predictions['Label'] < 0, 'Label'] = 0 #removing any negative values

def plot_series(time, series,i, format="-", start=0, end=None):
    #plt.figure(figsize=(20,10))
    plt.plot(time[start:end], series[start:end], format,label=i)
    plt.xlabel("OrderDate")
    plt.ylabel("Sales")
    plt.legend()

plt.figure(figsize=(20,10))
plot_series(test.index, test['Sales'],"True")
#plot_series(train['ds'],train['y'])
plot_series(test.index, unseen_predictions['Label'],"Baseline")

"""In order to provide visualization in BI reporting, we used Tableau interactive analytical dashbord.

The main KPIs of our shop are presented on the first dashboard. We have performed clusterization of the customers, there are 5 clusters based on profit value. Sales values, categories of goods that are sold in our shop, and suppliers??? countries are presented on this dashboard.
"""

# Commented out IPython magic to ensure Python compatibility.
#   %%html
<div class='tableauPlaceholder' id='viz1656244175827' style='position: relative'><noscript><a href='#'><img alt='Dashboard 1 ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Da&#47;DashboardwithKPIandClusterizationforCustomers&#47;Dashboard1&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='DashboardwithKPIandClusterizationforCustomers&#47;Dashboard1' /><param name='tabs' value='no' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Da&#47;DashboardwithKPIandClusterizationforCustomers&#47;Dashboard1&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1656244175827');                    var vizElement = divElement.getElementsByTagName('object')[0];                    if ( divElement.offsetWidth > 800 ) { vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';} else if ( divElement.offsetWidth > 500 ) { vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';} else { vizElement.style.width='100%';vizElement.style.height='1577px';}                     var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>

# Commented out IPython magic to ensure Python compatibility.
# %%html
# <div class='tableauPlaceholder' id='viz1643292857762' style='position: relative'><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='DashboardwithKPIandClusterizationforCustomers&#47;Dashboard1' /><param name='tabs' value='no' /><param name='toolbar' value='yes' /><param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /><param name='filter' value='publish=yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1643292857762');                    var vizElement = divElement.getElementsByTagName('object')[0];                    if ( divElement.offsetWidth > 800 ) { vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';} else if ( divElement.offsetWidth > 500 ) { vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';} else { vizElement.style.width='100%';vizElement.style.height='1577px';}                     var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>

# Commented out IPython magic to ensure Python compatibility.
# %%html
# <div class='tableauPlaceholder' id='viz1643292560051' style='position: relative'><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='CustomerswiththeLowestProfit&#47;Story2' /><param name='tabs' value='no' /><param name='toolbar' value='yes' /><param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /><param name='filter' value='publish=yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1643292560051');                    var vizElement = divElement.getElementsByTagName('object')[0];                    vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';                    var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>

# Commented out IPython magic to ensure Python compatibility.
# %%html
# <div class='tableauPlaceholder' id='viz1656244325584' style='position: relative'><noscript><a href='#'><img alt='Story 3 ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Sa&#47;SalesForecastUsingTableauTS&#47;Story3&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='SalesForecastUsingTableauTS&#47;Story3' /><param name='tabs' value='no' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Sa&#47;SalesForecastUsingTableauTS&#47;Story3&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1656244325584');                    var vizElement = divElement.getElementsByTagName('object')[0];                    vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';                    var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>