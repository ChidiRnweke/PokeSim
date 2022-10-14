from sklearn.base import BaseEstimator, ClassifierMixin


class BaselineClassifier(BaseEstimator, ClassifierMixin):
    """Decides if player 1 or two wins based on a simple rule:
    if player 1 has more pokemon than player 2 they win.
    Otherwise, even in the case of a draw, they lose.
    """

    def __init__(self, decisionColumn: str = "diff") -> None:
        """
        Args:
            decisionColumn (int): Index of column you want to
            use to make the decision
        """
        self.decisionColumn = decisionColumn

    def fit(self, X, y):
        return self

    def predict(self, X) -> int:
        return (X[self.decisionColumn] > 0).astype(int)
