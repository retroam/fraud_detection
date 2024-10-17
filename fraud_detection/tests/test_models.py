import unittest
from sklearn.linear_model import LogisticRegression
from fraud_detection.models import create_pipeline, compare_models
import pandas as pd
from typing import Dict

class TestModels(unittest.TestCase):

    def test_create_pipeline(self) -> None:
        model = LogisticRegression()
        pipeline = create_pipeline(model)
        self.assertTrue(hasattr(pipeline, 'fit'))
        self.assertTrue(hasattr(pipeline, 'predict'))

    def test_compare_models(self) -> None:
        X_test = pd.DataFrame({
            'feature1': [0.5, 1.5, 2.5, 3.5],
            'feature2': [1, 0, 1, 0]
        })
        y_test = pd.Series([0, 1, 0, 1])
        model = create_pipeline(LogisticRegression()).fit(X_test, y_test)
        models: Dict[str, LogisticRegression] = {'LogisticRegression': model}
        results = compare_models(models, X_test, y_test, display_viz=False)
        self.assertIsInstance(results, pd.DataFrame)
        self.assertGreater(len(results), 0)

if __name__ == '__main__':
    unittest.main()
