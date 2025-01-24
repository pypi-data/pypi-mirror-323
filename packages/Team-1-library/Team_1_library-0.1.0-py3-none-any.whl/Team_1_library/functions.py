import pandas as pd
from scipy import stats
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder, StandardScaler
import warnings
from fuzzywuzzy import process
warnings.simplefilter(action='ignore', category=FutureWarning)  ##It disables the warnings in the monitor


def _clustering_imputations(df, col, numeric_var, object_var):
    X = df.copy()

    fill_methods = {
    'mode':  lambda: X[column].fillna(X[column].dropna().mode()[0], inplace=True),
    'ffill': lambda: X[column].ffill(inplace=True),
    'bfill': lambda: X[column].bfill(inplace=True),
}
    for column in X.columns:

        #Filling the copied matrix NaNs with desired variables
        fill_function = fill_methods.get(object_var)
        
        if fill_function:
            fill_function() 

        #Encoding objects
        if X[column].dtype == 'object':   
            le = LabelEncoder()
            X[column] = le.fit_transform(X[column].astype(str))
    
    X = X.drop(columns=[col])  # Exclude the objective column

    # Data sacling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Number of clusters depending on unique values
    n_clusters = df[col].nunique()  
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df['cluster'] = kmeans.fit_predict(X_scaled)  #Cluster creation
    # Impute the values depending on clusters
    for cluster in df['cluster'].unique():
        cluster_rows = df[df['cluster'] == cluster]
        if not cluster_rows[col].isna().all():  # Avoid clusters with no data
            mode_value = cluster_rows[col].mode()[0]  # Cluster's mode
            df.loc[(df['cluster'] == cluster) & (df[col].isna()), col] = mode_value
        else: 
            print('Cluster not encountered for column "%s", imputing statistical variable'%(col))
            df = _statistical_imputation(df,col,numeric_var,object_var)

    # Eliminate cluster column
    df.drop(columns=['cluster'], inplace=True)

    return df

def _statistical_imputation(df,col, numeric_var, object_var):
    col_type =df[col].dtype
    fill_methods = {
        'mean': lambda: df[col].fillna(df[col].mean(),inplace=True),
        'median': lambda: df[col].fillna(df[col].median(),inplace=True),
        'mode':  lambda: df[col].fillna(df[col].mode()[0],inplace=True),
        'ffill': lambda: df[col].ffill(inplace=True),
        'bfill': lambda: df[col].bfill(inplace=True),
}
    if col_type == int  or col_type == float:
        ##FILLNA
        fill_function = fill_methods.get(numeric_var)
        
        if fill_function:
            fill_function()   
        else: print('Error with fill function')   

    elif col_type == object or col_type == bool:
        ##FILLNA

        fill_function = fill_methods.get(object_var)
        
        if fill_function:
            fill_function() 
        else: print('Error with fill function')   
        
    return df
                
def _corregir_outliers(df,col):       ##Outlier correction

    if df[col].dtype == int  or df[col].dtype == float:

        z_scores = stats.zscore(df[col])
        df[col] = df[col].where(abs(z_scores) < 2.2, df[col].mean())

    return df

def _drop_column_if_low_variance(df, col, threshold):

    # only compute in numeric columns
    if pd.api.types.is_numeric_dtype(df[col]):
        col_var = df[col].var()
        if col_var <= threshold:
            df.drop(columns=[col], inplace=True)
            print(f'Column "{col}" deleted due to low variance: ({col_var:.4f}).')
    
    return df


class Automatic_Preprocess:

    def __init__(self,df_original, empty_threshold=0.65, variance_threshold=0.0 ,clustering=True, numeric_var='mean',object_var='mode'):

        self.df = df_original.copy()
        self.empty_threshold = empty_threshold
        self.variance_threshold = variance_threshold
        self.numeric_var = numeric_var
        self.object_var = object_var

        if isinstance(clustering, bool):    #If is bool. fill column size array with bool
                    self.clustering = np.full(len(self.df.columns), clustering)

        elif isinstance(clustering, list):  #If list, we check size is correct
            if len(clustering) != len(self.df.columns):
                raise ValueError("List of clustering must be equal size to df columns")
            self.clustering = np.array(clustering)

        else:
            raise ValueError("Parameter 'clustering' must be boolean or array of booleans")

    def run(self):

        for col in self.df.columns:         
            nan_perc = self.df[col].isna().mean()
            ##Drop the column if empty threshold reached
            if nan_perc > self.empty_threshold:
                self.df.drop(columns=[col],inplace=True)
                print(f'Column deleted due to excess of NaN ({nan_perc*100:.2f}%).')
                continue
            ##Drop column if varience threshold surpassed
            self.df = _drop_column_if_low_variance(self.df,col, self.variance_threshold)


        for index, col in enumerate(self.df.columns):
            if self.clustering[index] == True:  #If true for that column, imput by clustering
                self.df = _clustering_imputations(self.df,col,self.numeric_var,self.object_var)
            
            else:
                self.df = _statistical_imputation(self.df,col,self.numeric_var,self.object_var)
            self.df = _corregir_outliers(self.df,col)
        return self.df
    

class Manual_Preprocess:
    """Preprocess Functions"""
    def __init__(self, df):
        self.df = df


##AUXILIAR FUNCTIONS:
    def _correct_string(self,value,correct_values):

        best_coincidence, score = process.extractOne(value, correct_values)

        return best_coincidence if score >= 70 else value

    def _get_correct_values(self,values):

        correct_values = [values[0]]

        for val in values:
            best_coincidence, score = process.extractOne(val, correct_values)

            if score < 70:
                correct_values.append(val)
                
        return correct_values


##PRINCIPAL_FUNCTIONS:
    def turn_positive(self, selected_columns):
        try:

            for col in selected_columns:
                self.df[col] = self.df[col].apply(lambda x: -x if x < 0 else x)

        except Exception as e:
            print(f"An error ocurred: {e}")

        return self.df
    
    def fill_nan(self, selected_columns, var='mean'):
        """Fills a column NaN's with different statistical variables.
        
        Args:

            selected_columns (list): List of column's names where apply the function
            var (string): Name of the statistical variable to replace the NaN's
        
        Returns:

            Modified dataframe 
        """   
        try:
            if var == 'mean':
                for col in selected_columns:
                    self.df[col].fillna(self.df[col].mean(), inplace=True)

            elif var == 'median':
                for col in selected_columns:
                    self.df[col].fillna(self.df[col].median(), inplace=True)

            elif var =='mode':
                for col in selected_columns:
                    self.df[col].fillna(self.df[col].mode()[0], inplace=True)

            elif var == 'ffill':
                for col in selected_columns:
                    self.df[col].fillna(method='ffill')

            elif var == 'bfill':
                for col in selected_columns:
                    self.df[col].fillna(method='bfill')

        except Exception as e:
            print(f"An error ocurred: {e}")
        
        return self.df

    def correct_outliers(self, selected_columns):
        """Corrects the outliers based on their zscore.
        
        Args:
            selected_columns (list): List of column's names where apply the function
        
        Returns:
            Modified dataframe 
        """
        try:
            for col in selected_columns:
                z_scores = stats.zscore(self.df[col])  # Calcular los z-scores
                mask = abs(z_scores) < 2.2  # Máscara para valores dentro del umbral
                mean_without_outliers = self.df[col][mask].mean()  # Media sin outliers
                self.df[col] = self.df[col].where(mask, mean_without_outliers)  # Reemplazo de outliers

        except Exception as e:
            print(f"An error ocurred: {e}")

        return self.df

    def correct_string_errors(self,selected_columns,correct_values=None):
        """Corrects strings with theorical errors approximating them to the most used similar ones.
        
        Args:

            selected_columns (list): List of column's names where apply the function
            correct_values (list): List of the correct values to approximate (if not given it choose automatically)
        
        Returns:

            Modified dataframe 
        """
        try:
            i = 0
            for col in selected_columns:
                i += 1
                if self.df[col].dtype == object:
                    try:
                        if correct_values is not None:
                            self.df[col] = self.df[col].apply(lambda x: self._correct_string(x,correct_values[i]))
                        else:
                            sorted_values = self.df[col].value_counts(ascending=False)
                            values = sorted_values.index

                            correct_values = self._get_correct_values(values)
                            

                            self.df[col] = self.df[col].apply(lambda x: self._correct_string(x,correct_values))
                            correct_values = None
                    except: print('NaN number found, fill the NaN before correcting string')
                else: print(f'Column "{col}" omited due to not string.')

        except Exception as e:
            print(f"An error ocurred: {e}")

        return self.df
    
    def normalize_string(self,selected_columns):
        """Lowers the cases and eliminates the blank spaces of the colum's strings.
        
        Args:

            selected_columns (list): List of column's names where apply the function
        
        Returns:

            Modified dataframe 
        """      
        try:  
            for col in selected_columns:
                self.df[col] = self.df[col].str.strip()
                self.df[col] = self.df[col].str.lower()

        except Exception as e:
            print(f"An error ocurred: {e}")

        return self.df
