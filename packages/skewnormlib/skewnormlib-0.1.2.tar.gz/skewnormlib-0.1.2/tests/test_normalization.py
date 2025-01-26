import unittest
from scipy.stats import skew
import numpy as np
from skewnorm.normalization import SkewWeightedNormalization

class TestSkewWeightedNormalization(unittest.TestCase):
    """
    Unit tests for SkewWeightedNormalization.
    """
    def setUp(self):
        """
        Set up sample data for testing.
        """
        self.data = np.array([[1, 2, 3],
                              [4, 5, 6],
                              [7, 8, 9],
                              [10, 20, 30]])

    def test_fit(self):
        """
        Test that the fit method correctly computes mean, standard deviation, and skewness.
        """
        transformer = SkewWeightedNormalization()
        transformer.fit(self.data)

        np.testing.assert_almost_equal(transformer.mu_, np.mean(self.data, axis=0))
        np.testing.assert_almost_equal(transformer.sigma_, np.std(self.data, axis=0))
        np.testing.assert_almost_equal(transformer.gamma_, skew(self.data, axis=0))

    def test_transform(self):
        """
        Test that the transform method correctly normalizes the data.
        """
        transformer = SkewWeightedNormalization()
        transformer.fit(self.data)
        transformed_data = transformer.transform(self.data)

        self.assertEqual(transformed_data.shape, self.data.shape)
        np.testing.assert_almost_equal(np.mean(transformed_data, axis=0), 0, decimal=1)

# Run the tests
if __name__ == "__main__":
    unittest.main()
