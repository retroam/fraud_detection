from setuptools import setup, find_packages

setup(
    name='fraud_detection',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'click>=8.0.0',
        'pandas',
        'scipy',
        'duckdb',
        'scikit-learn',
        'xgboost',
        'evidently',
        'bayesian-optimization'
    ],
    entry_points={
        'console_scripts': [
            'fraud_detection=fraud_detection.cli:cli',
        ],
    },
)