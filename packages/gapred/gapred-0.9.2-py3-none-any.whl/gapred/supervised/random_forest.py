import numpy as np
from collections import Counter
from gapred.supervised.decision_tree import DecisionTree  # Using your own DecisionTree implementation

class RandomForest:
    def __init__(self, n_estimators=10, max_depth=None, max_features="sqrt", random_state=None):
        """
        Initialize the Random Forest model.
        :param n_estimators: Number of trees in the forest.
        :param max_depth: Maximum depth of each tree.
        :param max_features: Number of features to consider for the best split ("sqrt" or "log2").
        :param random_state: Seed for reproducibility.
        """
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.max_features = max_features
        self.random_state = random_state
        self.trees = []
        self.features_indices = []

    def _bootstrap_sample(self, X, y):
        """
        Generate a bootstrap sample of the data.
        """
        n_samples = X.shape[0]
        indices = np.random.choice(n_samples, size=n_samples, replace=True)
        return X[indices], y[indices]

    def fit(self, X_train, y_train):
        """
        Fit the Random Forest model to the training data.
        """
        np.random.seed(self.random_state)
        self.trees = []
        self.features_indices = []

        n_features = X_train.shape[1]
        max_features = (
            int(np.sqrt(n_features)) if self.max_features == "sqrt" 
            else int(np.log2(n_features)) if self.max_features == "log2" 
            else n_features
        )

        for _ in range(self.n_estimators):
            X_sample, y_sample = self._bootstrap_sample(X_train, y_train)
            feature_indices = np.random.choice(n_features, size=max_features, replace=False)
            self.features_indices.append(feature_indices)

            tree = DecisionTree(max_depth=self.max_depth, random_state=self.random_state)  # Use your DecisionTree
            tree.fit(X_sample[:, feature_indices], y_sample)
            self.trees.append(tree)

    def predict(self, X_test):
        """
        Predict the class labels for test data.
        """
        tree_predictions = np.array([
            tree.predict(X_test[:, feature_indices])
            for tree, feature_indices in zip(self.trees, self.features_indices)
        ])
        majority_votes = [Counter(tree_predictions[:, i]).most_common(1)[0][0] for i in range(X_test.shape[0])]
        return np.array(majority_votes)


# Example usage
# if __name__ == "__main__":
#     # Generate a synthetic dataset
#     np.random.seed(42)
#     X = np.random.rand(200, 5) * 10
#     y = np.random.choice([0, 1], size=200)

#     # Split into training and testing sets
#     split_index = int(0.8 * len(X))
#     X_train, X_test = X[:split_index], X[split_index:]
#     y_train, y_test = y[:split_index], y[split_index:]

#     # Random Forest
#     rf = RandomForest(n_estimators=50, max_depth=5, max_features="sqrt", random_state=42)
#     rf.fit(X_train, y_train)
#     rf_predictions = rf.predict(X_test)

#     print("RandomForest Predictions:", rf_predictions)