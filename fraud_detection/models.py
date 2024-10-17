from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from xgboost import XGBClassifier
from bayes_opt import BayesianOptimization
from sklearn.model_selection import cross_val_score
import numpy as np
import pandas as pd
from typing import Optional, Dict


def create_pipeline(model) -> make_pipeline:
    """
    Create a machine learning pipeline with imputer, scaler, and given model.
    """
    return make_pipeline(SimpleImputer(strategy='most_frequent'), StandardScaler(), model)

def train_model(model_type: str):
    """
    Train a fraud detection model based on the selected model type.
    """
    model_mapping = {
        'logistic': create_pipeline(LogisticRegression()),
        'gbm': create_pipeline(GradientBoostingClassifier()),
        'xgb': create_pipeline(XGBClassifier())
    }
    return model_mapping.get(model_type)

def compare_models(models: Dict[str, make_pipeline], X_test: pd.DataFrame, y_test: pd.Series, display_viz: bool = False) -> pd.DataFrame:
    """
    Compare the performance of multiple trained models.
    """
    from sklearn.metrics import roc_curve, precision_recall_curve, average_precision_score
    import matplotlib.pyplot as plt

    results = []
    for name, model in models.items():
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        avg_precision = average_precision_score(y_test, y_pred_proba)
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
        results.append({'model': name, 'avg_precision': avg_precision})

        if display_viz:
            plt.figure(figsize=(10, 5))
            plt.plot(fpr, tpr, label=f'{name} ROC Curve')
            plt.xlabel('False Positive Rate')
            plt.ylabel('True Positive Rate')
            plt.legend()
            plt.show()

            plt.figure(figsize=(10, 5))
            plt.plot(recall, precision, label=f'{name} Precision-Recall Curve')
            plt.xlabel('Recall')
            plt.ylabel('Precision')
            plt.legend()
            plt.show()

    return pd.DataFrame(results)

def optimize_model(X_train: pd.DataFrame, y_train: pd.Series) -> Dict[str, float]:
    """
    Optimize hyperparameters for Gradient Boosting Classifier using Bayesian Optimization.
    """
    def gbm_eval(n_estimators: float, learning_rate: float, max_depth: float, min_samples_split: float, min_samples_leaf: float, subsample: float) -> float:
        model = create_pipeline(GradientBoostingClassifier(
            n_estimators=int(n_estimators),
            learning_rate=learning_rate,
            max_depth=int(max_depth),
            min_samples_split=int(min_samples_split),
            min_samples_leaf=int(min_samples_leaf),
            subsample=subsample))
        return np.mean(cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy'))

    pbounds = {
        'n_estimators': (10, 500),
        'learning_rate': (0.01, 0.2),
        'max_depth': (3, 10),
        'min_samples_split': (2, 10),
        'min_samples_leaf': (1, 10),
        'subsample': (0.5, 1.0)
    }

    optimizer = BayesianOptimization(f=gbm_eval, pbounds=pbounds, random_state=42)
    optimizer.maximize()
    return optimizer.max
