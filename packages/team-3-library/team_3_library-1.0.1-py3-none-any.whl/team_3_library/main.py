import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class dataset_clean():
    def __init__(self,dataframe):
        self.df=dataframe
    def analyze_nulls(self): #percentage of null values
        null_percentage = self.df.isnull().mean() * 100
        return null_percentage
    
    def drop_null_columns(self,percentage):
        null_percentage=self.analyze_nulls()
        column_drop = null_percentage[null_percentage>percentage].index
        self.df.drop(columns=column_drop, inplace=True)

    def fill_nulls(self,column, e):
        if self.df[column].dtype in [np.float64, np.int64]:
            if e == 'auto':
                distribution_type = self.analyze_distribution(column)
                if distribution_type == 'normal':
                    e ='mean'
                elif distribution_type =='skewed':
                    e = 'median'
                else:
                    e = 'mode'
            if e == 'mean':
                fill_value = self.df[column].mean()
            elif e == 'median':
                fill_value = self.df[column].median()
            elif e == 'mode':
                fill_value = self.df[column].mode()[0]
            elif e == 'random':
                fill_value = np.random.choice(self.df[column].dropna())
            else:
                raise ValueError (
                    'You did not put a valid choice'
                )
            print('The value that replaced the null values is %f'%fill_value)
            self.df[column].fillna(fill_value, inplace=True)
        elif self.df[column].dtype == object or str:
            if e == 'auto':
                e = 'mode'

            if e == 'mode':
                fill_value = self.df[column].mode()[0]
                self.df[column].fillna(fill_value, inplace=True)
                print('The value that replaced the null values is %s'%fill_value)
            elif e == 'ffill':
                self.df[column].fillna(method='ffill', inplace = True)
            elif e == 'bfill':
                self.df[column].fillna(method='bfill', inplace = True)
            elif e == 'random':
                fill_value = np.random.choice(self.df[column].dropna())
                self.df[column].fillna(fill_value, inplace=True)
                print('The value that replaced the null values is %s'%fill_value)
            else:
                raise ValueError('You did not choose a valid thing')
            
        else:
            raise TypeError ('Data of the column no identified {%d} : {%d}'%(column,self.df[column].dtype))
        
        
    
    def analyze_distribution(self, column):
        column_data = self.df[column].dropna()
        mean = column_data.mean()
        median = column_data.median()
        std_dev = column_data.std()
        #std_dev = np.sqrt(((column_data - mean)**2).sum() / len (column_data))

        sesgo = (3*(mean-median)) / std_dev if std_dev!=0 else 0 #to calculate the symmetry

        if abs(sesgo) < 0.5: #if the skewness is < 0.5 it is considered a symmetric distribution, meaning normal distribution 
            print('The distribution is normal')
            return 'normal'
        elif abs(sesgo) >= 0.5: #if the skewness is >= 0.5 it is considered a asymmetric distribution, meaning skewed distribution
            print('The distribution is skewed')
            return 'skewed'
        else: 
            return 'other'
        
    def clean_column_customized(self, column):
        null_count = self.df[column].isnull().sum()
        if null_count ==  0:
            return
        
        else:
            if self.df[column].dtype in [np.float64, np.int64, np.float_, np.int_]:
                print('The column %s is a numerical column and it has %i null values\n'%(column,null_count))
                print('The distribution that follow this column data is the following:\n')
                self.graph_num(column)
                e = input('How do you want to fill the null values of %s? (auto/mean/median/mode/random): '%(column))
                self.fill_nulls(column,e)
                print('Now the distribution of the column %s has changed to the following one: '%(column))
                self.graph_num(column)
            elif self.df[column].dtype in [str, object]:
                print('The column %s is a categorical column and it has %i null values\n'%(column,null_count))
                print('The distribution that follow this column data is the following:\n')
                self.graph_obj(column)
                e = input('How do you want to fill the null values of %s? (auto/mode/ffill/bfill/random): '%(column))
                self.fill_nulls(column,e)
                print('Now the distribution of the column %s has changed to the following one: '%(column))
                self.graph_obj(column)
            else:
                raise TypeError('Not identified')
        

    def graph_num(self,column):
        sns.histplot(data=self.df, x=column,kde=True)
        plt.show()
        
    def graph_obj(self,column):
        sns.countplot(data=self.df,x=column)
        plt.title('Different values')
        plt.xlabel('Value')
        plt.ylabel('Times that it appears')
        plt.xticks(rotation=90)
        plt.show()

    def clean_dataset_percentage(self, percentage):
        self.drop_null_columns(percentage)
        for c in self.df.columns:
            self.clean_column_customized(c)
            print(self.df[c])
            print('The number of null values is %i'%self.df[c].isnull().sum())

    def percentage(self):
        p=int(input('What number of percentage of null do you want to have? '))
        return p