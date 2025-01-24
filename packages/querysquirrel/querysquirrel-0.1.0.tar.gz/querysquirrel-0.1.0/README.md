# SearchGenius
SearchGenius is a Python library designed for building and testing NLP models using PyTorch and Transformers.

# Features
Implements deep learning models like FullyConnected and MLPsoftmax.

Provides utilities for embedding generation, dataset handling, and model evaluation.

Compatible with modern NLP frameworks like HuggingFace's Transformers.

# Installation
To install SearchGenius on your local machine, follow these steps:

1. Install from PyPI

Run the following command to install SearchGenius via pip: pip install searchgenius

# Usage
Once installed, you can import SearchGenius in your Python projects like this:

from searchgenius import myfunctions

# Development and Testing
Development and Testing

To set up the library locally for development:

1. Clone the Repository

git clone https://github.com/yourusername/searchgenius.git
cd searchgenius

2. Set Up a Virtual Environment

python -m venv venv
source venv/bin/activate  # For macOS/Linux
venv\Scripts\activate     # For Windows

3. Install Dependencies

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

4. Build and Test Locally

Build the Package

python setup.py sdist bdist_wheel

Test the Package

Run the following test file:

python tests/test_myfunctions.py pytest

Expected Output:

Testing FullyConnected...
FullyConnected passed.
Testing MLPsoftmax...
MLPsoftmax passed.
Testing ESCIDataset...
ESCIDataset passed.
Testing training loop...
Training loop passed.
Testing evaluation loop...
Accuracy: 0.4
Evaluation loop passed.

# Uploading to PyPI

1. Ensure Your .pypirc File is Set Up

Create or update your ~/.pypirc file with the following content:

[pypi]
username = __token__
password = pypi-<your-api-token>

2. Use Twine to Upload

Run the following command from your package directory:

twine upload dist/*

If successful, your package will be live on PyPI. You can find it at:

https://pypi.org/project/searchgenius/

# Key Commands
pip install searchgenius 

python test_myfunctions.py pytest
