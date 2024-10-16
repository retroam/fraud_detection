# Fraud Detection Package

This package provides tools for building, training, and evaluating fraud detection models. It includes features for data loading, preprocessing, model training, hyperparameter optimization, and model comparison.

## Features
- Data loading from DuckDB
- Data quality report generation
- Feature engineering and preprocessing
- Model training with Logistic Regression, GBM, and XGBoost
- Hyperparameter optimization with Bayesian Optimization
- Model comparison and evaluation

## Installation
```sh
pip install .
```

## Usage
This package comes with a command-line interface (CLI) that makes it easy to interact with.

### Generate a Quality Report
```sh
fraud_detection generate_quality_report --db_path "interview_database.db" --query_file "data.sql"
```

### Train a Model
```sh
fraud_detection train --model_type "logistic" --save_model "logistic_model.pkl"
```

### Compare Models
```sh
fraud_detection compare --models "logistic,gbm,xgb"
```

### Optimize Hyperparameters
```sh
fraud_detection optimize
```

