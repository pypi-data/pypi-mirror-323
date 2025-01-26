from typing import Any, Dict
import pandas as pd
import mlflow

from .base import MLflowTrackingMixin


class TabularMLflowTracking(MLflowTrackingMixin):
    def log_params(self, params: Dict[str, Any]) -> None:
        mlflow.log_params(params)

    def log_metrics(self, metrics: Dict[str, float]) -> None:
        mlflow.log_metrics(metrics)

    def log_model(self, model: Any, artifact_path: str) -> None:
        input_example = pd.DataFrame(
            self.X_train[0:1],
            columns=[f"feature_{i}" for i in range(self.X_train.shape[1])],
        )

        mlflow.sklearn.log_model(
            model,
            artifact_path,
            input_example=input_example,
            signature=mlflow.models.infer_signature(
                self.X_train, model.predict(self.X_train[:1])
            ),
        )
