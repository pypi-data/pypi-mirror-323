import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from rfproximity.treeimputer.treeimputermissingtarget import TreeImputerMissingTarget

def test_class_averages_imputer():
    data_df = pd.DataFrame({'feature1': [1, 2, 3, 4, 5],
                            'feature2': [6, 7, 8, 9, 10],
                            'target': ['A', 'B', 'A', 'B', 'A']})

    missing_values_df = pd.DataFrame({'feature1': [1, np.nan, 3, np.nan, 5],
                                        'feature2': [6, np.nan, 8, np.nan, 10],
                                        'target': ['A', 'B', 'A', 'B', 'A']})

    imputer = TreeImputerMissingTarget('classification', RandomForestClassifier(),'target')
    imputer.imputer_pipeline(data_df,missing_values_df,'target')
    imputed_df = imputer.class_averages_imputer(data_df, missing_values_df)

    expected_df = pd.DataFrame({'feature1': [1, 2, 3, 4, 5],
                                'feature2': [6, 7, 8, 9, 10],
                                'target': ['A', 'B', 'A', 'B', 'A']})

    assert isinstance(expected_df,pd.DataFrame)

def test_regression_averages_imputer():
    data_df = pd.DataFrame({'feature1': [1, 2, 3, 4, 5],
                            'feature2': [6, 7, 8, 9, 10],
                            'target': [10, 20, 30, 40, 50]})

    missing_values_df = pd.DataFrame({'feature1': [1, np.nan, 3, np.nan, 5],
                                      'feature2': [6, np.nan, 8, np.nan, 10],
                                      'target': [10, np.nan, 30, np.nan, 50]})

    imputer = TreeImputerMissingTarget('regression', RandomForestRegressor(),'target')
    imputer.imputer_pipeline(data_df,missing_values_df,'target')
    imputed_df, _ = imputer.regression_averages_imputer(data_df, missing_values_df)

    expected_df = pd.DataFrame({'feature1': [1, 2, 3, 4, 5],
                                'feature2': [6, 7, 8, 9, 10],
                                'target': [10, 20, 30, 40, 50]})

    assert isinstance(expected_df,pd.DataFrame)

def test_duplicate_rows():
    data_df = pd.DataFrame({'feature1': [1, 2, 3, 4, 5],
                            'feature2': [6, 7, 8, 9, 10],
                            'target': ['A', 'B', 'A', 'B', 'A']})

    missing_values_df = pd.DataFrame({'feature1': [1, np.nan, 3, np.nan, 5],
                                        'feature2': [6, np.nan, 8, np.nan, 10],
                                        'target': ['A', 'B', 'A', 'B', 'A']})

    full_y_column = pd.Series(['A', 'B', 'A', 'B', 'A'])

    imputer = TreeImputerMissingTarget('classification', RandomForestClassifier(),'target')
    imputer.imputer_pipeline(data_df,missing_values_df,'target')
    duplicated_df, row_num_group_column = imputer.duplicate_rows(missing_values_df, full_y_column)

    expected_duplicated_df = pd.DataFrame({'feature1': [1, 2, 3, 1, 2, 3, 1, 2, 3],
                                            'feature2': [4, 5, 6, 4, 5, 6, 4, 5, 6],
                                            'target': ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C']})

    expected_row_num_group_column = pd.Series([0, 0, 0, 1, 1, 1, 2, 2, 2])

    assert isinstance(expected_duplicated_df,pd.DataFrame)
    assert isinstance(row_num_group_column,pd.Series)

def test_impute_results_classification():
    data_df = pd.DataFrame({'feature1': [1, 2, 3, 4, 5],
                            'feature2': [6, 7, 8, 9, 10],
                            'target': ['A', 'B', 'A', 'B', 'A']})

    missing_values_df = pd.DataFrame({'feature1': [1, 2, 3, 4, 5],
                                        'feature2': [np.nan, 7, 8, 9, np.nan],
                                        'target': ['A', 'B', 'A', 'B', 'A']})

    missing_values_df_imputed = pd.DataFrame({'feature1': [1, 2, 3, 4, 5],
                                                'feature2': [6, 7, 8, 9, 10],
                                                'target': ['A', 'B', 'A', 'B', 'A']})

    y_pred = pd.Series(['A', 'B', 'A', 'B', 'A'])

    row_num_group_column = pd.Series([0, 1, 0, 1, 0])

    imputer = TreeImputerMissingTarget('classification', RandomForestClassifier(),'target')
    missing_values_df_imputed,_ = imputer.imputer_pipeline(data_df,missing_values_df,'target')
    final_predictions = imputer.impute_results(data_df, missing_values_df, missing_values_df_imputed, y_pred, row_num_group_column)

    expected_predictions = pd.DataFrame({'feature1': [1, 2, 3, 4, 5],
                                            'feature2': [6, 7, 8, 9, 10],
                                            'target': ['A', 'B', 'A', 'B', 'A']})
    assert isinstance(final_predictions,pd.DataFrame)

def test_impute_results_regression():
    data_df = pd.DataFrame({'feature1': [1, 2, 3, 4, 5],
                            'feature2': [6, 7, 8, 9, 10],
                            'target': [10, 20, 30, 40, 50]})

    missing_values_df = pd.DataFrame({'feature1': [1, np.nan, 3, np.nan, 5],
                                        'feature2': [6, np.nan, 8, np.nan, 10],
                                        'target': [10, np.nan, 30, np.nan, 50]})

    missing_values_df_imputed = pd.DataFrame({'feature1':
                                              [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,
                                               1.0,1.0,1.0,2.0,3.0,4.0,3.0,3.0,3.0,3.0,3.0,3.0,3.0,3.0,3.0,3.0,3.0,
                                               3.0,3.0,3.0,3.0,3.0,3.0,3.0,3.0,1.0,2.0,3.0,4.0,5.0,5.0,5.0,5.0,5.0,
                                               5.0,5.0,5.0,5.0,5.0,5.0,5.0,5.0,5.0,5.0,5.0,5.0,5.0,5.0],
                                            'feature2':[6.0,6.0,6.0,6.0,6.0,6.0,6.0,6.0,6.0,6.0,6.0,6.0,6.0,6.0,6.0,
                                                        6.0,6.0,6.0,6.0,6.0,7.0,8.0,9.0,8.0,8.0,8.0,8.0,8.0,8.0,8.0,
                                                        8.0,8.0,8.0,8.0,8.0,8.0,8.0,8.0,8.0,8.0,8.0,8.0,6.0,7.0,8.0,
                                                        9.0,10.0,10.0,10.0,10.0,10.0,10.0,10.0,10.0,10.0,10.0,10.0,
                                                        10.0,10.0,10.0,10.0,10.0,10.0,10.0,10.0],
                                            'binned_feature':[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,1,6,11,
                                                              16,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,1,6,
                                                              11,16,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
                                            'target':[13.6,13.6,13.6,13.6,13.6,13.6,13.6,13.6,13.6,13.6,13.6,13.6,13.6,
                                                      13.6,13.6,13.6,13.6,13.6,13.6,13.6,18.1,28.2,37.0,28.2,28.2,28.2,
                                                      28.2,28.2,28.2,28.2,28.2,28.2,28.2,28.2,28.2,28.2,28.2,28.2,28.2,
                                                      28.2,28.2,28.2,13.6,18.1,28.2,37.0,45.5,45.5,45.5,45.5,45.5,45.5,
                                                      45.5,45.5,45.5,45.5,45.5,45.5,45.5,45.5,45.5,45.5,45.5,45.5,45.5],
                                            'row_num_group':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,2,2,
                                                             2,2,2,2,2,2,2,2,2,2,2,2,2,3,3,3,3,4,4,4,4,4,4,4,4,4,4,4,4,
                                                             4,4,4,4,4,4,4]})

    y_pred = pd.Series([10, 20, 30, 40, 50])

    row_num_group_column = pd.Series([0, 0, 0, 1, 1])

    imputer = TreeImputerMissingTarget('regression', RandomForestRegressor(),'target')
    out = imputer.imputer_pipeline(data_df,missing_values_df,'target')
    final_predictions = imputer.impute_results(data_df, missing_values_df, missing_values_df_imputed, y_pred, row_num_group_column)

    assert isinstance(final_predictions,pd.DataFrame)

def test_imputer_pipeline_classification():
    data_df = pd.DataFrame({'feature1': [1, 2, 3, 4, 5],
                            'feature2': [6, 7, 8, 9, 10],
                            'target': ['A', 'B', 'A', 'B', 'A']})

    missing_values_df = pd.DataFrame({'feature1': [1, np.nan, 3, np.nan, 5],
                                      'feature2': [6, np.nan, 8, np.nan, 10],
                                      'target': ['A', 'B', 'A', 'B', 'A']})

    imputer = TreeImputerMissingTarget('classification', RandomForestClassifier(),'target')
    final_predictions, _ = imputer.imputer_pipeline(data_df, missing_values_df, 'target')

    expected_predictions = pd.DataFrame({'feature1': [1, 2, 3, 4, 5],
                                         'feature2': [6, 7, 8, 9, 10],
                                         'target': ['A', 'B', 'A', 'B', 'A']})

    assert isinstance(final_predictions,pd.DataFrame)

def test_imputer_pipeline_regression():
    data_df = pd.DataFrame({'feature1': [1, 2, 3, 4, 5],
                            'feature2': [6, 7, 8, 9, 10],
                            'target': [10, 20, 30, 40, 50]})

    missing_values_df = pd.DataFrame({'feature1': [1, np.nan, 3, np.nan, 5],
                                      'feature2': [6, np.nan, 8, np.nan, 10],
                                      'target': [10, np.nan, 30, np.nan, 50]})

    imputer = TreeImputerMissingTarget('regression', RandomForestRegressor(),'target')
    final_predictions, _ = imputer.imputer_pipeline(data_df, missing_values_df, 'target')

    expected_predictions = pd.DataFrame({'feature1': [1, 2, 3, 4, 5],
                                         'feature2': [6, 7, 8, 9, 10],
                                         'target': [10, 20, 30, 40, 50]})
    assert isinstance(final_predictions,pd.DataFrame)