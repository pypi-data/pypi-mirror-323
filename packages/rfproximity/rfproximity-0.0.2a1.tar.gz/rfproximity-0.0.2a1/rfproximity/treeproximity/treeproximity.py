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

from sklearn import ensemble
import numpy as np
import warnings
import sklearn.ensemble._forest as forest_utils
warnings.filterwarnings("ignore", category=RuntimeWarning) 
np.seterr(invalid='ignore')


class TreeProximity:
    """
    Module to calculate proximity for tree-based models trained with sklearn python packages.
    Proximity calculations implemented are vanilla proximity proposed by Brieman,
    Out-of-bag proximity, and Geometry and Accuracy Preserving (GAP) proximity.

    In case of out-of-bag (OOB) and GAP proximity, 
    the input array should be in the shape of concatenated X_train and X_test, and the shape of X_train
    indices should be defined accordingly. Current implementation is only supported for sklearn models.

    Parameters
    ----------
    leaf_nodes : np.ndarray
        The leaf nodes of the model.
    """

    def __init__(self, leaf_nodes: np.ndarray):
        """
        Initialize with leaf codes from any tree-based model from sklearn/xgboost/lightgbm/catboost

        Parameters
        ----------
        leaf_nodes : list
            The leaf nodes of the model.
        """
        self.leaf_nodes = leaf_nodes

    def _set_model(self, model):
        """
        Class method to test if the model file is a supported sklearn ensemble model.
        """
        if isinstance(model, (ensemble._forest.RandomForestClassifier,
                              ensemble._forest.RandomForestRegressor)):
            self.modelclass = 'sklearn'
            return model
        else:
            self.modelclass = None
            raise TypeError("Input type must be a valid RandomForest model supported in sklearn")
        
    def get_sampled_indices(self, tree, n_samples, max_samples: None):
        """
        Return indices for sampled data points in the dataset used for training
        the corresponding tree model.

        Parameters
        ----------
        tree : sklearn.tree._classes.DecisionTreeClassifier or sklearn.tree._classes.DecisionTreeRegressor
            The decision tree classifier.
        n_samples : int
            The number of samples used to train the original model or tree.
        max_samples : int, float, or None
            The number of samples used to train the random forest model. Can be derived from model parameters for a pretrained model.

        Returns
        -------
        ndarray of shape (n_samples,)
            Array of indices used from the training set to train the given tree, usually repeated set of indices.
        """
        # n_samples here - training set of examples
        n_samples_bootstrap = forest_utils._get_n_samples_bootstrap(
            n_samples, max_samples
        )
        sample_indices = forest_utils._generate_sample_indices(
            tree.random_state, n_samples, n_samples_bootstrap
        )
        return sample_indices

    def get_unsampled_indices(self, tree, n_samples, max_samples=None):
        """
        Return indices for unsampled data from the set of all data points which aren't used to train that particular tree.

        Parameters
        ----------
        tree : sklearn.tree._classes.DecisionTreeClassifier or sklearn.tree._classes.DecisionTreeRegressor
            The decision tree classifier.
        n_samples : int
            The number of samples used to train the original model or tree.
        max_samples : int, float, or None
            The number of samples used to train the random forest model. Can be derived from model parameters for a pretrained model.

        Returns
        -------
        ndarray of shape (n_samples,)
            Array of unsampled indices from the training set not used to train the given tree.
        """

        # X here - training set of examples
        n_samples_bootstrap = forest_utils._get_n_samples_bootstrap(
            n_samples, max_samples
        )
        return forest_utils._generate_unsampled_indices(
            tree.random_state, n_samples, n_samples_bootstrap
        )

    def proximity_matrix(self, treeimportance: list = None):
        """
        Return the proximity matrix for input data X inferred on the model.

        Parameters
        ----------
        treeimportance : list of float, optional
            Weight given to each tree while calculating proximity. If None, each tree has uniform weight. Default is None.

        Returns
        -------
        ndarray of shape (n_samples, n_samples)
            The proximity matrix of X.
        """
        terminals = self.leaf_nodes.T
        NoneType = type(None)
        if isinstance(treeimportance, NoneType):
            treeimportance = [1/terminals.shape[0] for i in range(terminals.shape[0])]
        assert(terminals.shape[0] == len(treeimportance))

        proximity_matrix = np.zeros((terminals.shape[1], terminals.shape[1]))

        for tree in range(terminals.shape[0]):
            proximity_matrix += np.equal(terminals[tree][:,None],
                                        terminals[tree]) * treeimportance[tree]

        return proximity_matrix

    def proximity_matrix_oob(self,model, X_train_shape, normalize=True):
        """
        Return the out-of-bag (OOB) proximity matrix. Only supported for sklearn models.

        Parameters
        ----------
        model : object
            The trained model object.
        X_train_shape : int
            The number of samples used in the training.
        normalize : bool, optional
            Boolean value indicating whether to normalize the matrix. If True, it will be normalized. Default is True.

        Returns
        -------
        ndarray of shape (n_samples, n_samples)
            The OOB proximity matrix of X.
        """
        terminals = self.leaf_nodes.T
        self.model = self._set_model(model)
        max_samples = self.model.get_params()["max_samples"]

        sum_ntree = np.zeros((terminals.shape[1], terminals.shape[1]))
        proximity_matrix = np.zeros((terminals.shape[1], terminals.shape[1]))

        for tree in range(terminals.shape[0]):

            # get all oob indices for that tree
            oob_mat = np.zeros(X_train_shape)
            unsampled_indices = self.get_unsampled_indices(
                self.model.estimators_[tree], X_train_shape, max_samples
            )
            # replace unsampled data points with ones in the oob matrix
            np.put(oob_mat, unsampled_indices,
                    np.ones(unsampled_indices.shape))

            # check if more data was passed in addition to the training dataset
            # if so, append an array of ones corresponding to the difference in
            # the size of training and input array

            if self.leaf_nodes.shape[0] > X_train_shape:
                oob_mat = np.concatenate(
                    (oob_mat, np.ones(self.leaf_nodes.shape[0] - X_train_shape)))

            # take the outer product of oob_mat to make all
            # x_i,j pairs where either i or j is in-bag as zero
            # or in other terms, all x_i,j pairs are 1 where
            # both i and j are oob samples

            oob_mat = np.outer(oob_mat, oob_mat)

            # nullify terminal nodes for those indices
            proximity_matrix += (
                1 * np.equal(terminals[tree][:,None], terminals[tree]) * oob_mat
                )

            # keep summing oob matrix to calculate the numerator
            # i.e count for which the data point for in a given tree should be
            # considered or not
            sum_ntree += oob_mat
        if normalize:
            return np.divide(
                proximity_matrix,
                sum_ntree,
                out=np.zeros_like(proximity_matrix),
                where=sum_ntree != 0,
            )

        return proximity_matrix


    def proximity_matrix_gap(self,model, X_train_shape):
        """
        Return Geometry and Accuracy preserving (GAP) proximity matrix,
        only supported for sklearn models.

        Parameters
        ----------
        model : object
            The trained sklearn model object.
        X_train_shape : int
            The number of samples used in the training.

        Returns
        -------
        ndarray of shape (n_samples, n_samples)
            The GAP proximity matrix.

        Raises
        ------
        ValueError
            If the model is not supported.

        Notes
        -----
        This method calculates the GAP proximity matrix for a given sklearn model.
        The GAP proximity matrix measures the similarity between data points based on
        their proximity in the decision tree ensemble. It is a measure of how often
        two data points end up in the same leaf node across different trees in the ensemble.

        The method assumes that the model has been trained using the sklearn framework.
        """
        s_i = np.zeros(self.leaf_nodes.shape[0])
        p_gap = np.zeros((self.leaf_nodes.shape[0], self.leaf_nodes.shape[0]))
        terminals = self.leaf_nodes.T
        self.model = self._set_model(model)
        max_samples = self.model.get_params()["max_samples"]

        for tree in range(len(self.model.estimators_)):

            in_bag_samples = np.zeros(X_train_shape)
            in_bag_indices = self.get_sampled_indices(
                self.model.estimators_[tree], X_train_shape, max_samples
            )
            np.put(in_bag_samples, in_bag_indices, 1)
            in_bag_samples = np.concatenate(
                (in_bag_samples, np.zeros(self.leaf_nodes.shape[0] - X_train_shape))
            )

            in_bag_multiplicity = np.zeros(X_train_shape)
            np.add.at(in_bag_multiplicity, in_bag_indices, np.ones(X_train_shape))
            
            in_bag_multiplicity = np.concatenate(
                (in_bag_multiplicity, np.zeros(self.leaf_nodes.shape[0] - X_train_shape))
            )
            
            oob_samples = 1 - in_bag_samples

            # get pair of data points where i is OOB and j is in-bag for i_th tree
            oob_in_bag = np.equal.outer(oob_samples, in_bag_samples) * 1

            # sum the total number of in_bag data points which are in same leaf node and are in_bag
            # check if i and j end up in same leaf node
            prox = np.equal(terminals[tree][:,None], terminals[tree]) * 1

            # i.e. outer product being 1
            # get sum of shared in bag observations for i and j
            # where i and j end up in same terminal node (prox)
            # in_bag_shared = np.outer(in_bag_samples, in_bag_samples)
            sum_leaf_node = np.sum((prox * in_bag_multiplicity), axis=1)
            # j_j_xt = prox * oob_in_bag
            
            # warnings.filterwarnings("ignore", category=RuntimeWarning)
            p_gap += (prox*in_bag_multiplicity)/sum_leaf_node
            # p_gap += np.nan_to_num((j_j_xt*in_bag_multiplicity / sum_leaf_node), posinf=0)
            s_i += oob_samples
        return p_gap / len(self.model.estimators_)