import pymysql as PMS

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, auc, accuracy_score, roc_auc_score,f1_score,log_loss,\
classification_report, roc_curve

import warnings
warnings.filterwarnings("ignore")
RAND = 10
# connection to database / query
try:
    conn= PMS.connect(
        host='localhost',
        port=3306,
        user='root',
        password='Klim2007',
        database='sakila'
    )
    print("Connected")
except Exception as ex:
    print("Connection refused")
    print(ex)

        #cursor = conn.cursor()
with conn.cursor()as cursor:
  extract = "SELECT \
             rental.customer_id,\
             film.film_id,\
             inventory.inventory_id,\
             film.rating,\
             film.special_features,\
             address.address_id,\
             film_category.category_id,\
             payment.amount\
             FROM  film\
             left join inventory on film.film_id = inventory.film_id\
             left join rental on rental.inventory_id = inventory.inventory_id \
             left join customer on customer.customer_id = rental.customer_id\
             left join address on address.address_id = customer.address_id\
             left join payment on payment.customer_id= customer.customer_id\
             left join film_category on film.film_id = film_category.film_id"
  cursor.execute(extract)
  myresult = cursor.fetchall()

# filling data set
data_set = [i for i in myresult]
 #: data_set.append(i)

# creating data frame
df = pd.DataFrame(data_set)
df = df.rename(columns={df.columns[0]: 'customer', 1:'film_id',2:'inventory_id',3:'rating',4:'special_features',5:'address_id',6:'category_id',7:'amount'})

#print(f'Train size = {df.shape}') # no of columns & rows

#print(df.customer.isna().sum() / df.shape[0]*100) # portion of missed values in customer colum (tiny)

# filling NA`s
ed_mode = df.rating.mode()[0]
df.rating = df.rating.fillna(ed_mode) # filling the blanks
ed_mode_cus = df.customer.mode()[0]
df.customer = df.customer.fillna(ed_mode) # filling the blanks with mode
ed_mean = df.amount.mean()
df.amount = df.amount.fillna(ed_mean) # filling the blanks with mean
ed_mode_cus = df.address_id.mode()[0]
df.address_id = df.address_id.fillna(ed_mode)

# changing formats
df[['film_id','inventory_id']]=df[['film_id','inventory_id']].astype(object)
df['amount'] = df['amount'].astype(float)

#print(df.rating.unique())

#print(df.describe()) # main stat points
#print(df.info())  # Na and Dtype check
#print(df.nunique())
# normalizing for data set size

#ANALYSE OF DISTRIBUTION OF AMOUNT (income)
norm_target = (df
               .amount         # column
               .value_counts(normalize=True)
               .mul(100)
               .rename('percent')
               .reset_index())
plt.figure(figsize=(15, 7))
ax = sns.barplot(x='index', y='percent', data=norm_target)
for p in ax.patches:
    percentage = '{:.1f}%'.format(p.get_height())
    ax.annotate(percentage,  # текст
                (p.get_x() + p.get_width() / 2., p.get_height()),  # axises xy
                ha='center', # centrilizing
                va='center',
                xytext=(0, 10),
                textcoords='offset points', # точка смещения относительно координаты
                fontsize=14)

plt.title('rating', fontsize=16)
plt.xlabel('rating', fontsize=12)
plt.ylabel('Проценты', fontsize=12)

plt.xticks(fontsize=12)
plt.yticks(fontsize=12); # film rating are well balanced

# CAtegory analysis to undetstand

#print(plt.show())
#print(df.groupby('rating')['amount'].sum())
print(df.head(10))
