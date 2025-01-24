import numpy as np
from scipy.stats import skew
from sklearn.base import BaseEstimator, TransformerMixin

class SkewWeightedNormalization(BaseEstimator, TransformerMixin):
    """
    SkewWeightedNormalization: A custom transformer for skew-weighted normalization.

    This transformer normalizes data while accounting for its skewness and optionally
    applies a non-linear transformation to reduce the influence of outliers.

    Parameters:
    ----------
    alpha : float, default=1.0
        Weighting factor for skewness adjustment.
    beta : float, default=0.5
        Weighting factor for the non-linear transformation.
    k : float, default=1.0
        Scaling factor for the non-linear transformation.
    """
    def __init__(self, alpha=1.0, beta=0.5, k=1.0):
        self.alpha = alpha
        self.beta = beta
        self.k = k

    def fit(self, X, y=None):
        """
        Fit the transformer by calculating mean, standard deviation, and skewness for each feature.

        Parameters:
        ----------
        X : array-like of shape (n_samples, n_features)
            Input data used to compute statistics.
        y : None (ignored)
            Included for compatibility with Scikit-learn.

        Attributes:
        ----------
        mu_ : array-like of shape (n_features,)
            Mean of each feature.
        sigma_ : array-like of shape (n_features,)
            Standard deviation of each feature.
        gamma_ : array-like of shape (n_features,)
            Skewness of each feature.

        Returns:
        -------
        self : object
            Returns the instance itself.
        """
        X = np.asarray(X)
        self.mu_ = np.mean(X, axis=0)
        self.sigma_ = np.std(X, axis=0)
        self.gamma_ = skew(X, axis=0)
        return self

    def transform(self, X):
        """
        Apply skew-weighted normalization to the data.

        Parameters:
        ----------
        X : array-like of shape (n_samples, n_features)
            Input data to be transformed.

        Returns:
        -------
        scaled_data : array-like of shape (n_samples, n_features)
            Transformed data.
        """
        X = np.asarray(X)
        scaled_data = (X - self.mu_) / (self.sigma_ * (1 + self.alpha * np.abs(self.gamma_))) \
                      + self.beta * np.tanh((X - self.mu_) / (self.k * self.sigma_))
        return scaled_data
