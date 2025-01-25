import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import pytest

from rfproximity.treeimputer import TreeImputer, ImputerUtils

@pytest.fixture
def tree_imputer():
    model = RandomForestRegressor()
    return TreeImputer(model)

def test_tree_imputer_init(tree_imputer):
    assert isinstance(tree_imputer.model, RandomForestRegressor)
    assert isinstance(tree_imputer.params, dict)
    assert isinstance(tree_imputer.utils, ImputerUtils)

def test_tree_imputer_check_model(tree_imputer):
    with pytest.raises(TypeError):
        tree_imputer.model = "RandomForestRegressor"
        tree_imputer._check_model()

def test_tree_imputer_check_impute_pipeline_parameters(tree_imputer):
    X = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    y = pd.Series([7, 8, 9])
    proxy_method = 'means'
    categorical_ordinal_features = ['A']
    with pytest.raises(ValueError):
        tree_imputer._check_impute_pipeline_parameters(X, y,
                                                        proxy_method,
                                                        categorical_ordinal_features)

# def test_tree_imputer_training_iteration(tree_imputer):
#     tree_imputer.X_copy = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
#     tree_imputer.y_copy = pd.Series([7, 8, 9])
#     proxy_method = 'original'
#     result = tree_imputer.training_iteration(proxy_method)
#     assert isinstance(result, np.ndarray)

def test_tree_imputer_class_average_imputer(tree_imputer):
    dataframe = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    y = pd.Series([7, 8, 9])
    missing_mask = np.array([False, True, False])
    tree_imputer.imputer_pipeline(dataframe,y)
    result = tree_imputer.class_average_imputer(dataframe, missing_mask)
    assert isinstance(result, pd.DataFrame)

# def test_tree_imputer_training_pipeline(tree_imputer):
#     proxy_method = 'original'
#     training_iterations = 5
#     result = tree_imputer.training_pipeline(proxy_method, training_iterations)
#     assert isinstance(result, pd.DataFrame)

def test_tree_imputer_imputer_pipeline(tree_imputer):
    X = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    y = pd.Series([7, 8, 9])
    proxy_method = 'original'
    cardinality_threshold = 10
    training_iterations = 5
    result = tree_imputer.imputer_pipeline(X=X,y=y,proxy_method=proxy_method,
                                           cardinality_threshold=cardinality_threshold,
                                           training_iterations=training_iterations)
    assert isinstance(result, pd.DataFrame)