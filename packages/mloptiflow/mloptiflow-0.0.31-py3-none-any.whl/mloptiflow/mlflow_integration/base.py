from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
from pathlib import Path
import mlflow


class MLflowTrackingMixin(ABC):
    def __init__(
        self,
        tracking_uri: Optional[str] = None,
        experiment_name: Optional[str] = None,
        artifact_location: Optional[str] = None,
    ):
        self.tracking_uri = tracking_uri or "file:./mlruns"
        self.experiment_name = experiment_name or "demo_tabular_classification"
        self.artifact_location = artifact_location or "./mlruns"
        self.logger = logging.getLogger(self.__class__.__name__)

        Path(self.artifact_location).mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(self.tracking_uri)

        experiment = mlflow.get_experiment_by_name(self.experiment_name)
        if experiment is None:
            experiment_id = mlflow.create_experiment(
                name=self.experiment_name, artifact_location=self.artifact_location
            )
            self.experiment = mlflow.get_experiment(experiment_id)
        else:
            self.experiment = experiment

    def cleanup_mlflow_experiments(self) -> None:
        """Clean up corrupted MLflow experiments in the current tracking location."""
        mlruns_dir = Path("./mlruns")

        if not mlruns_dir.exists():
            return

        experiment_dirs = [
            d for d in mlruns_dir.iterdir() if d.is_dir() and d.name != ".trash"
        ]

        for exp_dir in experiment_dirs:
            if not (exp_dir / "meta.yaml").exists():
                import shutil

                self.logger.warning(
                    f"Removing corrupted experiment directory: {exp_dir}"
                )
                shutil.rmtree(exp_dir)

    def start_run(
        self, run_name: Optional[str] = None, nested: bool = False
    ) -> mlflow.ActiveRun:
        return mlflow.start_run(
            experiment_id=self.experiment.experiment_id,
            run_name=run_name,
            nested=nested,
        )

    @abstractmethod
    def log_params(self, params: Dict[str, Any]) -> None:
        """Log parameters to MLflow"""
        pass

    @abstractmethod
    def log_metrics(self, metrics: Dict[str, float]) -> None:
        """Log metrics to MLflow"""
        pass

    @abstractmethod
    def log_model(self, model: Any, artifact_path: str) -> None:
        """Log model to MLflow"""
        pass

    @property
    def X_train(self):
        return self._X_train

    @X_train.setter
    def X_train(self, value):
        self._X_train = value
