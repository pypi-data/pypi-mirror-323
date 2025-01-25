# **RFProximity**
<TODO>
## Introduction

RFProximity is a python package which computes proximity matrix for any Random Forest model. Package includes three specific implementations of proximity. Additionally, using the proximity matrix, package includes methods to perform missing value imputaion, outlier detection and prototype identification. 

## Table of Contents

- [Installation](#installation)
- [Background](#background)
- [Usage/Configurations](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)
- [Contact](#contact)

## Background

Reference Material:
- Leo Brieman and Adele Cutler's [blog](https://www.stat.berkeley.edu/~breiman/RandomForests/cc_papers.htm) on Random Forest
- Geometry and Accuracy Preserving (GAP) Proximities [Arxiv Link](https://arxiv.org/abs/2201.12682)


## Usage

```python
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from rfproximity import TreeProximity, SimilarityExplainer
import matplotlib.pyplot as plt
import pandas as pd

# Using Iris dataset 
# using the function `sklearn.datasets.load_iris` from
# scikit-learn. The dataset will contain:
# - 3 classes 
# - n samples

data = load_iris()
X,y = data['data'], data['target']
print(X.shape)


# Using the dataset we now train a random forest classifier first
model = RandomForestClassifier().fit(X,y)
leaf_nodes = model.apply(X)


# After training the model, initialize the TreeProximity module
prox = TreeProximity(leaf_nodes)

# Using TreeProximity module calculate proximity matrix
proximity_matrix = prox.proximity_matrix()
print(proximity_matrix)

# Using TreeProximity module calculate out-of-bag proximity matrix
proximity_matrix_oob = prox.proximity_matrix_oob(model,X.shape[0])
print(proximity_matrix_oob)


# Using TreeProximity module calculate geometry and accuracy preserving
# proximity matrix
proximity_matrix_gap = prox.proximity_matrix_gap(model,X.shape[0])
print(proximity_matrix_gap)


# Using TreeProximity module to identify prototype samples

SimEx = SimilarityExplainer(proximity_matrix, y)
prototypes = SimEx.get_prototype(top_k=20, total_prototypes=3, return_neighbors=True)
print(prototypes)


# Using TreeProximity module to identify class-wise outlier samples
raw_outlier_measure = SimEx.raw_outlier_measure()
outlier_measure = SimEx.get_classwise_outlier_measure()
df_outlier_measure = pd.DataFrame({'raw_outlier_measure':raw_outlier_measure,
                                    'outlier_measure':outlier_measure,
                                    'class_label':y}
                                  )
plt.figure()
plt.scatter(x=y,y=outlier_measure)
plt.xlabel('Class Label')
plt.ylabel('Outlier Measure')  
plt.title('Class-wise Outlier Measure')
plt.show()
```

## Contributing

Guidelines for contributing to the project:
  - [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)
  - [CONTRIBUTING.md](./CONTRIBUTING.md)

## License

The license for the project:
  - [LICENSE](./LICENSE)

## Credits

Initial code contributions:
- Dhruv Desai
- Dhagash Mehta
- Julio Urquidi
