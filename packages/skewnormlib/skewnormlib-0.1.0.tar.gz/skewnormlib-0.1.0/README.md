# skewnormlib

`skewnorm` is an open-source Python library designed for preprocessing data using a novel method called **Skew Weighted Normalization**. This technique accounts for the skewness in data and applies normalization while optionally introducing a non-linear transformation. It is ideal for preparing data for machine learning models that require normalized inputs.

---

## What is SkewWeightedNormalization?

The `SkewWeightedNormalization` class is a custom data transformer that normalizes data while considering its skewness. It achieves this by combining a skew-adjusted normalization term and a non-linear transformation term, making it more robust for skewed datasets.

### Mathematical Formula:
The transformation is defined as:

\[
\text{scaled\_data} = \frac{X - \mu}{\sigma (1 + \alpha \cdot |\gamma|)} + \beta \cdot \tanh\left(\frac{X - \mu}{k \cdot \sigma}\right)
\]

Where:
- \(X\): Input data.
- \(\mu\): Mean of the data.
- \(\sigma\): Standard deviation of the data.
- \(\gamma\): Skewness of the data.
- \(\alpha\): Skewness weighting factor (default: 1.0).
- \(\beta\): Weighting factor for the non-linear transformation (default: 0.5).
- \(k\): Scaling factor for the non-linear term (default: 1.0).

---

## How to Use

### Installation
Install the library from PyPI:
```bash
pip install skewnorm
```

### Usage Example
```python
import numpy as np
from skewnorm.normalization import SkewWeightedNormalization

# Sample data
data = np.array([[1, 2, 3],
                 [4, 5, 6],
                 [7, 8, 9],
                 [10, 20, 30]])

# Initialize the transformer
swn = SkewWeightedNormalization(alpha=1.0, beta=0.5, k=1.0)

# Fit the transformer to the data
swn.fit(data)

# Transform the data
transformed_data = swn.transform(data)
print("Transformed Data:")
print(transformed_data)
```

---

## Advantages
- **Handles Skewness**: Unlike traditional normalization techniques, this method adjusts for skewness, making it suitable for heavily skewed datasets.
- **Non-linear Transformation**: The additional \(\tanh\) term helps reduce the influence of extreme outliers.
- **Scikit-learn Compatible**: The class adheres to Scikit-learn's API, allowing seamless integration into pipelines.
- **Open Source**: The library is open for contributions, making it a community-driven project.

---

## Disadvantages
- **Complexity**: The additional parameters (\(\alpha, \beta, k\)) require tuning for optimal results.
- **Performance**: Slightly slower than standard normalization techniques due to the computation of skewness and the non-linear term.

---

## When to Use It
- **Skewed Data**: Use this method when the dataset has significant skewness, as it normalizes while accounting for the skew.
- **Outlier Sensitivity**: When datasets contain extreme outliers that might adversely affect models, this normalization technique can help mitigate their influence.
- **Preprocessing for ML**: Use this as a preprocessing step for machine learning models that perform better on normalized data (e.g., SVM, Neural Networks).

---

## Contributing
This library is open source, and contributions are welcome! Feel free to:
1. Submit bug reports.
2. Suggest new features.
3. Improve documentation.
4. Optimize performance.

Visit the GitHub repository to contribute:
[GitHub Repository](https://github.com/mohdnihal03/skewnorm)

---

## License
This project is licensed under the MIT License, ensuring it remains free and open for everyone.

---

## Contact
For questions or suggestions, contact:
- **Author**: Your Name
- **Email**: your.email@example.com
