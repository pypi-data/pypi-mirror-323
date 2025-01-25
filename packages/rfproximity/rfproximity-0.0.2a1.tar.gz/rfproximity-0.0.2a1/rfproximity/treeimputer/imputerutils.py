"""
Copyright 2024 BlackRock, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_squared_error
from sklearn.utils.extmath import weighted_mode
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from category_encoders import OneHotEncoder, OrdinalEncoder,BinaryEncoder

class ImputerUtils:
    '''A series of helper functions with some direct copies taken from the Prospect33
    library. Created in mind to help with most any imputation task involing only 
    categroical and numerical variables.

    Methods
    -------
    set_fraction_missing(X:pd.DataFrame, fraction=0.2, random_state=42)                        
        select fraction of data to be randomly missing

    get_num_cat_vars(df: pd.DataFrame)
        get the position of numerical and categorical variables

    mixerror(X_imp: np.ndarray,
             X: np.ndarray,
             X_miss_idx: np.ndarray,
             cat_vars = None)
        combined-error for both categorical and continuous variables

    update(df_column, 
           proximity_matrix, 
           mask_column, 
           is_categorical=False)
        Impute a single variable (column).

    encode(original_dataframe, 
           categorical_ordinal_features = [], 
           cardinality_threshold = 10)
        Build an encoding pipeline for numerical and categorical variables.

    reverse_encoding(encoded_dataframe, 
                    pipeline,
                    numerical_columns,
                    pre_encoding_X_columns)
        Reverse the encoding 

    simple_imputer(proxy_method, 
                   num_indecies, 
                   cat_indecies)
        Uses the Sklearn pipeline to apply simple imputations 

    '''

    def set_fraction_missing(self, X:pd.DataFrame, fraction=0.2, random_state=42):
        '''
            select fraction of data to be randomly missing

            Inputs:
            ------------------------------------------------------------
            X: pd.DataFrame

            fraction: float

            random_state: int

            Outputs:
            ------------------------------------------------------------
            X_miss: pd.Dataframe
                X, but with missing data

            X_miss_idx: np.Dataframe
                A boolean dataframe utilizing the .isnull() function
        '''
        X_miss = X.copy()
        for col in X.columns:
            X_miss.loc[:,col] = X_miss.loc[:,col].sample(frac=1-fraction, random_state=random_state)
            random_state += 1
        X_miss_idx = X_miss.isnull()
        return X_miss, X_miss_idx

    def get_num_cat_vars(self, df: pd.DataFrame):
        '''
            get the position of numerical and categorical variables

            Inputs:
            ------------------------------------------------------------
            df: pd.DataFrame

            Outputs:
            ------------------------------------------------------------
            num_vars: list, numerical variables
            cat_vars: list, categorical variables
        '''
        
        num_vars = []
        cat_vars = []
        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df).infer_objects()
        for col in df.columns:
            if df[col].dtype == 'O':
                cat_vars.append(col)
            else:
                num_vars.append(col)

        return num_vars, cat_vars

    def mixerror(self,
                X_imp: np.ndarray,
                X: np.ndarray,
                X_miss_idx: np.ndarray,
                cat_vars = None):
        '''
        Combined-error for both categorical and continuous variables, 
        Reference: 
        - Tang, F., & Ishwaran, H. (2017). Random forest missing data algorithms. 
        Statistical Analysis and Data Mining: The ASA Data Science Journal, 10(6), 363-377
        
        
        Inputs:
        ------------------------------------------------------------
        X: np.ndarray
        X_true: np.ndarray
        X_miss_idx: where to compare
        cat_vars: bool vector, whether the variable is a categorical variable
        
        
        Output:
        ------------------------------------------------------------
        error: float
        '''
        
        N, nvars = X.shape
        cat_error, num_error = 0, 0

        # identify categorical and continuous variables
        #if cat_vars is None:
        #    num_features, cat_features = get_num_cat_vars(X)
        #else:
        col_list = np.array(range(nvars))
        num_features, cat_features = col_list[~np.array(cat_vars)], col_list[np.array(cat_vars)]
        n_num, n_cat = len(num_features), len(cat_features)
        
        for num in num_features:
            if any(X_miss_idx[:,num]):
                var = np.var(X[X_miss_idx[:,num],num]) # Variance of non missing elements from the column
                if var <= 1e-6:
                    var = 1
                num_error += np.sqrt(mean_squared_error(X_imp[X_miss_idx[:,num],num], X[X_miss_idx[:,num],num]) / var)

        for cat in cat_features:
            if any(X_miss_idx[:,cat]):
                cat_error += np.sum(X_imp[X_miss_idx[:,cat],cat] != X[X_miss_idx[:,cat],cat]) / np.sum(X_miss_idx[:,cat])

        error = 1/max(1, n_cat)*cat_error + 1/max(1, n_num)*(num_error)

        return error



    def update(self,
                df_column, 
                proximity_matrix, 
                mask_column, 
                is_categorical=False):
        ''' 
        Impute a single variable (column).
        
        Parameters
        ----------
        df_column : np.ndarray
            one single variable of X with missing values.
        
        proximity_matrix: np.ndarray
            Proximity matrix got from self.get_proximity. 

        mask_column: np.ndarray
            single column indicating which values were originally present.
            
        
        is_categorical: bool or None
            Whether the variable is a categorical variable. If None, 
            use `self._iscategory_` to determine. 


            Returns
            -------
            column : np.ndarray
                df_column with imputed values applied.
        '''
        column = df_column.copy()
        isnanx = mask_column.copy() # True if missing, False if present 
        # for testing, could include values in the test set too into isnan

        #isnanx = isnanx.T[0]
        n_to_impute = sum(isnanx.astype(int))
        n_known_samples = len(isnanx) - n_to_impute

        if n_known_samples == 0:
            column = np.zeros(column.shape)

        elif n_to_impute > 0:
            # subvector of x without NaN
            present_values = column[~isnanx]
            # determine if categorical variable
            #if catvar is None:
            #    catvar = self._iscategory_(xr)
            weights = proximity_matrix[~isnanx,:][:, isnanx] # shape = (n_known_samples:=len(xr), n_to_impute)

            # some error avoiding stuff
            is0_ = np.sum(weights, axis = 0) == 0
            n0_  = np.sum(is0_.astype(int))

            if n0_ > 0:
                # when proxi = 0 (happens in regression), modify those weights to 1
                weights[:, is0_] = np.ones((n_known_samples, n0_))  

            # replicate xr into matrix with same shape as W
            missing_values_duplicated = np.tile(present_values.reshape(-1,1), 
                                                (1, n_to_impute)) # replicate missing column to have shape (n_to_impute, n_to_impute)
            W = np.copy(weights)

            
            if is_categorical:
                # categorical variable
                column[isnanx] = weighted_mode(missing_values_duplicated, w = W,
                                                axis = 0)[0][0] #still have to deal with one-hot encoding condition
            else:
                # continuous variable
                column[isnanx] = np.average(missing_values_duplicated, weights = W, axis = 0)

        return column

    def convert_boolean_to_string(self,
                                  dataframe):
        ''' 
        Convert all boolean columns to string
        
        Parameters
        ----------
        dataframe : pd.Dataframe
            X dataframe passed in to build pipeline

            Returns
            -------
            dataframe : pd.Dataframe
            Transformed dataframe
        '''
        # Get boolean columns
        bool_cols = dataframe.select_dtypes(include=bool).columns.tolist()
        
        # Convert boolean columns to string
        dataframe[bool_cols] = dataframe[bool_cols].astype(str)
        
        return dataframe


    def encode(self,
                original_dataframe, 
                categorical_ordinal_features = [], 
                cardinality_threshold = 10):
        ''' 
        Build an encoding pipeline for numerical and categorical variables.
        
        Parameters
        ----------
        original_dataframe : pd.Dataframe
            X dataframe passed in to build pipelinr
        
        categorical_ordinal_features: List[str]
            Optional ordinal features parameter

        cardinality_threshold: int
            Threshold for determining if a feature will be OHE or Binary 

            Returns
            -------
            preprocessor, numerical_features : ColumnTransformer
                ColumnTransformer object to apply and later use for decoding guidelines

        numerical_features : List[str]
                Uses the get_num_cat_vars utility function to return numerical_features.
                Had difficulty making the decoder work without explicitly passing this in.
        '''


        numerical_features, categorical_features = self.get_num_cat_vars(original_dataframe)
        transformers = []
        if len(categorical_ordinal_features) != 0:
            categorial_cardinal_features = [column for column in categorical_features if column not in categorical_ordinal_features]
        else:
            categorial_cardinal_features = categorical_features

        n_unique_categories = original_dataframe[categorial_cardinal_features].nunique()
        low_cardinality_features = n_unique_categories[n_unique_categories < cardinality_threshold].index
        high_cardinality_features = n_unique_categories[n_unique_categories >= cardinality_threshold].index

        # Conditionally building the 
        if len(numerical_features) != 0 : # can easily add more transformation conditions other than passthrough
            transformers.append(('numerical_features', 'passthrough', numerical_features))

        if len(high_cardinality_features) != 0:
            categorical_high_cardinality_transformer = Pipeline([ 
                ('binary', BinaryEncoder(handle_missing='return_nan')) 
            ])
            
            transformers.append(('categorical_high_cardinality_features',
                                 categorical_high_cardinality_transformer,
                                 high_cardinality_features))

        if len(low_cardinality_features) != 0:
            categorical_low_cardinality_transformer = Pipeline([
                ('onehot', OneHotEncoder(handle_missing='return_nan'))  # Apply one-hot encoding
            ])
            transformers.append(('categorical_low_cardinality_features',
                                 categorical_low_cardinality_transformer,
                                 low_cardinality_features))

        if len(categorical_ordinal_features) != 0:
            categorical_ordinal_transformer = Pipeline([
                ('ordinal', OrdinalEncoder(handle_missing='return_nan'))  # Apply Ordinal
            ])
            transformers.append(('categorical_ordinal_features',
                                 categorical_ordinal_transformer,
                                 categorical_ordinal_features))

        preprocessor = ColumnTransformer(transformers=transformers) 
        return preprocessor, numerical_features

    def reverse_encoding(self,
                            encoded_dataframe, 
                            pipeline,
                            numerical_columns,
                            pre_encoding_X_columns):
        ''' 
        Reverse the encoding 
        
        Parameters
        ----------
        encoded_dataframe : pd.Dataframe
            X dataframe post encoding
        
        pipeline: ColumnTransfomer
            encoding dataframe to be parsed for it's steps 

        numerical_columns: List[str]
            List of numerical columns

        pre_encoding_X_columns: Index
            original_dataframe.columns to arrange the order of the encoded dataframe to the original one 

            Returns
            -------
            decoded_transformed_data: pd.Dataframe 
                ColumnTransformer object to apply and later use for decoding guidelines

        '''



        encoded_dataframe = encoded_dataframe.copy()
        if len(numerical_columns) != 0:
            all_transformed_columns = [column for column in numerical_columns]
            transformers = list(pipeline.named_transformers_.keys())[1:] #excluding numerical transformer
        else:
            all_transformed_columns = []
            transformers = list(pipeline.named_transformers_.keys())

        for transformer in transformers:
            transformers_columns = list(pipeline.named_transformers_[transformer].get_feature_names_out())
            for column in transformers_columns:
                all_transformed_columns.append(column)

        encoded_dataframe = pd.DataFrame(encoded_dataframe, columns = all_transformed_columns)
        reverse_transformed_dfs = [encoded_dataframe[numerical_columns]]
        for transformer in transformers:
            feature_names = list(pipeline.named_transformers_[transformer].get_feature_names_out())
            reverse_transformed_dfs.append(pipeline.named_transformers_[transformer].inverse_transform(encoded_dataframe[feature_names]))

        decoded_transformed_data = pd.concat(reverse_transformed_dfs, axis = 1)

        # Same order as original inputed dataframe
        decoded_transformed_data = decoded_transformed_data[pre_encoding_X_columns ]
        return decoded_transformed_data


        
    def simple_imputer(self,
                       proxy_method, 
                        num_indecies, 
                        cat_indecies):
        ''' 
        Uses the Sklearn pipeline to apply simple imputations 
        
        Parameters
        ----------
        proxy_method: str
            X dataframe post encoding
        
        num_indecies: List[str]
            encoding dataframe to be parsed for it's steps 

        cat_indecies: List[str]
            List of numerical columns

            Returns
            -------
            simple_imputers: ColumnTransformer
                ColumnTransformer object to apply 

        '''
        if proxy_method == 'median':                   
            numeric_imputer_transformer = Pipeline([('imputer', SimpleImputer(strategy='median'))])
        elif proxy_method == 'mode':
            numeric_imputer_transformer = Pipeline([('imputer', SimpleImputer(strategy='most_frequent'))])
        elif proxy_method == 'mean':
            numeric_imputer_transformer = Pipeline([('imputer', SimpleImputer(strategy='mean'))])
        else:
            numeric_imputer_transformer = Pipeline([('imputer', SimpleImputer(strategy='most_frequent'))])

        categorical_imputer_transformer = Pipeline([('imputer', SimpleImputer(strategy='most_frequent'))])


        simple_imputers = ColumnTransformer(
            transformers=[
                ('numeric_imputer_transformer', numeric_imputer_transformer, num_indecies),
                ('categorical_imputer_transformer', categorical_imputer_transformer, cat_indecies),
        ])
        return simple_imputers