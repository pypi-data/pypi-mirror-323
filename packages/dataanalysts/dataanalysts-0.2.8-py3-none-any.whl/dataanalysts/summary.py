
import pandas as pd
import numpy as np

def summary(df):
    """
    Generate a comprehensive summary of a DataFrame, including:
        - Column names
        - Data types
        - Non-null count
        - Number of unique values
        - Minimum, maximum, mean, and median (for numeric columns)
        - Top value and frequency (for categorical columns)

    Parameters:
        df (pd.DataFrame): Input DataFrame

    Returns:
        pd.DataFrame: A DataFrame summarizing the input DataFrame.
    """
    summary_data = []

    for column in df.columns:
        col_data = {
            'Column': column,
            'Data Type': df[column].dtype,
            'Non-Null Count': df[column].notnull().sum(),
            'Unique Values': df[column].nunique()
        }

        if np.issubdtype(df[column].dtype, np.number):
            col_data.update({
                'Min': df[column].min(),
                'Max': df[column].max(),
                'Mean': df[column].mean(),
                'Median': df[column].median(),
                'Top': None,
                'Frequency': None
            })
        elif df[column].dtype == 'object':
            top_value = df[column].mode()[0] if not df[column].mode().empty else None
            col_data.update({
                'Min': None,
                'Max': None,
                'Mean': None,
                'Median': None,
                'Top': top_value,
                'Frequency': df[column].value_counts().iloc[0] if top_value else None
            })
        else:
            col_data.update({
                'Min': None,
                'Max': None,
                'Mean': None,
                'Median': None,
                'Top': None,
                'Frequency': None
            })

        summary_data.append(col_data)

    summary_df = pd.DataFrame(summary_data)
    return summary_df
