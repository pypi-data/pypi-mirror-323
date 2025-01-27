import numpy as np

class DecisionTree:
    def __init__(self, max_depth=None, random_state=None):
        """
        Initialize the Decision Tree model.

        Parameters:
        - max_depth: int, the maximum depth of the tree (default: None, no limit)
        - random_state: int or None, random state for reproducibility (default: None)
        """
        self.max_depth = max_depth
        self.random_state = random_state
        self.tree = None
        if self.random_state is not None:
            np.random.seed(self.random_state)

    def fit(self, X_train, y_train):
        """
        Build the decision tree based on the training data.

        Parameters:
        - X_train: ndarray of shape (n_samples, n_features)
        - y_train: ndarray of shape (n_samples,)
        """
        self.tree = self._build_tree(X_train, y_train)

    def predict(self, X_test):
        """
        Predict the class labels for the test data.

        Parameters:
        - X_test: ndarray of shape (m_samples, n_features)

        Returns:
        - predictions: ndarray of shape (m_samples,)
        """
        predictions = [self._traverse_tree(x, self.tree) for x in X_test]
        return np.array(predictions)

    def _build_tree(self, X, y, depth=0):
        """
        Recursively build the decision tree.

        Parameters:
        - X: ndarray of shape (n_samples, n_features)
        - y: ndarray of shape (n_samples,)
        - depth: int, current depth of the tree

        Returns:
        - tree: dict, representing the tree structure
        """
        n_samples, n_features = X.shape
        n_classes = len(np.unique(y))

        # Stopping conditions
        if n_classes == 1 or n_samples == 0 or (self.max_depth is not None and depth >= self.max_depth):
            return np.argmax(np.bincount(y))

        # Find the best split
        best_feature, best_threshold = self._best_split(X, y)
        if best_feature is None:
            return np.argmax(np.bincount(y))

        # Split the data
        left_idx = X[:, best_feature] <= best_threshold
        right_idx = X[:, best_feature] > best_threshold

        # Recursively build the left and right subtrees
        left_subtree = self._build_tree(X[left_idx], y[left_idx], depth + 1)
        right_subtree = self._build_tree(X[right_idx], y[right_idx], depth + 1)

        return {"feature": best_feature, "threshold": best_threshold, "left": left_subtree, "right": right_subtree}

    def _best_split(self, X, y):
        """
        Find the best feature and threshold to split the data.

        Parameters:
        - X: ndarray of shape (n_samples, n_features)
        - y: ndarray of shape (n_samples,)

        Returns:
        - best_feature: int, index of the feature to split on
        - best_threshold: float, value of the threshold to split on
        """
        best_gain = -1
        best_feature, best_threshold = None, None
        n_samples, n_features = X.shape

        for feature in range(n_features):
            thresholds = np.unique(X[:, feature])
            for threshold in thresholds:
                gain = self._information_gain(X[:, feature], y, threshold)
                if gain > best_gain:
                    best_gain = gain
                    best_feature = feature
                    best_threshold = threshold

        return best_feature, best_threshold

    def _information_gain(self, feature_column, y, threshold):
        """
        Calculate the information gain for a given feature and threshold.

        Parameters:
        - feature_column: ndarray of shape (n_samples,)
        - y: ndarray of shape (n_samples,)
        - threshold: float, value of the threshold to split on

        Returns:
        - gain: float, information gain from the split
        """
        left_idx = feature_column <= threshold
        right_idx = feature_column > threshold

        if len(y[left_idx]) == 0 or len(y[right_idx]) == 0:
            return 0

        # Compute entropy before and after the split
        parent_entropy = self._entropy(y)
        left_entropy = self._entropy(y[left_idx])
        right_entropy = self._entropy(y[right_idx])

        # Compute weighted average entropy after the split
        n = len(y)
        n_left, n_right = len(y[left_idx]), len(y[right_idx])
        child_entropy = (n_left / n) * left_entropy + (n_right / n) * right_entropy

        # Information gain
        gain = parent_entropy - child_entropy
        return gain

    def _entropy(self, y):
        """
        Calculate the entropy of a label distribution.

        Parameters:
        - y: ndarray of shape (n_samples,)

        Returns:
        - entropy: float, entropy of the distribution
        """
        proportions = np.bincount(y) / len(y)
        return -np.sum([p * np.log2(p) for p in proportions if p > 0])

    def _traverse_tree(self, x, tree):
        """
        Traverse the tree to make a prediction for a single data point.

        Parameters:
        - x: ndarray of shape (n_features,)
        - tree: dict, the tree structure

        Returns:
        - prediction: int, predicted class label
        """
        if not isinstance(tree, dict):
            return tree

        feature = tree["feature"]
        threshold = tree["threshold"]
        if x[feature] <= threshold:
            return self._traverse_tree(x, tree["left"])
        else:
            return self._traverse_tree(x, tree["right"])


# Example usage
# if __name__ == "__main__":
#     X_train = np.array([[1, 2], [2, 3], [3, 3], [6, 8], [7, 9]])
#     y_train = np.array([0, 0, 0, 1, 1])
# 
#     X_test = np.array([[3, 4], [5, 7]])
# 
#     dt = DecisionTree(max_depth=3)
#     dt.fit(X_train, y_train)
# 
#     predictions = dt.predict(X_test)
#     print("Predictions:", predictions)
