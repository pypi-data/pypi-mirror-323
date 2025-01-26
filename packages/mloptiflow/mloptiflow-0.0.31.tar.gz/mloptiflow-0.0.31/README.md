# MLOPTIFLOW

Dynamic MLOps Framework with Integrated CLI for Automated ML Project Inception, Kafka-Driven Real-Time Model Monitoring, and Adaptive Canary Deployment Architectures

## Background

We are introducing a Python framework and library with an integrated CLI, designed to streamline ML lifecycle management by automating project inception, real-time model monitoring, and adaptive canary deployment processes. The library facilitates automated project setup across various configurable ML paradigms (whether it is a Random Forest classification, XGBoost regression, T5-based time-series forecasting, encoder-only / encoder-decoder / decoder-only transformer-based NLP downstream tasks, or practically any other configurable ML paradigm) with optimized directories, subdirectories and configuration files adhering to recommended practices in ML development. The library features a plugin architecture for extensibility, allowing integration with other core components / packages, such as real-time model monitoring with anomaly detection mechanisms, adaptive canary deployment architectures, and integrated UI for monitoring and deployment control. Model monitoring is implemented using high-throughput, low-latency data streaming tool Apache Kafka. Deployed ML models act as Kafka producers, emitting real-time inference data and performance metrics serialized with Apache Avro for schema enforcement and efficiency. Model monitoring is accompanied with anomaly, data, and concept drift detection mechanisms via techniques like PSI, Isolation Forests, or LSTM auto-encoders. Adaptive canary deployment architectures and strategies are implemented specifically for ML models using Kubernetes for container orchestration and Istio as a service mesh for traffic management and routing between baseline and canary versions at granular levels. Integrated UI for monitoring and deployment control is implemented using Vanilla JavaScript and Bootstrap on the client-side, and FastAPI / LitServe on the server-side.

## Installation

1. create a new virtual environment with python ^3.11 and activate it (currently works with virtualenv, venv, and conda)

2. install poetry:

```bash
pip install poetry
```

3. install mloptiflow:

```bash
pip install mloptiflow
```

4. initialize a new project and choose a name and paradigm (currently supported paradigms are: `tabular_regression`, `tabular_classification`, `demo_tabular_classification`)[demo ones are just a minimalistic examples of the paradigm]:

```bash
mloptiflow init <your-project-name> --paradigm=<paradigm-name>
```

5. `cd` into your project directory:

```bash
cd <your-project-name>
```

6. install dependencies:

```bash
poetry install
```

or if using `pip`:

```bash
pip install -r requirements.txt
```

## DEMO Test

1. create a new virtual environment with python ^3.11 and activate it

2. install poetry:

```bash
pip install poetry
```

3. install mloptiflow:

```bash
pip install mloptiflow
```

4. initialize a new project with the name `demo-project` and paradigm `demo_tabular_classification`:

```bash
mloptiflow init demo-project --paradigm=demo_tabular_classification
```

5. `cd` into your project directory:

```bash
cd demo-project
```

6. install dependencies:

```bash
poetry install
```

7. run the training pipeline:

```bash
mloptiflow train start
```

8. run and test the inference API:

```bash
mloptiflow deploy start --with-api-test
```

## Usage
- TBA

## Support
- TBA

## Roadmap
- TBA

## Contributing

- do not push directly to the main branch, open MR instead
- after implementing and before pushing, run:

```bash
poetry run python scripts/dev.py lint
poetry run python scripts/dev.py format
poetry run python scripts/dev.py fix
```

- after implementing and before pushing, implement corresponding tests and run them:

```bash
poetry run pytest
```

- if the tests fail, fix them and run tests again until they pass

## License
MIT

