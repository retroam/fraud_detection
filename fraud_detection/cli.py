import click
from fraud_detection.data import load_data, quality_report
from fraud_detection.models import train_model, compare_models, optimize_model
from fraud_detection.utils import setup_logger

logger = setup_logger()

@click.group()
def cli() -> None:
    """CLI for Fraud Detection Package"""
    pass

@cli.command()
@click.option('--db_path', default='company_database.db', help='Path to DuckDB database.')
@click.option('--query_file', default='data.sql', help='Path to SQL query file.')
@click.option('--winsorize', default=False, is_flag=True, help='Option to winsorize the data.')
def generate_quality_report(db_path: str, query_file: str, winsorize: bool) -> None:
    """Generate a data quality report"""
    click.echo(f"Generating data quality report from {db_path}...")
    try:
        data = load_data(db_path, query_file, winsorize=winsorize)
        report = quality_report(data)
        report.to_csv('quality_report.csv', index=False)
        click.echo("Data quality report saved to 'quality_report.csv'")
    except Exception as e:
        logger.error(f"Failed to generate quality report: {e}")

@cli.command()
@click.option('--model_type', default='logistic', type=click.Choice(['logistic', 'gbm', 'xgb']), help='Type of model to train.')
@click.option('--save_model', default='model.pkl', help='Filename to save the trained model.')
def train(model_type: str, save_model: str) -> None:
    """Train a fraud detection model"""
    click.echo(f"Training {model_type} model...")
    try:
        model, X_train, y_train, X_test, y_test = train_model(model_type)
        click.echo(f"Model {model_type} trained successfully.")
        # Save model logic here, e.g. using joblib or pickle
    except Exception as e:
        logger.error(f"Failed to train model: {e}")

@cli.command()
@click.option('--models', default='logistic,gbm,xgb', help='Comma-separated list of models to compare.')
def compare(models: str) -> None:
    """Compare multiple models"""
    model_list = models.split(',')
    click.echo(f"Comparing models: {', '.join(model_list)}")
    try:
        comparison_results = compare_models(model_list)
        click.echo("Model comparison completed.")
        click.echo(comparison_results)
    except Exception as e:
        logger.error(f"Failed to compare models: {e}")

@cli.command()
def optimize() -> None:
    """Optimize model hyperparameters using Bayesian Optimization"""
    click.echo("Starting hyperparameter optimization...")
    try:
        best_params = optimize_model()
        click.echo(f"Optimization completed with best parameters: {best_params}")
    except Exception as e:
        logger.error(f"Failed to optimize model: {e}")

if __name__ == '__main__':
    cli()




