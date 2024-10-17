import duckdb
import pandas as pd
from fraud_detection.utils import setup_logger
from scipy.stats.mstats import winsorize

logger = setup_logger()

def load_data(db_path: str, query_file: str, winsorize_data: bool = False) -> pd.DataFrame:
    """
    Load data from a SQL database and optionally winsorize.
    """
    con = duckdb.connect()
    con.execute("INSTALL 'sqlite'")
    con.execute("LOAD 'sqlite'");
    try:
        with open(query_file, 'r') as file:
            query = file.read()
        logger.info(f"Loading data from {db_path} with query: {query}")
        con = duckdb.connect(database=db_path, read_only=True)

        data = con.execute(query).fetchdf()
        if winsorize_data:
            data = _winsorize_data(data)
        return data
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

def _winsorize_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Winsorize numerical columns to reduce the influence of outliers.
    """
    for col in df.select_dtypes(include='number').columns:
        df[col] = winsorize(df[col], limits=[0.05, 0.05])
    return df

def quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a data quality report for a DataFrame.
    """
    dqr = pd.DataFrame(df.dtypes, columns=['dtype'])
    dqr['count'] = df.count()
    dqr['missing'] = df.isnull().sum()
    dqr['unique'] = df.nunique()
    dqr['min'] = df.min(numeric_only=True)
    dqr['max'] = df.max(numeric_only=True)
    return dqr