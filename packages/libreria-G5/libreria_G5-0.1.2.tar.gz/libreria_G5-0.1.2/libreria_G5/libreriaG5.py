import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns

class Structure:
    def __init__ (self, limit_value = 65, method_object = 'moda', method_number = 'mean', quantile_min = 0.15, quantile_max = 0.75, keep_column = 'no'):
        self.limit_value = limit_value
        self.method_object = method_object
        self.method_number = method_number
        self.quantile_min = quantile_min
        self.quantile_max = quantile_max
        self.keep_column = keep_column

    def processing(self, df):
        df = df.loc[:, df.isna().mean()*100 < self.limit_value]
        columns = df.columns
        num_columns = len(columns)
        for i in columns:
            if df[i].dtype == 'object':
                if self.method_object.lower() == 'moda':
                    df[i] = df[i].fillna(df[i].mode()[0])
                elif self.method_object.lower() == 'bfill':
                    df[i] = df[i].bfill()
                elif self.method_object.lower() == 'ffil':
                    df[i] = df[i].ffill()
                else:
                    print('This model is not valid; please try one of the following: moda, bfill (back fill) or ffill (front fill)')
            else:
                if self.method_number.lower() == 'mean':
                    df[i] = df[i].fillna(df[i].mean())
                elif self.method_number.lower() == 'moda':
                    df[i] = df[i].fillna(df[i].mode()[0])
                elif self.method_number.lower() == 'bfill':
                    df[i] = df[i].bfill()
                elif self.method_number.lower() == 'ffil':
                    df[i] = df[i].ffill()
                elif self.method_number.lower() == 'medain':
                    df[i] = df[i].fillna(df[i].median())
                elif self.method_number.lower() == 'max':
                    df[i] = df[i].fillna(df[i].max())
                elif self.method_number.lower() == 'min':
                    df[i] = df[i].fillna(df[i].min())
                else: 
                    print('This model is not valid; please try one of the following: moda, mean, median, max, min, bfill (back fill) or ffill (front fill)')
        return df

    def remove_outliers(self, df, columns):
        for col in columns:
            try:
                Q1 = df[col].quantile(self.quantile_min)
                Q3 = df[col].quantile(self.quantile_max)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
            except TypeError:
                df[col] = df[col]   
        return df

    def normalize(self, df1):
        try: 
            scaler = MinMaxScaler()
            datos_normalizados = scaler.fit_transform(df1)
            df = pd.DataFrame(datos_normalizados, columns= df1.columns)
            return df
        except ValueError:
            print('There are non-numeric variables that cannot be normalized. Remove them or use the .string_to_number() function to convert them into numbers.')

    
    def string_to_number(self, df):
        modelo_label = LabelEncoder()
        if self.keep_column.lower() == 'no':
            for i in df.columns:
                if df[i].dtype == 'object':
                    df[i] = modelo_label.fit_transform(df[i])
        elif self.keep_column.lower() == 'si':
            for i in df.columns:
                if df[i].dtype == 'object':
                    nombre = i + '_encoded'
                    df[nombre] = modelo_label.fit_transform(df[i])
        return df

    def visual_analysis_of_numerical_variables(self, df_g):
        numerical_columns = df_g.select_dtypes(include=['float64', 'int64']).columns
        num_cols = len(numerical_columns) 
        index = max(1, int(round(num_cols / 3)))

        fig, axes = plt.subplots(index, 3, figsize=(12, 10))
        for i, col in enumerate(numerical_columns):
            row = i // 3  # Fila actual
            col_pos = i % 3  # Columna actual
            sns.histplot(df_g[col], kde=True, ax=axes[row, col_pos])
            axes[row, col_pos].set_title(f'Distribution of {col}')
            axes[row, col_pos].set_xlabel(col)
            axes[row, col_pos].set_ylabel('Frequency')
            
        for j in range(num_cols, index * 3):
            fig.delaxes(axes.flatten()[j])

        plt.tight_layout()
        plt.show()


        corr = df_g.iloc[:, 1:].corr()
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="cool", cbar=True, 
                    xticklabels=corr.columns, yticklabels=corr.columns)
        plt.show()