"""
Minimalistic demo example for a tabular classification paradigm (train.py).
"""


from typing import Optional, Any, ClassVar, List, Dict, TypedDict, Tuple
import joblib
from pathlib import Path
from dataclasses import dataclass
import logging
import logging.config
import random
import warnings
import numpy as np
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from xgboost import XGBClassifier
import mlflow

try:
    from logger.logger_config import LOGGING_CONFIG
except ImportError:
    from mloptiflow.templates.demo_tabular_classification.logger.logger_config import (
        LOGGING_CONFIG,
    )

from mloptiflow.utils.common import (
    method_timer,
    log_method_call,
    SingletonMeta,
)
from mloptiflow.utils.exceptions import (
    DataProcessingError,
    ModelTrainingError,
    ModelEvaluationError,
)
from mloptiflow.utils.abstractions import BaseProcessor, BaseTrainer


logging.config.dictConfig(LOGGING_CONFIG)
warnings.filterwarnings("ignore")
random.seed(hash("abc") % 2**32 - 1)
np.random.seed(hash("xyz") % 2**32 - 1)


@dataclass(frozen=True)
class DataProcessorConfig(metaclass=SingletonMeta):
    FEATURES: ClassVar[List[str]] = [
        feature for feature in load_breast_cancer().feature_names
    ]
    CATEGORICAL_FEATURES: ClassVar[List[str]] = []
    NUMERICAL_FEATURES: ClassVar[List[str]] = FEATURES


class ModelEvaluationResult(TypedDict):
    classification_report: str
    roc_auc_score: float
    brier_score: float
    y_pred: np.ndarray
    y_pred_proba: np.ndarray


class DataProcessor(BaseProcessor):
    def __init__(self):
        self.config = DataProcessorConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.scaler: Optional[StandardScaler] = None

    @log_method_call
    @method_timer
    def load_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        try:
            breast_cancer = load_breast_cancer()
            X = pd.DataFrame(breast_cancer.data, columns=self.config.FEATURES)
            y = pd.Series(breast_cancer.target, name="target")
            return X, y
        except Exception as e:
            self.logger.error("Error loading data")
            raise DataProcessingError(e) from e

    @log_method_call
    @method_timer
    def preprocess_data(
        self, X: pd.DataFrame, y: pd.Series
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, stratify=y, random_state=42
            )

            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)

            model_dir = Path("out/models")
            model_dir.mkdir(exist_ok=True)
            joblib.dump(self.scaler, model_dir / "scaler.joblib")
            return X_train_scaled, X_test_scaled, y_train, y_test
        except Exception as e:
            self.logger.error("Error preprocessing data")
            raise DataProcessingError(e) from e


class ModelTrainer(BaseTrainer):
    def __init__(self, X_train, X_test, y_train, y_test):
        super().__init__(X_train, X_test, y_train, y_test)
        self.models = {}
        self.results = {}
        self.best_params = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def initialize_models(random_state: int = 42) -> Dict[str, BaseEstimator]:
        return {
            "RandomForest": RandomForestClassifier(random_state=random_state),
            "XGBoost": XGBClassifier(
                random_state=random_state,
                eval_metric="logloss",
            ),
        }

    @staticmethod
    def get_param_distributions() -> Dict[str, Dict[str, Any]]:
        return {
            "RandomForest": {
                "n_estimators": [100, 200, 300, 400, 500],
                "max_depth": [None, 10, 20, 30, 40, 50],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
                "max_features": ["sqrt", "log2", None],
                "class_weight": ["balanced", "balanced_subsample", None],
            },
            "XGBoost": {
                "n_estimators": [100, 200, 300, 400, 500],
                "max_depth": [3, 4, 5, 6, 7, 8],
                "learning_rate": [0.01, 0.05, 0.1, 0.15, 0.2],
                "subsample": [0.6, 0.7, 0.8, 0.9, 1.0],
                "colsample_bytree": [0.6, 0.7, 0.8, 0.9, 1.0],
                "min_child_weight": [1, 3, 5, 7],
                "gamma": [0, 0.1, 0.2, 0.3, 0.4],
            },
        }

    @log_method_call
    @method_timer
    def train_models(self, random_state: int = 42) -> None:
        try:
            param_distributions = self.get_param_distributions()
            self.models = {}
            self.best_params = {}

            with mlflow.start_run(run_name="training_session") as parent_run:
                mlflow.log_params(
                    {
                        "n_samples_train": len(self.X_train),
                        "n_samples_test": len(self.X_test),
                        "n_features": self.X_train.shape[1],
                        "random_state": random_state,
                    }
                )

                for name, base_model in self.initialize_models(random_state).items():
                    self.logger.info(
                        f"Training {name} with hyperparameter optimization"
                    )

                    with mlflow.start_run(
                        run_name=f"{name}_training",
                        nested=True,
                        description=f"Hyperparameter optimization for {name}",
                        tags={"mlflow.parentRunId": parent_run.info.run_id},
                    ):
                        search = RandomizedSearchCV(
                            estimator=base_model,
                            param_distributions=param_distributions[name],
                            n_iter=20,
                            cv=5,
                            scoring="roc_auc",
                            n_jobs=-1,
                            random_state=random_state,
                            verbose=1,
                        )
                        search.fit(self.X_train, self.y_train)

                        mlflow.log_params(
                            {
                                f"{name}_param_space": str(param_distributions[name]),
                                f"{name}_best_params": str(search.best_params_),
                                f"{name}_cv_folds": 5,
                                f"{name}_n_iter": 20,
                            }
                        )

                        mlflow.log_metrics(
                            {
                                f"{name}_best_cv_score": search.best_score_,
                                f"{name}_mean_cv_time": search.cv_results_[
                                    "mean_fit_time"
                                ].mean(),
                            }
                        )

                        mlflow.sklearn.log_model(
                            search.best_estimator_,
                            f"{name}_model",
                            registered_model_name=name,
                            input_example=self.X_train[:1],
                        )

                        self.models[name] = search.best_estimator_
                        self.best_params[name] = search.best_params_
                        self.results[name] = self._evaluate_model(
                            search.best_estimator_
                        )

                        mlflow.log_metrics(
                            {
                                f"{name}_test_roc_auc": self.results[name][
                                    "roc_auc_score"
                                ]
                            }
                        )

        except Exception as e:
            self.logger.error("Error during model training and optimization")
            raise ModelTrainingError(e) from e

    @log_method_call
    @method_timer
    def _evaluate_model(self, model: BaseEstimator) -> ModelEvaluationResult:
        try:
            y_pred = model.predict(self.X_test)
            y_pred_proba = model.predict_proba(self.X_test)[:, 1]

            return {
                "classification_report": classification_report(self.y_test, y_pred),
                "roc_auc_score": roc_auc_score(self.y_test, y_pred_proba),
                "y_pred": y_pred,
                "y_pred_proba": y_pred_proba,
            }
        except Exception as e:
            self.logger.error("Error evaluating model")
            raise ModelEvaluationError(e) from e

    @log_method_call
    def print_results(self):
        for name in self.models:
            print(f"\n--- {name} Results ---")
            print(f"Best Parameters: {self.best_params[name]}")
            print("\nTest Set Performance:")
            print(self.results[name]["classification_report"])
            print(f"ROC AUC Score: {self.results[name]['roc_auc_score']:.4f}")

    @log_method_call
    def get_best_model(self, metric: str = "roc_auc_score") -> str:
        return max(self.results, key=lambda x: self.results[x][metric])

    @log_method_call
    def run_all(self) -> None:
        self.train_models()
        self.print_results()
        best_model = self.get_best_model()
        print(f"\nBest model based on ROC AUC score: {best_model}")
        return None


def main():
    try:
        mlruns_dir = Path("mlruns")
        mlruns_dir.mkdir(exist_ok=True)
        mlflow.set_tracking_uri("file:./mlruns")

        experiment_name = "demo_tabular_classification"
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            mlflow.create_experiment(name=experiment_name, artifact_location="./mlruns")
        mlflow.set_experiment(experiment_name)

        processor = DataProcessor()
        X, y = processor.load_data()
        X_train, X_test, y_train, y_test = processor.preprocess_data(X, y)

        trainer = ModelTrainer(X_train, X_test, y_train, y_test)
        trainer.run_all()

    except Exception as e:
        logging.error(f"Error during main execution: {str(e)}")
        raise


if __name__ == "__main__":
    main()
