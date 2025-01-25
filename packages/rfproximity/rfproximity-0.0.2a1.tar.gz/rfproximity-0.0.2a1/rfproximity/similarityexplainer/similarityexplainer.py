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
import numpy as np
from scipy.stats import median_abs_deviation
from copy import deepcopy

class SimilarityExplainer:
    """
    Class for explaining similarity in a dataset using proximity matrix.

    Parameters
    ----------
    proximity_matrix : array-like or sparse matrix
        Proximity matrix of shape (n_samples, n_samples).
    y : array-like
        The target values (class labels in classification, bins in case of regression) associated with samples in proximity matrix.

    Methods
    -------
    _raw_outlier_measure()
        Calculates the raw outlier measure for each sample in the proximity matrix.

    get_classwise_outlier_measure()
        Returns the outliers in the proximity matrix based on the outlier measure.

    get_top_sample(proximity_matrix, y, top_k)
        Returns the sample in the proximity matrix which is surrounded by the maximum number of samples from the same class weighted by proximity measure.

    get_prototype(top_k, total_prototypes, return_neighbors=False)
        Returns the prototypes extracted from the dataset based on the proximity matrix.

    """

    def __init__(self, proximity_matrix, y):
        self.proximity_matrix = np.array(proximity_matrix)
        self.y = np.array(y)

    def raw_outlier_measure(self):
        """
        Calculates the raw outlier measure for each sample in the proximity matrix. 
        Raw outlier measure is calculated as the ratio of the number of in-class samples to the sum of the squared proximity values.

        Returns
        -------
        ndarray
            Raw outlier measure for each sample in the proximity matrix of shape (n_samples,).

        """
        proximity_matrix = deepcopy(self.proximity_matrix)
        y = deepcopy(self.y)
        if proximity_matrix.shape[0] != len(y):
            raise ValueError("The shape of proximity matrix and target values must match.")
        #create matrix to keep track of in class samples per row
        class_samples = np.equal.outer(y,y)*1
        #multiply prox mat with in class sample to calculate outlier measure
        self.proximity_matrix = proximity_matrix*class_samples 
        np.fill_diagonal(proximity_matrix,0)
        np.fill_diagonal(class_samples,0)
        return np.sum(class_samples,axis=1) / np.sum(proximity_matrix**2,axis=1) 
    
    def get_classwise_outlier_measure(self):
        """
        Returns the outliers in the proximity matrix based on the outlier measure. 
        Classwise outlier measure is computed as the difference of raw outlier measure 
        and median of raw outlier measure for the same class divided by median absolute deviation.

        Returns:
        --------
            list: A list of outlier measures for each data point.

        """
        #compute raw outlier measure
        raw_outlier_score = self.raw_outlier_measure() 

        #calculate classwise outlier measure
        classwise_outlier = []
        for idx,raw_score in enumerate(raw_outlier_score):
            median_absolute_diveation = median_abs_deviation(raw_outlier_score[np.argwhere(self.y==self.y[idx])])[0] + np.random.uniform(1e-4,1e-6)
            measure = ((raw_score+np.random.uniform(1e-4,1e-6))-np.median(raw_outlier_score[np.argwhere(self.y==self.y[idx])])) / median_absolute_diveation
            classwise_outlier.append(measure)
        return classwise_outlier
    
    def get_top_sample(self,proximity_matrix,y,top_k:int):
        """
        Returns the sample in the proximity matrix which is surrounded by the maximum number of samples from the same class weighted by proximity measure.

        Parameters
        ----------
        proximity_matrix : array-like or sparse matrix
            Proximity matrix of shape (n_samples, n_samples).
        y : array-like
            The target values (class labels in classification, bins in case of regression) associated with samples in proximity matrix.
        top_k : int
            Number of neighbors to use when calculating top sample.

        Returns
        -------
        int
            Index of the top sample.
        ndarray
            Indexes of the top sample's neighbors of shape (1, top_k_samples).

        """
        if proximity_matrix.shape[0] <= top_k:
            raise ValueError("The number of samples in the proximity matrix must be greater than top_k.")

        #partition proximity matrix at top_k based on proximity score
        partition = np.argpartition(-proximity_matrix,top_k)[:,:top_k]
        #subset proximity matrix to chosen partition    
        proximity_subset = proximity_matrix[np.arange(proximity_matrix.shape[0])[:,None],
                                            partition]
        #check total sum of proximity for sample and neighbors from same class
        check_neigh_label = np.sum((y[partition]==y.reshape(-1,1))*1*proximity_subset,
                                    axis=1)
        top_sample = np.argmax(check_neigh_label)
        return top_sample, partition[top_sample,:] 
        
    def get_prototype(self, 
                      top_k:int, 
                      total_prototypes:int,
                      return_neighbors:bool=False)->dict:
        """
        Returns the prototypes extracted from the dataset based on the proximity matrix.

        Parameters
        ----------
        top_k : int
            Number of neighbors to use when calculating top sample.
        total_prototypes : int
            Number of prototypes to be extracted from the dataset.
        return_neighbors : bool, optional
            Return indexes of neighbors for corresponding prototype. Default is False.

        Returns
        -------
        dict
            Prototype sample index for each class.

        """
        #create an index tracker for samples
        samples_idx = np.arange(self.y.shape[0])

        #initialize prototype tracker
        prototype_tracker = {}
        #initialize prototype count
        protoype_count = 0
        #create a copy of proximity matrix
        proximity_matrix_copy = deepcopy(self.proximity_matrix)
        #create a copy of target variable
        y = deepcopy(self.y)

        #loop through proximity matrix to extract prototypes while elemenating neighbors after each iteration
        while (proximity_matrix_copy.shape[0] >= top_k) & (protoype_count < total_prototypes):
                # get top sample and its neighbors
                sample,top_k_neighbors = self.get_top_sample(proximity_matrix_copy,y,top_k)
                protoype_count+=1
                #add prototype to prototype tracker
                if y[sample] in prototype_tracker.keys():
                    if return_neighbors:
                        prototype_tracker[y[sample]][samples_idx[sample]] = samples_idx[top_k_neighbors]
                    else:
                        prototype_tracker[y[sample]].append(samples_idx[sample])
                else:
                    if return_neighbors:
                        prototype_tracker[y[sample]] = {}
                        prototype_tracker[y[sample]][samples_idx[sample]] = samples_idx[top_k_neighbors]
                    else:
                        prototype_tracker[y[sample]] = [samples_idx[sample]]
                #eliminate neighbors from y matrix and proximity matrix
                y = np.delete(y, top_k_neighbors)
                samples_idx = np.delete(samples_idx, top_k_neighbors)
                proximity_matrix_copy = np.delete(proximity_matrix_copy, top_k_neighbors, axis=0)
                proximity_matrix_copy = np.delete(proximity_matrix_copy, top_k_neighbors, axis=1)
            
        return prototype_tracker