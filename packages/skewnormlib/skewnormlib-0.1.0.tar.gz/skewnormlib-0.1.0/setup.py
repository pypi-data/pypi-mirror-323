from setuptools import setup, find_packages

setup(
    name="skewnorm",
    version="0.1.0",
    author="Mohammed Nihal",
    author_email="mohd.nihalll03@gmail.com",
    description="A library for skew-weighted normalization",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mohdnihal03/skewnormlib",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "scikit-learn"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
