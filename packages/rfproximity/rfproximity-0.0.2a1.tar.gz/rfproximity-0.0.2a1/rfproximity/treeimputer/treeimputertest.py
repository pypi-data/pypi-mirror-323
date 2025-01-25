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
import statistics
from sklearn import ensemble
from typing import List
from pandas import DataFrame
from pandas.core.indexes.base import Index
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import accuracy_score
from rfproximity import TreeProximity
from rfproximity.treeimputer.imputerutils import ImputerUtils

class TreeImputerTest:
    '''Applies K-fold cross validation, removed data based on a user provided 
    percentage trains a sklearn RF, obtains prox matrix from the TreeProximity
    Class, applies updates to X_train, uses learned proximity matrix to then
    apply to the test set as well. Calculates the accuracy of the resulting
    random forest model provided and the mixederror upon each iteration of
    training.

    This class follows the methodology propsed by Jake S. Rhodes, Geometry- and 
    Accuracy-Perserving Random Forest Proximities.

    The primary purpose of this class is to apply these methodologies for 
    datasets with missing data that also have a target varaiable aviable to it
    in the hopes of leveraging supervised random forest models to minimize the
    error between predicted and real values. This is to give the user a better 
    understanding of what to expect when later using the TreeProximity class to 
    impute on real data with no way to measure accuracy. 

        
    Parameters
    ----------
    problem_type: str

    model: ensemble._forest.model
        Indicates model that will be used to pass into the TreeProximity function

    **params: Dict
        Dictonary containing parameters associated with the model chosen to build the forest

    Methods
    -------
    training_pipeline(self, X, y, proxy_method= 'original', 
                      categorical_ordinal_features = [],  
                      random_state=42, 
                      fraction=0.05, 
                      n_splits=5, 
                      cardinality_threshold=10,
                      training_iterations = 5)
        Handles preprocessor and training_pipeline call
    '''

    def __init__(self, problem_type, model, **params):
        
        self.model = model
        self.problem_type = problem_type
        self.params = self.model.get_params()
        self.utils = ImputerUtils()
        self.X_columns: Index
        self.X_train: DataFrame
        self.y_train: DataFrame
        self.X_train_true: DataFrame
        self.X_miss_idx_train: np.ndarray
        self.train_index: np.ndarray
        self.transformed_missing_training_mask : np.ndarray
        self.X_test: DataFrame
        self.y_test: DataFrame
        self.X_test_true: DataFrame
        self.X_miss_idx_test: np.ndarray
        self.test_index: np.ndarray
        self.X_copy: DataFrame
        self.preprocessor: ColumnTransformer
        self.numerical_columns: List[str]
        self.transformed_missing_mask: np.ndarray
        self.index_is_categorical: List[bool]
        self.pre_encoding_index_is_categorical: List[bool]

        self._check_model_and_prob_type()

    def _check_model_and_prob_type(self):
        if not isinstance(self.model, (ensemble._forest.RandomForestClassifier,
                              ensemble._forest.RandomForestRegressor,
                              ensemble._forest.ForestClassifier,
                              ensemble._forest.ForestRegressor,
                              ensemble._forest.ExtraTreesClassifier,
                              ensemble._forest.ExtraTreesRegressor)):
            raise TypeError("Input type must be valid tree based model supported in sklearn")

        if self.problem_type not in ("classification", "regression"):
            raise ValueError("Invalid problem type. It must be 'classification' or 'regression'.")

    def _check_training_pipeline_parameters(self, X, y, proxy_method, categorical_ordinal_features):
        if not isinstance(X, pd.DataFrame):
            raise TypeError("X input must be a Pandas DataFrame.")
        
        if not isinstance(y, pd.Series):
            raise TypeError("y input must be a Pandas Series.")
        
        if proxy_method not in ('mean', 'median', 'mode', 'original', 'oob', 'rfgap'):
            raise ValueError("Invalid imputation type. It must be 'mean', 'median', 'mode', 'original', 'oob', 'rfgap'.")
        
        if not isinstance(categorical_ordinal_features, list):
            raise TypeError("Input for categorical_ordinal_features must be a list.")



    def evaluate_accuracy(self):
        self.model.set_params(**self.params)  
        self.model.fit(self.X_train,self.y_train)
        y_train_pred = self.model.predict(self.X_train)
        y_pred = self.model.predict(self.X_test)

        if self.problem_type == 'classification':
            train_accuracy = accuracy_score(self.y_train, y_train_pred)
            test_accuracy = accuracy_score(self.y_test, y_pred)

        else:# self.problem_type == 'regression':

            train_accuracy = mean_absolute_error(self.y_train, y_train_pred)
            test_accuracy = mean_absolute_error(self.y_test, y_pred)

        # reversing encoding 
        decoded_transformed_test_data = self.utils.reverse_encoding(self.X_test, 
                                                                    self.preprocessor, 
                                                                    self.numerical_columns,
                                                                    self.X_columns)
        
        post_training_test_nan = decoded_transformed_test_data.isnull().to_numpy()

        decoded_transformed_train_data = self.utils.reverse_encoding(self.X_train, 
                                                                     self.preprocessor,
                                                                     self.numerical_columns,
                                                                     self.X_columns)
        
        post_training_train_nan = decoded_transformed_train_data.isnull().to_numpy()

        # Want to apply class average imputer here 
        decoded_transformed_train_data, decoded_transformed_test_data = self.class_average_imputer(post_training_train_nan, 
                                                                                                   post_training_test_nan)
        ######## Hot fix for regression problems ########
        decoded_transformed_train_data = decoded_transformed_train_data.apply(lambda col: col.fillna(col.mode()[0]))
        decoded_transformed_test_data =  decoded_transformed_test_data.apply(lambda col: col.fillna(col.mode()[0]))
        ########################################


        #error calculation
        test_error = self.utils.mixerror(decoded_transformed_test_data.values,
                                         self.X_test_true.values,
                                         self.X_miss_idx_test,
                                         self.pre_encoding_index_is_categorical)
        print("Test Acc:",test_accuracy)
        print("Test Err:", test_error)
        train_error = self.utils.mixerror(decoded_transformed_train_data.values,
                                          self.X_train_true.values,
                                          self.X_miss_idx_train,
                                          self.pre_encoding_index_is_categorical)
        
        print("Train Acc:",train_accuracy)
        print("Train Err:",train_error)
        return test_error, train_error, test_accuracy, train_accuracy


    def training_iteration(self, proxy_method):
        ''' Trains RF, obtains prox matrix, and applied updates to X_train
        
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

        for column_index in range(self.X_train.shape[1]):
            self.X_train[:,column_index] = self.utils.update(self.X_train[:,column_index], 
                                                    proximity_matrix, 
                                                    self.transformed_missing_training_mask[:,column_index], 
                                                    self.index_is_categorical[column_index])
            
        return self.X_train #probably isn't necessary
    
    def class_average_imputer(self, train_nan_index, test_nan_index):
        ''' Trains RF, obtains prox matrix, and applied updates to X_copy.
        Mostly meant to fill any values that had difficulty being decoded 
        via OHE or Binary.
        
            Parameters
            ----------
            dataframe: np.ndarray
                Indicates preferred method of RF imputation

            missing_mask: np.ndarray
                Mask for values that need to be imputed

             Returns
             -------
            self.X_test: np.ndarray or pd.Dataframe
                 self.X_test with class average imputed values applied from 
                 self.X_train.
        '''
        
        def custom_mode(values):
            try:
                return statistics.median(values)
            except:
                return statistics.mode(values)
        
        decoded_train_data = self.utils.reverse_encoding(self.X_train,
                                                         self.preprocessor, 
                                                         self.numerical_columns,
                                                         self.X_columns)
        decoded_train_data['y_column'] = self.y_train
        
        # Have the dataframe for update here 
        class_averages = decoded_train_data.groupby('y_column')[self.X_copy.columns].agg(custom_mode)

        # Applying onto X_train
        decoded_train_data = decoded_train_data.set_index('y_column')
        decoded_train_data[train_nan_index] = np.nan
        decoded_train_data.update(class_averages, overwrite=False)
        decoded_train_data = decoded_train_data.reset_index(drop=True)

        # Applying onto X_test
        decoded_test_data = self.utils.reverse_encoding(self.X_test,
                                                        self.preprocessor, 
                                                        self.numerical_columns,
                                                        self.X_columns)
        decoded_test_data['y_column'] = self.y_test
        decoded_test_data = decoded_test_data.set_index('y_column')
        decoded_test_data[test_nan_index] = np.nan
        decoded_test_data.update(class_averages, overwrite=False)
        decoded_test_data = decoded_test_data.reset_index(drop=True)
        
        return decoded_train_data, decoded_test_data

    def training_and_evaluation_iteration(self, proxy_method):
        ''' Trains RF, obtains prox matrix, and applied updates to X_train
        and X_test
        
            Parameters
            ----------
            proxy_method: str
                Indicates preferred method of RF imputation

             Returns
             -------
             test_error, train_error, test_accuracy, train_accuracy: float
        '''
        self.model.set_params(**self.params)
        self.model.fit(self.X_train, self.y_train)
        X_train_and_test = pd.concat([pd.DataFrame(self.X_train, index = self.train_index), 
                                      pd.DataFrame(self.X_test, index = self.test_index)]).sort_index().to_numpy()
        
        self.leaf_codes = self.model.apply(X_train_and_test)
        prox = TreeProximity(self.leaf_codes)
        
        if 'gap' in proxy_method:
            proximity_matrix = prox.proximity_matrix_gap(self.model,
                                                         self.X_train.shape[0])
        elif 'oob' in proxy_method:
            proximity_matrix = prox.proximity_matrix_oob(self.model,
                                                         self.X_train.shape[0])
        else:
            proximity_matrix =  prox.proximity_matrix()

        proximity_matrix[np.isnan(proximity_matrix)] = 0
        
        # This line must not be enough to exclude the test values from ebing included in the calulation 
        proximity_matrix[self.test_index,:][:, self.test_index] = 0  
        # Updating every column (vectorized at the column level) need to remember if only the test indexes are update or all
        for column_index in range(X_train_and_test.shape[1]):
            X_train_and_test[:,column_index] = self.utils.update(X_train_and_test[:,column_index],
                                                                 proximity_matrix,
                                                                 self.transformed_missing_mask[:,column_index],
                                                                 self.index_is_categorical[column_index])

        self.X_test = X_train_and_test[self.test_index]
        self.X_train = X_train_and_test[self.train_index]
        test_error, train_error, test_accuracy, train_accuracy = self.evaluate_accuracy()
        
        return test_error, train_error, test_accuracy, train_accuracy
        
    def evaluate_imputer(self, proxy_method, training_iterations):
        ''' Trains RF, obtains prox matrix, and applied updates to X_train
        and X_test
        
            Parameters
            ----------
            proxy_method: str
                Indicates preferred method of RF imputation

            training_iterations: int
                Number of iterations that the user wants to do on the trianing/test sets

             Returns
             -------
             X_copy: np.ndarray or pd.Dataframe
                 X_copy with class average imputed values applied.
        '''

        all_results = []
        if proxy_method in ['mean','median','mode']:            
            test_error, train_error, test_accuracy, train_accuracy = self.evaluate_accuracy()
            all_results.append([0, test_error, train_error, test_accuracy, train_accuracy])
            return all_results

        # Need to update values 5 times according to literature
        elif proxy_method in ['original', 'oob', 'rfgap']: 
            for update_iteration in range(training_iterations):
                print(update_iteration)
                test_error, train_error, test_accuracy, train_accuracy = self.training_and_evaluation_iteration(proxy_method)
                all_results.append([update_iteration, test_error, train_error, test_accuracy, train_accuracy])
                
        return all_results

    # Might need one more to wrap everything nicely and only require the input of X, y, train_index, test_index
    def training_pipeline(self, 
                          X, 
                          y, 
                          proxy_method= 'original', 
                          categorical_ordinal_features = [],  
                          random_state=42, 
                          fraction=0.20, 
                          n_splits=5, 
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
             training_results: List[List[float]]
                 List[all_results]
        '''
        self._check_training_pipeline_parameters(X, y, proxy_method, categorical_ordinal_features)

        self.categorical_ordinal_features = categorical_ordinal_features
        if self.problem_type == "classification":
            splitter = StratifiedKFold(n_splits = n_splits, shuffle = True, random_state = random_state)
        else:
            splitter = KFold(n_splits = n_splits, shuffle = True, random_state = random_state)

        self.X_copy = X.copy()
        self.X_copy = self.utils.convert_boolean_to_string(self.X_copy)
        self.X_columns = self.X_copy.columns
        X_miss, X_miss_idx = self.utils.set_fraction_missing(X, fraction = fraction, random_state = random_state)
        training_results = []

        for fold, (self.train_index, self.test_index) in enumerate(splitter.split(X_miss, y)):
            print(f'    - fold-{fold+1}/{n_splits}')
            self.X_train_true = X.iloc[self.train_index]
            self.X_train = X_miss.iloc[self.train_index]
            self.y_train = y.iloc[self.train_index]

            self.X_test_true = X.iloc[self.test_index]
            self.X_test = X_miss.iloc[self.test_index]
            self.y_test = y.iloc[self.test_index]

            # Need both these masks to update values properly 
            self.X_miss_idx_train = self.X_train.isnull().to_numpy()
            self.X_miss_idx_test = self.X_test.isnull().to_numpy()

            _, cat_vars = self.utils.get_num_cat_vars(self.X_copy)
            self.pre_encoding_index_is_categorical = [True if column in cat_vars else False for column in self.X_copy.columns]

            self.preprocessor, self.numerical_columns= self.utils.encode(self.X_copy, categorical_ordinal_features, cardinality_threshold)

            # Transforming all data before simple imputation to make an accurate mask of values to update
            self.X_train =  self.preprocessor.fit_transform(self.X_train)
            self.transformed_missing_training_mask = np.isnan(self.X_train)

            self.X_test =  self.preprocessor.transform(self.X_test)
            transformed_missing_test_mask = np.isnan(self.X_test)
            
            transformed_data = self.preprocessor.transform(X_miss)
            self.transformed_missing_mask = np.isnan(transformed_data)

            # Simple imputer based on whether a column is categorical or numerical 
            num_indecies = list(range(len(self.numerical_columns)))
            cat_indecies = list(range(len(self.numerical_columns), transformed_data.shape[1]))
            # Boolean mask used for updating 
            self.index_is_categorical = [True if index in cat_indecies else False for index in range(transformed_data.shape[1])]
            self.simple_imputers = self.utils.simple_imputer(proxy_method, num_indecies, cat_indecies)

            # Fit and transform the data
            self.X_train = self.simple_imputers.fit_transform(self.X_train)
            self.X_test = self.simple_imputers.transform(self.X_test)
            all_results = self.evaluate_imputer(proxy_method, training_iterations)
            training_results.append([proxy_method, fraction, all_results])
        return training_results
    

    