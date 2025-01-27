# Imports
from gapred.supervised.knn import KNN
from gapred.supervised.linear_regression import LinearRegression
from gapred.supervised.decision_tree import DecisionTree
from gapred.supervised.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from gapred.supervised.random_forest import RandomForest

# Calls
__all__ = ["KNN", "LinearRegression", "DecisionTree", "GaussianNB", "MultinomialNB", "BernoulliNB", "RandomForest"]