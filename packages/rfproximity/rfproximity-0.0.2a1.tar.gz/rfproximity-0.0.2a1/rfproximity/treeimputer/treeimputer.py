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

import copy
import statistics
import pandas as pd
import numpy as np
from typing import List
from sklearn import ensemble
from pandas import DataFrame
from pandas.core.indexes.base import Index
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from rfproximity import TreeProximity
from rfproximity.treeimputer.imputerutils import ImputerUtils
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning) 
np.seterr(invalid='ignore')

class TreeImputer:
    '''Trains a sklearn RF, obtains prox matrix from the TreeProximity Class,
    and applies updates to X_copy following the methodology propsed by Jake 
    S. Rhodes, Geometry- and Accuracy-Perserving Random Forest Proximities.

    The primary purpose of this class is to apply these methodologies for 
    datasets with missing data that also have a target varaiable aviable to it
    in the hopes of leveraging supervised random forest models to minimize the
    error between predicted and real values. 

    For accuracy/error approximations see TreeImputerTest
        
    Parameters
    ----------
    model: ensemble._forest.model
        Indicates model that will be used to pass into the TreeProximity function

    **params: Dict
        Dictonary containing parameters associated with the model chosen to build the forest

    Methods
    -------
    imputer_pipeline(X,
                    y,  
                    proxy_method= 'original',  
                    categorical_ordinal_features = [],  
                    cardinality_threshold=10, 
                    training_iterations = 5)
                             
    Handles preprocessor and training_pipeline call

    '''
    
    def __init__(self, model, **params):
        self.model = model
        self.params = self.model.get_params()
        self.utils = ImputerUtils()
        self.X_copy: DataFrame
        self.y_copy: DataFrame
        self.X_miss_idx: np.ndarray
        self.transformed_missing_mask: np.ndarray
        self.X_columns: Index
        self.preprocessor: ColumnTransformer
        self.numerical_columns: List[str]
        self.index_is_categorical: List[bool]

        self._check_model()

    def _check_model(self):
        if not isinstance(self.model, (ensemble._forest.RandomForestClassifier,
                              ensemble._forest.RandomForestRegressor,
                              ensemble._forest.ForestClassifier,
                              ensemble._forest.ForestRegressor,
                              ensemble._forest.ExtraTreesClassifier,
                              ensemble._forest.ExtraTreesRegressor)):
            raise TypeError("Input type must be valid tree based model supported in sklearn")
        
    def _check_impute_pipeline_parameters(self, X, y, proxy_method, categorical_ordinal_features):
        if not isinstance(X, pd.DataFrame):
            raise TypeError("Input 'data' must be a Pandas DataFrame.")
        
        if not isinstance(y, pd.Series):
            raise TypeError("Input 'data' must be a Pandas DataFrame.")
        
        if proxy_method not in ('mean', 'median', 'mode', 'original', 'oob', 'rfgap'):
            raise ValueError("Invalid imputation type. It must be 'mean', 'median', 'mode', 'original', 'oob', 'rfgap'.")
        
        if not isinstance(categorical_ordinal_features, list):
            raise TypeError("Input for categorical_ordinal_features must be a list.")
    
 

    def training_iteration(self,
                           proxy_method):
        ''' Trains RF, obtains prox matrix, and applied updates to X_copy
        
            Parameters
            ----------
            proxy_method: str
                Indicates preferred method of RF imputation

             Returns
             -------
             X_copy: np.ndarray
                 df_column with imputed values applied.
        '''

        self.model.set_params(**self.params)
        self.model.fit(self.X_copy, self.y_copy)
        self.leaf_codes = self.model.apply(self.X_copy)
        prox = TreeProximity(self.leaf_codes)
        
        if 'gap' in proxy_method:
            proximity_matrix = prox.proximity_matrix_gap(self.model,
                                                         self.X_copy.shape[0])
        elif 'oob' in proxy_method:
            proximity_matrix = prox.proximity_matrix_oob(self.model,
                                                         self.X_copy.shape[0])
        else:
            proximity_matrix =  prox.proximity_matrix()

        for column_index in range(self.X_copy.shape[1]):
            self.X_copy[:,column_index] = self.utils.update(self.X_copy[:,column_index],
                                                            proximity_matrix,
                                                            self.transformed_missing_mask[:,column_index],
                                                            self.index_is_categorical[column_index])
        return self.X_copy #probably isn't necessary
    
    def class_average_imputer(self,
                              dataframe, 
                              missing_mask):
        ''' Trains RF, obtains prox matrix, and applied updates to X_copy.
        Mostly meant to fill any values that had difficulty being decoded 
        via OHE or Binary
        
            Parameters
            ----------
            dataframe: np.ndarray
                Indicates preferred method of RF imputation

            missing_mask: np.ndarray
                Mask for values that need to be imputed

             Returns
             -------
             X_copy: np.ndarray or pd.Dataframe
                 X_copy with class average imputed values applied.
        '''
        # quick function to apply .agg on 
        def custom_mode(values):
            try:
                return statistics.median(values)
            except:
                return statistics.mode(values)
        # Making a seperate dataframe with aggregated class values to apply to X
        decoded_X = self.utils.reverse_encoding(dataframe,
                                                self.preprocessor,
                                                self.numerical_columns,
                                                self.X_columns)
        
        decoded_X['y_column'] = self.y_copy
        decoded_X_copy = copy.deepcopy(decoded_X)
        
        class_averages = decoded_X.groupby('y_column')[self.X_columns].agg(custom_mode)
        
        decoded_X_copy = decoded_X_copy.set_index('y_column')
        decoded_X_copy[missing_mask] = np.nan
        
        decoded_X_copy.update(class_averages, overwrite=False)
        decoded_X_copy = decoded_X_copy.reset_index(drop=True)

        self.X_copy = decoded_X_copy
        
        return self.X_copy
    
    def training_pipeline(self,
                          proxy_method,
                          training_iterations):
        ''' A series of logical statments defined by the proxy_method
        
            Parameters
            ----------
            proxy_method: str
                Indicates preferred method of imputation

            training_iterations:
                Number of iterations for the RF imputer

             Returns
             -------
             X_copy: np.ndarray or pd.Dataframe
                 X_copy with class average imputed values applied.
        '''

        if proxy_method in ['mean','median','mode']:
            self.X_copy = self.utils.reverse_encoding(self.X_copy,
                                                      self.preprocessor,
                                                      self.numerical_columns,
                                                      self.X_columns)
            return self.X_copy
        
        elif proxy_method in ['original', 'oob', 'rfgap']: 
            for _ in range(training_iterations):
                self.X_copy = self.training_iteration(proxy_method)

#                if only_class_imputer == True:
#                    self.X_copy = self.class_average_imputer(self.X_copy, self.X_miss_idx, return_encoded = True)

        # Dealing with any left over nan values as a result of decoding 
        temp_X = self.utils.reverse_encoding(self.X_copy,
                                             self.preprocessor,
                                             self.numerical_columns,
                                             self.X_columns)
        post_training_nan = temp_X.isnull().to_numpy()

        self.X_copy = self.class_average_imputer(self.X_copy, post_training_nan)
        #### Hotfix for regression ###
        self.X_copy = self.X_copy.apply(lambda col: col.fillna(col.mode()[0]))
        return self.X_copy


    # Might need one more to wrap everything nicely and only require the input of X, y, train_index, test_index
    def imputer_pipeline(self, 
                         X, 
                         y,  
                         proxy_method= 'original',  
                         categorical_ordinal_features = [],  
                         cardinality_threshold=10, 
                         training_iterations = 5):
                             
        ''' Handles preprocessor and training_pipeline call
        
            Parameters
            ----------
            X: pd.Dataframe
                Dataframe that requires imputation

            y: pd.Series
                Target variable
                
            proxy_method: str
                Indicates preferred method of imputation

            categorical_ordinal_features: List[str]
                Optional ordinal features parameter
                
            cardinality_threshold: int
                Threshold for determining if a feature will be OHE or Binary

            training_iterations: int
                Number of imputation iterations for the RF imputer
                

             Returns
             -------
             X_copy: np.ndarray or pd.Dataframe
                 X_copy with class average imputed values applied.
        '''
        self._check_impute_pipeline_parameters(X, y, proxy_method, categorical_ordinal_features)

        self.X_copy = X.copy()
        self.X_copy = self.utils.convert_boolean_to_string(self.X_copy)
        self.X_columns = self.X_copy.columns
        self.y_copy = y.copy()

        # Need both these masks to update values properly 
        self.X_miss_idx= self.X_copy.isnull().to_numpy()

        self.preprocessor, self.numerical_columns= self.utils.encode(self.X_copy,
                                                                     categorical_ordinal_features,
                                                                     cardinality_threshold)

        # Transforming all data before simple imputation to make an accurate mask of values to update
        self.X_copy =  self.preprocessor.fit_transform(self.X_copy)
        self.transformed_missing_mask = np.isnan(self.X_copy)

        # Simple imputer based on whether a column is categorical or numerical 
        num_indecies = list(range(len(self.numerical_columns)))
        cat_indecies = list(range(len(self.numerical_columns), self.X_copy.shape[1]))

        # Boolean mask used for updating 
        self.index_is_categorical = [True if index in cat_indecies else False for index in range(self.X_copy.shape[1])]
        simple_imputers = self.utils.simple_imputer(proxy_method,
                                                    num_indecies,
                                                    cat_indecies)

        # Fit and transform the data
        self.X_copy = simple_imputers.fit_transform(self.X_copy)

        self.X_copy = self.training_pipeline(proxy_method, training_iterations)
        return self.X_copy
            