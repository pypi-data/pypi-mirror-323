from setuptools import setup, find_packages

setup(
    name="querysquirrel",  # Replace with your library name
    version="0.1.0",  # Replace with your library version
    author="Will Armstrong, Thomas Burns. Caroline Cordes, Sarah Lawlis",
    author_email="wma002@uark.edu",
    description="A library for building and testing NLP models with PyTorch and Transformers",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sarahlawlis/esci-shopping-queries",  
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "torch>=1.9.0",
        "transformers>=4.12.0",
        "sentence-transformers>=2.2.2",
        "scikit-learn>=0.24.0",
        "pandas>=1.3.0",
        "numpy>=1.19.0",
        "matplotlib>=3.4.3",
        "seaborn>=0.11.2",
        "dask[dataframe]>=2021.10.0",
        "pyarrow>=5.0.0",
    ],
)
