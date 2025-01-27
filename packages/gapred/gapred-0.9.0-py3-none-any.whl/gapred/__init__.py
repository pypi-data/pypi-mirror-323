# gapred/__init__.py

# Import KNN from the correct location
from gapred.supervised.knn import KNN

# Explicitly define the public API of the package
__all__ = ["KNN"]