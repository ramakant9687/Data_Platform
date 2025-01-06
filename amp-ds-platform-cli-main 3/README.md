# Platform CLI

A CLI Tool used to create and manage Spark Jobs and Data Pipelines

## Installation

```bash
pip install amp-ds-platform-cli
```

## Usage

```python
amp-ds-platform-cli spark-job create --name new_spark_job --file new_spark_job.py --config new_spark_job.yml
```

## Development

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment
4. Install development dependencies: `pip install -e ".[dev,test]"`

## Testing

Run tests with:
```bash
pytest
```

Run flake8 with:
```bash
flake8
```

Run both with:
```bash
tox
```
