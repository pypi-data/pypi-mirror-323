import numpy as np


class GaussianNB:
    def __init__(self):
        self.means = None
        self.variances = None
        self.priors = None
        self.classes = None

    def fit(self, X_train, y_train):
        """
        Fit the model to the training data.
        """
        self.classes = np.unique(y_train)
        self.means = {}
        self.variances = {}
        self.priors = {}

        for c in self.classes:
            X_c = X_train[y_train == c]
            self.means[c] = np.mean(X_c, axis=0)
            self.variances[c] = np.var(X_c, axis=0)
            self.priors[c] = X_c.shape[0] / X_train.shape[0]

    def predict(self, X_test):
        """
        Predict the class labels for test data.
        """
        predictions = [self._predict_single(x) for x in X_test]
        return np.array(predictions)

    def _predict_single(self, x):
        """
        Predict the label for a single sample.
        """
        posteriors = []
        for c in self.classes:
            prior = np.log(self.priors[c])
            likelihood = np.sum(np.log(self._gaussian_likelihood(c, x)))
            posterior = prior + likelihood
            posteriors.append(posterior)
        return self.classes[np.argmax(posteriors)]

    def _gaussian_likelihood(self, c, x):
        """
        Compute the Gaussian likelihood for a class.
        """
        mean = self.means[c]
        variance = self.variances[c]
        numerator = np.exp(-0.5 * ((x - mean) ** 2) / (variance + 1e-9))
        denominator = np.sqrt(2 * np.pi * variance + 1e-9)
        return numerator / denominator


class MultinomialNB:
    def __init__(self):
        self.class_log_prior = None
        self.feature_log_prob = None
        self.classes = None

    def fit(self, X_train, y_train):
        """
        Fit the model to the training data.
        """
        self.classes = np.unique(y_train)
        class_counts = np.array([np.sum(y_train == c) for c in self.classes])
        self.class_log_prior = np.log(class_counts / len(y_train))

        feature_counts = np.array([np.sum(X_train[y_train == c], axis=0) for c in self.classes])
        smoothed_feature_counts = feature_counts + 1  # Additive smoothing
        smoothed_class_counts = smoothed_feature_counts.sum(axis=1, keepdims=True)
        self.feature_log_prob = np.log(smoothed_feature_counts / smoothed_class_counts)

    def predict(self, X_test):
        """
        Predict the class labels for test data.
        """
        log_probs = X_test @ self.feature_log_prob.T + self.class_log_prior
        return self.classes[np.argmax(log_probs, axis=1)]


class BernoulliNB:
    def __init__(self, alpha=1.0):
        self.alpha = alpha
        self.class_log_prior = None
        self.feature_log_prob = None
        self.classes = None

    def fit(self, X_train, y_train):
        """
        Fit the model to the training data.
        """
        self.classes = np.unique(y_train)
        class_counts = np.array([np.sum(y_train == c) for c in self.classes])
        self.class_log_prior = np.log(class_counts / len(y_train))

        feature_counts = np.array([np.sum(X_train[y_train == c], axis=0) for c in self.classes])
        smoothed_feature_counts = feature_counts + self.alpha  # Additive smoothing
        smoothed_class_counts = smoothed_feature_counts.sum(axis=1, keepdims=True)
        self.feature_log_prob = np.log(smoothed_feature_counts / (class_counts[:, None] + 2 * self.alpha))

    def predict(self, X_test):
        """
        Predict the class labels for test data.
        """
        log_probs = X_test @ self.feature_log_prob.T + (1 - X_test) @ np.log(1 - np.exp(self.feature_log_prob.T))
        log_probs += self.class_log_prior
        return self.classes[np.argmax(log_probs, axis=1)]


# Example usage
# if __name__ == "__main__":
#     X = np.random.rand(100, 2) * 10
#     y = np.random.choice([0, 1], size=100)

#     split_index = int(0.8 * len(X))
#     X_train, X_test = X[:split_index], X[split_index:]
#     y_train, y_test = y[:split_index], y[split_index:]

#     # Gaussian Naive Bayes
#     gnb = GaussianNB()
#     gnb.fit(X_train, y_train)
#     gnb_predictions = gnb.predict(X_test)

#     print("GaussianNB Predictions:", gnb_predictions)

#     # Example dataset for MultinomialNB
#     X_multinomial = np.random.randint(0, 5, (100, 3))  # Non-negative integer features
#     y_multinomial = np.random.choice([0, 1], size=100)

#     # Split dataset
#     X_train_m, X_test_m = X_multinomial[:split_index], X_multinomial[split_index:]
#     y_train_m, y_test_m = y_multinomial[:split_index], y_multinomial[split_index:]

#     # Multinomial Naive Bayes
#     mnb = MultinomialNB()
#     mnb.fit(X_train_m, y_train_m)
#     mnb_predictions = mnb.predict(X_test_m)

#     print("MultinomialNB Predictions:", mnb_predictions)

#     # Example dataset for BernoulliNB
#     X_bernoulli = np.random.choice([0, 1], size=(100, 4))  # Binary features
#     y_bernoulli = np.random.choice([0, 1], size=100)

#     # Split dataset
#     X_train_b, X_test_b = X_bernoulli[:split_index], X_bernoulli[split_index:]
#     y_train_b, y_test_b = y_bernoulli[:split_index], y_bernoulli[split_index:]

#     # Bernoulli Naive Bayes
#     bnb = BernoulliNB()
#     bnb.fit(X_train_b, y_train_b)
#     bnb_predictions = bnb.predict(X_test_b)

#     print("BernoulliNB Predictions:", bnb_predictions)