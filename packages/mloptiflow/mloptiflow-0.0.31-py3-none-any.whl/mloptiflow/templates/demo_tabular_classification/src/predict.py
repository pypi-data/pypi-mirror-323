"""
Minimalistic demo example for a tabular classification paradigm (predict.py).
"""

import joblib
import logging
import logging.config
from pathlib import Path
from typing import Optional, Any, Dict, Union, List
import numpy as np
import pandas as pd
import mlflow
from sklearn.base import BaseEstimator
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_breast_cancer

try:
    from logger.logger_config import LOGGING_CONFIG
except ImportError:
    from mloptiflow.templates.demo_tabular_classification.logger.logger_config import (
        LOGGING_CONFIG,
    )

logging.config.dictConfig(LOGGING_CONFIG)


class PredictionError(Exception):
    pass


class ModelPredictor:
    def __init__(
        self,
        model_dir: str = "out/models",
        run_id: Optional[str] = None,
        model_name: Optional[str] = None,
        tracking_uri: Optional[str] = None,
    ):
        self.model_dir = Path(model_dir)
        self.tracking_uri = tracking_uri or "file:./mlruns"
        mlflow.set_tracking_uri(self.tracking_uri)
        self.run_id = run_id or self._get_latest_successful_run()
        self.model_name = model_name or "XGBoost"
        self.model: Optional[BaseEstimator] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_names: List[str] = list(load_breast_cancer().feature_names)
        self._load_artifacts()

    def _get_latest_successful_run(self) -> str:
        client = mlflow.tracking.MlflowClient()
        experiment = client.get_experiment_by_name("demo_tabular_classification")

        if experiment is None:
            raise PredictionError("No MLflow experiment found")

        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            filter_string="status = 'FINISHED'",
            order_by=["start_time DESC"],
            max_results=1,
        )

        if not runs:
            raise PredictionError("No successful runs found")

        return runs[0].info.run_id

    def _load_artifacts(self) -> None:
        try:
            model_uri = f"runs:/{self.run_id}/{self.model_name}_model"
            self.model = mlflow.sklearn.load_model(model_uri)
            self.scaler = joblib.load(self.model_dir / "scaler.joblib")

        except Exception as e:
            logging.error(f"Failed to load artifacts: {str(e)}")
            raise PredictionError(f"Failed to load artifacts: {str(e)}") from e

    def predict(self, X: Union[pd.DataFrame, np.ndarray]) -> Dict[str, Any]:
        try:
            if isinstance(X, np.ndarray):
                X = pd.DataFrame(X, columns=self.feature_names)

            X_scaled = self.scaler.transform(X)

            y_pred = self.model.predict(X_scaled)
            y_pred_proba = self.model.predict_proba(X_scaled)

            return {
                "predictions": y_pred,
                "probabilities": y_pred_proba,
                "prediction_classes": self.model.classes_,
            }
        except Exception as e:
            logging.error(f"Failed to make predictions: {str(e)}")
            raise PredictionError(f"Failed to make predictions: {str(e)}") from e

    def predict_single(
        self, features: Union[np.ndarray, List[float]]
    ) -> Dict[str, Any]:
        features_array = np.array(features).reshape(1, -1)
        result = self.predict(features_array)
        return {
            "prediction": result["predictions"][0],
            "probability": result["probabilities"][0],
            "classes": result["prediction_classes"],
        }


def main():
    """
    different from defaults:
    predictor = ModelPredictor(run_id="your_run_id", model_name="your_model_name")
    """
    try:
        predictor = ModelPredictor()
        example_features = load_breast_cancer().data[0]
        result = predictor.predict_single(example_features)

        print("\nPrediction Results:")
        print(f"Predicted Class: {result['prediction']}")
        print(f"Class Probabilities: {result['probability']}")
        print(f"Classes: {result['classes']}")

    except Exception as e:
        logging.error(f"Error in prediction pipeline: {str(e)}")
        raise


if __name__ == "__main__":
    main()
