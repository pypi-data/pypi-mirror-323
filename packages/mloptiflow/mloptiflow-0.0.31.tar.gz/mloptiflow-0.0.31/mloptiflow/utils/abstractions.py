from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator


class BaseProcessor(ABC):
    @abstractmethod
    def load_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        pass

    @abstractmethod
    def preprocess_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        pass


class BaseTrainer(ABC):
    def __init__(self, X_train, X_test, y_train, y_test) -> None:
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        return None

    @abstractmethod
    def train_models(self) -> Any:
        pass

    @abstractmethod
    def _evaluate_model(self, model: BaseEstimator) -> Dict[str, Any]:
        pass
