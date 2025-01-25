import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from category_encoders import OneHotEncoder

from rfproximity.treeimputer.imputerutils import ImputerUtils

def test_set_fraction_missing():
    X = pd.DataFrame({'A': [1, 2, 3, 4, 5], 'B': [6, 7, 8, 9, 10]})
    imputer = ImputerUtils()
    X_miss, X_miss_idx = imputer.set_fraction_missing(X, fraction=0.2, random_state=42)
    assert isinstance(X_miss, pd.DataFrame)
    assert isinstance(X_miss_idx, pd.DataFrame)
    assert X_miss.shape == X.shape
    assert X_miss_idx.shape == X.shape

def test_get_num_cat_vars():
    df = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
    imputer = ImputerUtils()
    num_vars, cat_vars = imputer.get_num_cat_vars(df)
    assert isinstance(num_vars, list)
    assert isinstance(cat_vars, list)
    assert len(num_vars) == 1
    assert len(cat_vars) == 1

def test_mixerror():
    X_imp = np.array([[1, 2], [3, 4]])
    X = np.array([[1, 2], [3, 4]])
    X_miss_idx = np.array([[False, False], [False, False]])
    cat_vars = np.array([False, False])
    imputer = ImputerUtils()
    error = imputer.mixerror(X_imp, X, X_miss_idx, cat_vars)
    assert isinstance(error, float)

def test_update():
    df_column = np.array([1, np.nan, 3])
    proximity_matrix = np.array([[1.0, 0.5, 0.5], [0.3, 1.0, 0.7], [0.2, 1.0, 0.8]])
    mask_column = np.array([False, True, False])
    is_categorical = False
    imputer = ImputerUtils()
    column = imputer.update(df_column, proximity_matrix, mask_column, is_categorical)
    assert isinstance(column, np.ndarray)

def test_encode():
    original_dataframe = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
    categorical_ordinal_features = ['B']
    cardinality_threshold = 10
    imputer = ImputerUtils()
    preprocessor, numerical_features = imputer.encode(original_dataframe, categorical_ordinal_features, cardinality_threshold)
    assert isinstance(preprocessor, ColumnTransformer)
    assert isinstance(numerical_features, list)

def test_reverse_encoding():
    original_dataframe = pd.DataFrame({"Col1":['A','B','A'],
                                       "Col2":[1,2,3],
                                       "Col3":[1,2,3]})
    pipeline = ColumnTransformer(transformers=[('numerical_features', 'passthrough', ['Col2','Col3']),
                                    ('categorical_low_cardinality_features',
                                         Pipeline([('onehot', OneHotEncoder(handle_missing='return_nan'))]),
                                    ['Col1'])])
    encoded_dataframe = pipeline.fit_transform(original_dataframe)
    numerical_columns = ["Col2","Col3"]
    pre_encoding_X_columns = ["Col1"]
    imputer = ImputerUtils()
    decoded_transformed_data = imputer.reverse_encoding(encoded_dataframe, pipeline, numerical_columns, pre_encoding_X_columns)
    assert isinstance(decoded_transformed_data, pd.DataFrame)

def test_simple_imputer():
    proxy_method = 'median'
    num_indecies = ['A']
    cat_indecies = ['B']
    imputer = ImputerUtils()
    simple_imputers = imputer.simple_imputer(proxy_method, num_indecies, cat_indecies)
    assert isinstance(simple_imputers, ColumnTransformer)