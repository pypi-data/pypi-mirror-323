import numpy as np

class LinearRegression:
    def __init__(self, learning_rate=0.01, n_iterations=1000):
        """
        Initialize the Linear Regression model.

        Parameters:
        - learning_rate: float, learning rate for gradient descent
        - n_iterations: int, number of iterations for gradient descent
        """
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.weights = None
        self.bias = None

    def fit(self, X_train, y_train):
        """
        Train the model using gradient descent.

        Parameters:
        - X_train: ndarray of shape (n_samples, n_features)
        - y_train: ndarray of shape (n_samples,)
        """
        n_samples, n_features = X_train.shape
        self.weights = np.zeros(n_features)
        self.bias = 0

        for _ in range(self.n_iterations):
            # Predicted values
            y_predicted = self._predict(X_train)

            # Calculate gradients
            dw = (1 / n_samples) * np.dot(X_train.T, (y_predicted - y_train))
            db = (1 / n_samples) * np.sum(y_predicted - y_train)

            # Update weights and bias
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db

    def predict(self, X_test):
        """
        Predict the target values for the test data.

        Parameters:
        - X_test: ndarray of shape (m_samples, n_features)

        Returns:
        - predictions: ndarray of shape (m_samples,)
        """
        return self._predict(X_test)

    def _predict(self, X):
        """
        Calculate the predicted values based on the current weights and bias.

        Parameters:
        - X: ndarray of shape (n_samples, n_features)

        Returns:
        - y_predicted: ndarray of shape (n_samples,)
        """
        return np.dot(X, self.weights) + self.bias


# Example usage
# if __name__ == "__main__":
#     X_train = np.array([[1], [2], [3], [4], [5]])
#     y_train = np.array([1.2, 2.3, 2.9, 4.4, 5.1])  # Continuous targets
# 
#     X_test = np.array([[6], [7]])
# 
#     lr = LinearRegression(learning_rate=0.01, n_iterations=1000)
#     lr.fit(X_train, y_train)
# 
#     predictions = lr.predict(X_test)
#     print("Predictions:", predictions)
