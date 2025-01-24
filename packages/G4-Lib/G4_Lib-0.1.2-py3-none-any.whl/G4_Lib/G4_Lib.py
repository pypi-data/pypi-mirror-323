import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import LabelEncoder

class InvalidMethodError(Exception):
    # Custom exception for invalid method selection
    pass
class InvalidParameterError(Exception):
    # Custom exception for invalid parameter values
    pass

class DataStructure():
    def __init__(self, df, lim_nan=65, m_obj='mode', m_num='mean', threshold=3):
        if not isinstance(lim_nan, (int, float)):
            raise InvalidParameterError(f"The limit of NaN values in a column must be a number. Received {type(lim_nan).__name__}.")
        
        self.df = pd.DataFrame(df)
        self.lim_nan = lim_nan
        self.m_obj = m_obj
        self.m_num = m_num
        self.threshold = threshold

    def EncodeColumn(self,index,cond):
        try:
            # Validate the column index
            if index < 0 or index >= len(self.df.columns):
                raise ValueError(f"Invalid column index: {index}. Must be between 0 and {len(self.df.columns) - 1}.")
            # Validate the condition
            if cond not in ['Y', 'N']:
                raise ValueError(f"Invalid value for cond: '{cond}'. Must be 'Y' or 'N'.")

            col_name = self.df.columns[index]
            label_encoder = LabelEncoder()
            encoded_values = label_encoder.fit_transform(self.df[col_name])

            if cond == 'N':  # Replace the original column
                self.df[col_name] = encoded_values
            else:  # Add a new column
                new_col_name = f"{col_name}_encoded"
                if new_col_name in self.df.columns:
                    raise KeyError(f"Column '{new_col_name}' already exists in the DataFrame.")
                self.df[new_col_name] = encoded_values

        except Exception as e:
            print(f"An error occurred: {e}")

    def DropColumn(self,index):
        try:
            col = self.df.columns
            self.df.drop(columns=col[index], inplace=True)
        except IndexError:
            print('The index is out of range. Try again.')

    def HomogenizeData(self):
        col = self.df.columns
        for j in range(len(self.df.columns)):
            if self.df[col[j]].dtype == 'object':
                self.df[col[j]] = self.df[col[j]].str.lower()
                self.df[col[j]] = self.df[col[j]].str.strip()

    def CleanData(self):
        try: 
            col = self.df.columns
            for i in range(len(col)):
                if (self.df[col[i]].isna().mean() * 100) <= self.lim_nan:  # columns with LESS than 65% nan

                    if self.df[col[i]].dtype == 'object':  # columns of OBJECT type

                        if self.m_obj == 'mode':  # standard
                            self.df[col[i]].fillna(self.df[col[i]].mode()[0], inplace=True)
                        elif self.m_obj == 'bfill':
                            self.df[col[i]].fillna(self.df[col[i]].bfill())
                        elif self.m_obj == 'ffill':
                            self.df[col[i]].fillna(self.df[col[i]].ffill())

                        else:
                            raise InvalidMethodError(f"Invalid method '{self.m_obj}' for object-type columns. Choose from 'mode', 'bfill' and 'ffill'.")

                    else:  # columns of NUMERICAL type (int and float)

                        z = np.abs(stats.zscore(self.df[col[i]]))
                        self.threshold = 3 # standard
                        self.df.loc[z > self.threshold, col[i]] = self.df[col[i]].median()

                        if self.m_num == 'mean':  # standard
                            self.df[col[i]].fillna(self.df[col[i]].mean(), inplace=True)
                        elif self.m_num == 'median':
                            self.df[col[i]].fillna(self.df[col[i]].median(), inplace=True)
                        elif self.m_num == 'mode':
                            self.df[col[i]].fillna(self.df[col[i]].mode()[0], inplace=True)
                        elif self.m_num == 'bfill':
                            self.df[col[i]].fillna(self.df[col[i]].bfill(), inplace=True)
                        elif self.m_num == 'ffill':
                            self.df[col[i]].fillna(self.df[col[i]].ffill(), inplace=True)
                        elif self.m_num == 'max':
                            self.df[col[i]].fillna(self.df[col[i]].max(), inplace=True)
                        elif self.m_num == 'min':
                            self.df[col[i]].fillna(self.df[col[i]].min(), inplace=True)

                        else:
                            raise InvalidMethodError(f"Invalid method '{self.m_num}' for numerical columns. Choose from 'mean', 'median', 'mode', 'bfill', 'ffill', 'max' and 'min'.")

                else:  # columns with MORE than 65% nan
                    self.df.drop(columns=col[i], inplace=True)

                print('The DataFrame preprocessing is done!')

        except (InvalidMethodError, InvalidParameterError) as e:
            print(e)