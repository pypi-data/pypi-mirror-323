import numpy as np
import pytest
from skewnorm.normalization import SkewWeightedNormalization

def test_fit():
    """Test the fit method."""
    data = np.random.rand(100, 5)
    swn = SkewWeightedNormalization()
    swn.fit(data)
    assert hasattr(swn, "mu_")
    assert hasattr(swn, "sigma_")
    assert hasattr(swn, "gamma_")
    assert swn.mu_.shape == (5,)
    assert swn.sigma_.shape == (5,)
    assert swn.gamma_.shape == (5,)

def test_transform():
    """Test the transform method."""
    data = np.random.rand(100, 5)
    swn = SkewWeightedNormalization()
    swn.fit(data)
    transformed = swn.transform(data)
    assert transformed.shape == data.shape

def test_fit_transform():
    """Test the fit_transform method."""
    data = np.random.rand(100, 5)
    swn = SkewWeightedNormalization()
    transformed = swn.fit_transform(data)
    assert hasattr(swn, "mu_")
    assert hasattr(swn, "sigma_")
    assert hasattr(swn, "gamma_")
    assert transformed.shape == data.shape

def test_shape_mismatch():
    """Test for shape mismatch between fit and transform."""
    train_data = np.random.rand(100, 5)
    test_data = np.random.rand(100, 6)  # Different number of features
    swn = SkewWeightedNormalization()
    swn.fit(train_data)
    with pytest.raises(ValueError):
        swn.transform(test_data)
