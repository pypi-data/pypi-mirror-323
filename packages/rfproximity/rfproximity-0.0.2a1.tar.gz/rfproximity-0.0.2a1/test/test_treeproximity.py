import numpy as np
import sys
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from rfproximity.treeproximity import TreeProximity

def test_get_sampled_indices():
    tree = DecisionTreeClassifier()
    n_samples = 100
    max_samples = None
    tp = TreeProximity(None)
    indices = tp.get_sampled_indices(tree, n_samples, max_samples)
    assert isinstance(indices, np.ndarray)
    assert indices.shape == (n_samples,)

def test_get_unsampled_indices():
    tree = DecisionTreeRegressor()
    n_samples = 200
    max_samples = 150
    tp = TreeProximity(None)
    indices = tp.get_unsampled_indices(tree, n_samples, max_samples)
    assert isinstance(indices, np.ndarray)
    assert indices.shape != (n_samples,)

def test_proximity_matrix():
    X = np.random.rand(100, 5)
    treeimportance = [1]
    leaf_nodes = np.random.randint(1,100,100).reshape(100,1)
    tp = TreeProximity(leaf_nodes=leaf_nodes)
    proximity_matrix = tp.proximity_matrix(treeimportance)
    assert isinstance(proximity_matrix, np.ndarray)
    assert proximity_matrix.shape == (100, 100)

def test_proximity_matrix_oob() -> None:
    X = np.random.rand(100, 5)
    y = np.random.rand(100, 1)
    n_samples = 100
    model = RandomForestRegressor()
    leaf_nodes = np.random.randint(1,100,100).reshape(100,1)
    
    model.fit(X, y)
    tp = TreeProximity(leaf_nodes=leaf_nodes)
    proximity_matrix = tp.proximity_matrix_oob(model, n_samples)
    
    assert isinstance(proximity_matrix, np.ndarray)
    assert proximity_matrix.shape == (100, 100)

def test_proximity_matrix_gap() -> None:
    X = np.random.rand(100, 5)
    y = np.random.rand(100, 1).ravel()
    n_samples = 100
    model = RandomForestRegressor()
    leaf_nodes = np.random.randint(1,100,(100, 100))
    model.fit(X, y)

    tp = TreeProximity(leaf_nodes=leaf_nodes)
    proximity_matrix = tp.proximity_matrix_gap(model, n_samples)
    assert isinstance(proximity_matrix, np.ndarray)
    assert proximity_matrix.shape == (100, 100)