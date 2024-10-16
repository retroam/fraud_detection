import unittest
from unittest.mock import patch, mock_open
from fraud_detection.data import load_data, quality_report
import pandas as pd
import duckdb

class TestData(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data="SELECT * FROM test_table;")
    @patch("fraud_detection.data.duckdb.connect")
    def test_load_data(self, mock_duckdb_connect, mock_file) -> None:
        mock_connection = mock_duckdb_connect.return_value
        mock_connection.execute.return_value.fetchdf.return_value = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['x', 'y', 'z']
        })
        db_path = 'test_database.db'
        query_file = 'test_query.sql'
        data = load_data(db_path, query_file, winsorize_data=False)
        self.assertIsInstance(data, pd.DataFrame)
        self.assertEqual(len(data), 3)

    @patch("builtins.open", new_callable=mock_open, read_data="SELECT * FROM test_table;")
    @patch("fraud_detection.data.duckdb.connect")
    def test_winsorize_data(self, mock_duckdb_connect, mock_file) -> None:
        mock_connection = mock_duckdb_connect.return_value
        mock_connection.execute.return_value.fetchdf.return_value = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50]
        })
        db_path = 'test_database.db'
        query_file = 'test_query.sql'
        data = load_data(db_path, query_file, winsorize_data=True)
        self.assertIsInstance(data, pd.DataFrame)
        self.assertEqual(len(data), 5)

    def test_quality_report(self) -> None:
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, None],
            'B': ['x', 'y', 'z', None, 'w'],
            'C': [None, 1.5, 2.5, 3.5, 4.5]
        })
        report = quality_report(df)
        self.assertEqual(report.loc['A', 'dtype'], 'float64')
        self.assertEqual(report.loc['B', 'missing'], 1)
        self.assertEqual(report.loc['C', 'min'], 1.5)

if __name__ == '__main__':
    unittest.main()