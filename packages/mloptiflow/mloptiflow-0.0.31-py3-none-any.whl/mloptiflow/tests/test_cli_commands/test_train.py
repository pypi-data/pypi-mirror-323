import pytest
from unittest.mock import patch
import os
from click.testing import CliRunner
from pathlib import Path
from mloptiflow.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_mlflow():
    with patch("mlflow.set_tracking_uri"), patch(
        "mlflow.create_experiment"
    ) as mock_create_exp, patch("mlflow.get_experiment") as mock_get_exp, patch(
        "mlflow.start_run"
    ), patch("mlflow.log_params"), patch("mlflow.log_metrics"), patch(
        "mlflow.sklearn.log_model"
    ):
        mock_exp = type("Experiment", (), {"experiment_id": "test_id"})()
        mock_create_exp.return_value = "test_id"
        mock_get_exp.return_value = mock_exp

        yield


def test_train_command_basic(runner, temp_dir):
    """Test basic training command execution with MLflow integration."""
    with runner.isolated_filesystem(temp_dir=temp_dir) as fs:
        result_init = runner.invoke(
            cli, ["init", "test-project", "--paradigm", "demo_tabular_classification"]
        )
        assert result_init.exit_code == 0

        project_path = Path(fs) / "test-project"
        original_dir = os.getcwd()

        try:
            os.chdir(project_path)
            (project_path / "mlruns").mkdir(exist_ok=True)

            result_train = runner.invoke(
                cli, ["train", "start"], catch_exceptions=False
            )

            if result_train.exit_code != 0:
                print(f"Training command failed with output:\n{result_train.output}")
                print(f"Exception: {result_train.exception}")

            assert result_train.exit_code == 0
            assert "Starting model training..." in result_train.output
            assert "Training completed successfully!" in result_train.output

            model_dir = project_path / "out" / "models"
            assert model_dir.exists()
            assert (model_dir / "scaler.joblib").exists()

            mlruns_dir = project_path / "mlruns"
            assert mlruns_dir.exists()

        finally:
            os.chdir(original_dir)


def test_train_command_no_project(runner, temp_dir):
    """Test training command outside of project directory."""
    with runner.isolated_filesystem(temp_dir=temp_dir):
        result_train = runner.invoke(cli, ["train", "start"])
        assert result_train.exit_code != 0
        assert "train.py not found in src directory" in result_train.output
