import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from rfproximity.treeimputer.treeimputertest import TreeImputerTest

def test_training_pipeline():
    X = pd.DataFrame(np.random.rand(100, 5))
    y = pd.Series(np.random.rand(100))
    model = RandomForestRegressor()
    tp = TreeImputerTest("regression", model)
    train_res = tp.training_pipeline(X, y)
    assert len(train_res) == 5 #same length as number of splits, one result per split

    for res in train_res:
        assert len(res) == 3
