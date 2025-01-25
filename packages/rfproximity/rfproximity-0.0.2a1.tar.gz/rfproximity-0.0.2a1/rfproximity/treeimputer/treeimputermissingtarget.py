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
from sklearn.model_selection import GridSearchCV
from rfproximity.treeimputer.imputerutils import * 

utils = ImputerUtils()

class TreeImputerMissingTarget:
    '''This class takes historical training data and uses it to make predictions
    on unlabeled test data and apply imputation based on those results. This is 
    done by taking the training set, doing a separate calculation for the class 
    based averages on all the features, then taking the test set and duplicating
    each row for every unique class in the training set and applying the class
    bassed average onto the resulting missing values. Then a model is trained on 
    the training data and fit to the duplicated test set. the test set is then 
    grouped back to it's original state and polled on the class where the class 
    with the most votes is deemed the "true" class. Based on these true classes, 
    the class based averages are then applied.

    This class follows the methodology propsed by Leo Breiman and Adele Cutler.
    https://www.stat.berkeley.edu/~breiman/RandomForests/cc_home.htm#missing2

    The primary purpose of this class is to apply these methodologies for 
    datasets with missing data that do not have a target varaiable available to it,
    but clean historical data exists.So that we can leverage supervised random 
    forest models to minimize the error between predicted and real values.

        
    Parameters
    ----------
    problem_type: str

    model: ensemble._forest.model
        Indicates model that will be used to pass into the TreeProximity function

    **params: Dict
        Dictonary containing parameters associated with the model chosen to build the forest

    Methods
    -------
    param_grid = {
        'n_estimators': [100, 200, 300, 500],
        'max_depth': [None, 10, 20],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2, 4],
        'max_features':["sqrt","log2"],
        'class_weight': ['balanced']
    }
    class_test = TreeImputerMissingTarget(RandomForestClassifier(), 'classification', **param_grid)
    final_predictions, params_and_results = class_test.imputer_pipeline(X, X_miss, 'class')
    '''
    def __init__(self, problem_type, model, y_column_name,  **param_grid):
        self.model = model
        self.problem_type = problem_type
        self.y_column_name: y_column_name
        self.param_grid = param_grid 
        self.utils = ImputerUtils()
        self.data_df: pd.DataFrame
        self.missing_values_df: pd.DataFrame

        #self._check_model_and_prob_type()

    def _check_model_and_prob_type(self):
        if not isinstance(self.model, (ensemble._forest.RandomForestClassifier,
                              ensemble._forest.RandomForestRegressor,
                              ensemble._forest.RandomForestClassifier,
                              ensemble._forest.ForestRegressor,
                              ensemble._forest.ExtraTreesClassifier,
                              ensemble._forest.ExtraTreesRegressor)):
            raise TypeError("Input type must be valid tree based model supported in sklearn")

        if self.problem_type not in ("classification", "regression"):
            raise ValueError("Invalid problem type. It must be 'classification' or 'regression'.")

    def _check_training_pipeline_parameters(self, data_df, missing_values_df, y_column_name):
        if not isinstance( data_df, pd.DataFrame):
            raise TypeError(" data_df input must be a Pandas DataFrame.")
        
        if not isinstance( missing_values_df, pd.DataFrame):
            raise TypeError(" data_df input must be a Pandas DataFrame.")
        
        if not isinstance(y_column_name, str):
            raise TypeError("y_column_name input must be a string.")


    def class_averages_imputer(self, data_df, missing_values_df):
        ''' Aggregate values based on target variable class in the data_df to fill in missing
            values in the missing_values_df.
        
            Parameters
            ----------
            data_df : pd.DataFrame
                Dataframe with clean data 
            
            missing_values_df: pd.DataFrame
                Dataframe with missing data

             Returns
             -------
             missing_values_df_copy : pd.DataFrame
                 missing_values_df with imputed values applied.
        '''
        def custom_mode(values):
            try:
                return statistics.median(values) # Noteable cavieat: will not take avg of two values if rows num is even
            except:
                return statistics.mode(values)
        
        class_averages = data_df.groupby(self.y_column_name)[data_df.columns].agg(custom_mode).drop(columns=[self.y_column_name])
        missing_values_df_copy = missing_values_df.copy()
        # Matching index of missing so it can work with update
        missing_values_df_copy = missing_values_df_copy.set_index(self.y_column_name)
        missing_values_df_copy.update(class_averages, overwrite=False)
        # Putting in to the same format as before
        missing_values_df_copy = missing_values_df_copy.reset_index()[data_df.columns]#.drop(columns = y_column)

        return missing_values_df_copy#, class_averages
    
    def regression_averages_imputer(self, data_df, missing_values_df):
        ''' Applies binning and aggregates values based on binned target variable in the data_df to fill in missing
            values in the missing_values_df.
        
            Parameters
            ----------
            data_df : pd.DataFrame
                Dataframe with clean data 
            
            missing_values_df: pd.DataFrame
                Dataframe with missing data

             Returns
             -------
             missing_values_df_copy : pd.DataFrame
                 missing_values_df with imputed values applied.
        '''
        
        def custom_mode(values):
            try:
                return statistics.median(values) # Noteable cavieat: will not take avg of two values if rows num is even
            except:
                return statistics.mode(values)
        def binning_processor(base_df, y_column_name, number_of_bins):
            min_edge = min(base_df[y_column_name])
            max_edge = max(base_df[y_column_name])
            step = (max_edge-min_edge)/number_of_bins
            bin_edges = list(np.arange(min_edge,max_edge, step))
            base_df_binned_feature = np.digitize(base_df[y_column_name], bins=bin_edges)
            base_df["binned_feature"] = base_df_binned_feature
            return base_df
        
        missing_values_df_copy = missing_values_df.copy()
        data_df = binning_processor(data_df, self.y_column_name, self.number_of_bins).drop(columns=[self.y_column_name])
        class_averages = data_df.groupby("binned_feature")[data_df.columns].agg(custom_mode).drop(columns=["binned_feature"])

        # Matching index of missing so it can work with update
        missing_values_df_copy = missing_values_df_copy.set_index("binned_feature")
        missing_values_df_copy.update(class_averages, overwrite=False)
        # Putting in to the same format as before
        missing_values_df_copy = missing_values_df_copy.reset_index()[data_df.columns]#.drop(columns = y_column)

        return missing_values_df_copy, data_df["binned_feature"]

    def duplicate_rows(self, missing_values_df, full_y_column):
        ''' Duplicate missing_values_df rows based on number of unique classes.
        
            Parameters
            ----------
            
            missing_values_df: pd.DataFrame
                Dataframe with missing data

            full_y_column: pd.Series
                Target variable column in clean dataset

             Returns
             -------
            missing_values_df_copy : pd.DataFrame
                missing_values_df with rows duplicated.

            row_num_group_column : pd.Series
                Column indicating which duplicated row it originally belonged to 
        '''

        if self.problem_type == "classification":
            every_y_column = [full_y_column.unique().tolist()] * missing_values_df.shape[0]
        else:
            every_y_column = [list(range(1,self.number_of_bins))] * missing_values_df.shape[0]

        missing_values_df[self.y_column_name] = every_y_column
        missing_values_df = missing_values_df.explode(self.y_column_name).reset_index()
        missing_values_df = missing_values_df.rename(columns={'index':'row_num_group'})
        row_num_group_column = missing_values_df['row_num_group']
        missing_values_df = missing_values_df.drop(columns=['row_num_group'])
        if self.problem_type != "classification":
            missing_values_df = missing_values_df.rename(columns={self.y_column_name:'binned_feature'})
        return missing_values_df, row_num_group_column

    def impute_results(self, data_df, missing_df, missing_df_copy, y_pred, row_num_group_column):
        ''' Poll predicted results based on row_num_group_column and apply imputation based on 
            resulting class.
        
            Parameters
            ----------
            data_df : pd.DataFrame
                Dataframe with clean data
            
            missing_values_df: pd.DataFrame
                Dataframe with missing data

            missing_values_df_copy: pd.DataFrame
                Dataframe with duplicated and imputed data 

            y_pred: pd.Series
                Predicted results of missing_values_df_copy from self.model

            row_num_group_column : pd.Series
                Column indicating which duplicated row it originally belonged to 

             Returns
             -------
            final_predictions: pd.DataFrame
                missing_values_df with class averaged values.

        '''
        missing_df_copy[self.y_column_name] = y_pred
        missing_df_copy['row_num_group'] = row_num_group_column
        if self.problem_type == 'classification':
            final_class = missing_df_copy.groupby('row_num_group')[self.y_column_name].agg(lambda x: statistics.mode(x))
        elif self.problem_type == 'regression':
            final_class = missing_df_copy.groupby('row_num_group')["binned_feature"].agg(lambda x: statistics.median(x))
        else:
            raise ValueError("Invalid imputation type. Must be classification or regression.")

        
        if self.problem_type == "classification":
            missing_df[self.y_column_name] = final_class
            final_predictions = self.class_averages_imputer(data_df, missing_df)
            final_predictions[self.y_column_name] = final_class
        else:
            missing_df["binned_feature"] = final_class
            final_predictions, _ = self.regression_averages_imputer(data_df, missing_df)
        return final_predictions

    def imputer_pipeline(self, data_df, missing_values_df, y_column_name, number_of_bins = 20):
        ''' Handles preprocessing, model building, and imputation steps
        
            Parameters
            ----------
            data_df : pd.DataFrame
                Dataframe with clean data 
            
            missing_values_df: pd.DataFrame
                Dataframe with missing data
            
            y_column_name: str
                Target variable name

             Returns
             -------
            final_predictions: pd.DataFrame
                missing_values_df with class averaged values.

            [parameters, test_scores]:List[Dict, List]
                parameters used and thier associated test set scoring 
        '''
        self._check_training_pipeline_parameters(data_df, missing_values_df, y_column_name)

        self.data_df = data_df.copy()
        self.missing_values_df = missing_values_df[self.data_df.columns].copy()

        self.number_of_bins = number_of_bins
        self.y_column_name = y_column_name

        df_missing_copy, row_num_group_column = self.duplicate_rows(self.missing_values_df, self.data_df[self.y_column_name])

        if self.problem_type == "classification":
            regression_y = None
            missing_values_df_imputed= self.class_averages_imputer(self.data_df, df_missing_copy)
            y_data_df = self.data_df[self.y_column_name]
            X_data_df = self.data_df.drop(columns=[self.y_column_name])
        else:
            regression_y = self.data_df[self.y_column_name]
            missing_values_df_imputed, y_data_df  = self.regression_averages_imputer(self.data_df, df_missing_copy)
            missing_values_df_imputed = missing_values_df_imputed.dropna() #empty bins can exist
            X_data_df = self.data_df.drop(columns=["binned_feature", self.y_column_name])
        
        # Split x and y to train and predict
        try:
            X_predict = missing_values_df_imputed.drop(columns=[self.y_column_name])
        except:
            X_predict = missing_values_df_imputed
        
        # Need to encode 
        X_train_transformer, _ = utils.encode(X_data_df)
        X_data_df = X_train_transformer.fit_transform(X_data_df)
        X_predict = X_train_transformer.transform(X_predict)
        if self.problem_type == 'classification':

            if self.param_grid:
                grid_search = GridSearchCV(estimator=self.model, param_grid=self.param_grid, n_jobs =-1, scoring='accuracy', cv=3)
            else: # have to ask about which model to use here and how to execute this part as a whole
                param_grid_alt = {
                    'n_estimators': [100, 200, 300, 500],
                    'max_depth': [None, 10, 20],
                    'min_samples_split': [2, 5],
                    'min_samples_leaf': [1, 2, 4],
                    'max_features':["sqrt","log2"],
                    'class_weight': ['balanced']}
                grid_search = GridSearchCV(estimator=RandomForestClassifier(), param_grid= param_grid_alt, n_jobs =-1, scoring='accuracy', cv=3)

            grid_search.fit(X_data_df, y_data_df)
            best_model = grid_search.best_estimator_
            parameters = grid_search.cv_results_['params']
            test_scores = grid_search.cv_results_['mean_test_score']
            y_pred = best_model.predict(X_predict)

            # Make predictions on the test data
            final_predictions = self.impute_results(self.data_df, 
                                                    missing_values_df, 
                                                    missing_values_df_imputed, 
                                                    y_pred, 
                                                    row_num_group_column)

        elif self.problem_type == 'regression':
            grid_search = GridSearchCV(estimator=self.model, param_grid=self.param_grid, n_jobs =-1, scoring='neg_mean_squared_error', cv=3)
            grid_search.fit(X_data_df, regression_y)
            
            best_model = grid_search.best_estimator_
            parameters = grid_search.cv_results_['params']
            test_scores = grid_search.cv_results_['mean_test_score']
            y_pred = best_model.predict(X_predict)
            # Make predictions on the test data
            final_predictions = self.impute_results(self.data_df, 
                                                    missing_values_df, 
                                                    missing_values_df_imputed, 
                                                    y_pred, 
                                                    row_num_group_column)
            final_predictions = final_predictions.drop(columns=["binned_feature"])
            X_predict = X_train_transformer.transform(final_predictions)
            best_model = grid_search.best_estimator_
            y_pred = best_model.predict(X_predict)
            final_predictions[self.y_column_name] = y_pred
        
        return final_predictions, [parameters, test_scores]