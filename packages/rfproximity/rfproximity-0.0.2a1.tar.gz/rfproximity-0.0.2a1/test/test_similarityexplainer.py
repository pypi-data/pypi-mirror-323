import unittest

import numpy as np

from rfproximity.similarityexplainer import SimilarityExplainer

class TestSimilarityExplainer(unittest.TestCase):
    def setUp(self):
        self.proximity_matrix = np.array([[1, 0.8, 0.1], [0.8, 1, 0.2], [0.1, 0.2, 1]])
        self.y = np.array([0, 0, 1])
        self.explainer = SimilarityExplainer(self.proximity_matrix, self.y)

    def test_raw_outlier_measure(self):
        result = self.explainer.raw_outlier_measure()
        expected = np.array([1.5384, 1.4705, 0])
        np.testing.assert_array_equal(np.round(result,2), np.round(expected,2))

    def test_get_top_sample(self):
        top_sample, neighbors = self.explainer.get_top_sample(self.proximity_matrix, self.y, 2)
        self.assertEqual(top_sample, 0)
        np.testing.assert_array_equal(neighbors, np.array([0, 1]))

    def test_get_prototype(self):
        prototypes = self.explainer.get_prototype(2, 1, True)
        self.assertIsInstance(prototypes, dict)
        self.assertEqual(len(prototypes), 1)

    def test_get_classwise_outlier_measure(self):
        classwise_outlier = self.explainer.get_classwise_outlier_measure()
        self.assertIsInstance(classwise_outlier, list)
        self.assertEqual(len(classwise_outlier), len(self.y))

if __name__ == '__main__':
    unittest.main()