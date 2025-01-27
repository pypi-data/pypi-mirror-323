import numpy as np
from collections import Counter

class KNN:
    def __init__(self, k=3):
        self.k = k
        self.data = None
        self.labels = None

    def fit(self, X_train, y_train):
        """
        Store the training data and labels.

        Parameters:
        - X_train: ndarray of shape (n_samples, n_features)
        - y_train: ndarray of shape (n_samples,)
        """
        self.data = X_train
        self.labels = y_train

    def predict(self, X_test):
        """
        Predict the class labels for the test data.

        Parameters:
        - X_test: ndarray of shape (m_samples, n_features)

        Returns:
        - predictions: ndarray of shape (m_samples,)
        """
        predictions = []
        for point in X_test:
            distances = self._compute_distances(point)
            neighbors = self._get_neighbors(distances)
            label = self._vote(neighbors)
            predictions.append(label)
        return np.array(predictions)

    def _compute_distances(self, point):
        """
        Compute the distances between a test point and all training points.

        Parameters:
        - point: ndarray of shape (n_features,)

        Returns:
        - distances: ndarray of shape (n_samples,)
        """
        distances = np.linalg.norm(self.data - point, axis=1)
        return distances

    def _get_neighbors(self, distances):
        """
        Find the indices of the k nearest neighbors.

        Parameters:
        - distances: ndarray of shape (n_samples,)

        Returns:
        - neighbors: list of k indices
        """
        return np.argsort(distances)[:self.k]

    def _vote(self, neighbors):
        """
        Determine the most common class among the neighbors.

        Parameters:
        - neighbors: list of indices of the k nearest neighbors

        Returns:
        - most_common_label: the label with the majority vote
        """
        neighbor_labels = self.labels[neighbors]
        most_common_label = Counter(neighbor_labels).most_common(1)[0][0]
        return most_common_label


# Example usage
# if __name__ == "__main__":
#     X_train = np.array([[1, 2], [2, 3], [3, 3], [6, 8], [7, 9]])
#     y_train = np.array([0, 0, 0, 1, 1])  

#     X_test = np.array([[3, 4], [5, 7]])

#     knn = KNN(k=3)
#     knn.fit(X_train, y_train)

#     predictions = knn.predict(X_test)
#     print("Predictions:", predictions)
