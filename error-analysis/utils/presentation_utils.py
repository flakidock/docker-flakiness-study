import pandas as pd
from IPython.display import display


def display_metrics(values, metrics, title="", round_decimals=2, coeff=1):
    """
    Display metrics in a DataFrame.
    
    Args:
        values (list): List of values corresponding to each metric.
        metrics (list): List of metrics.
    """
    values = [round(value*coeff, round_decimals) for value in values]
    
    # Create a DataFrame
    df = pd.DataFrame({'Metrics': metrics, 'Values': values})
    
    # Display the DataFrame
    if title:
        print(title)
    display(df)
    
    return df






