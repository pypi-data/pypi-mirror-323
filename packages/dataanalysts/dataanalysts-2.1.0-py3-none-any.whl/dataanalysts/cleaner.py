
import pandas as pd
import numpy as np
import logging
from dataanalysts.exceptions import DataCleaningError

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    filename='cleaner.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def clean(df, strategy=None, **kwargs):
    """
    Data cleaning function with separate strategies for specific cleaning tasks.

    Parameters:
        df (pd.DataFrame): Input DataFrame.
        strategy (str): Cleaning operation ("remove_duplicates", "handle_missing", "fix_structural", "handle_outliers",
                        "convert_dtype", "encode_categorical", "scale", "filter", "split_column", "validate").
        kwargs: Additional parameters for specific strategies.

    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    try:
        if strategy == 'remove_duplicates':
            initial_rows = len(df)
            df.drop_duplicates(inplace=True)
            removed_rows = initial_rows - len(df)
            print(f"Removed {removed_rows} duplicate rows.")

        elif strategy == 'handle_missing':
            missing_strategy = kwargs.get('strategy', 'mean')
            value = kwargs.get('value', None)
            if missing_strategy == 'fill':
                if isinstance(value, dict):
                    df = df.fillna(value)
                else:
                    raise ValueError("For 'fill' strategy, provide 'value' as a dictionary.")
                print(f"Filled missing values with specified values: {value}.")
            elif missing_strategy in ['mean', 'median', 'mode']:
                for col in df.select_dtypes(include=['number']).columns:
                    if missing_strategy == 'mean':
                        df[col] = df[col].fillna(df[col].mean())
                    elif missing_strategy == 'median':
                        df[col] = df[col].fillna(df[col].median())
                    elif missing_strategy == 'mode' and not df[col].mode().empty:
                        df[col] = df[col].fillna(df[col].mode()[0])
                print(f"Filled missing values using {missing_strategy} strategy.")

        elif strategy == 'fix_structural':
            column = kwargs.get('column')
            if column in df.columns:
                fix_strategy = kwargs.get('fix_strategy', 'lowercase')
                if fix_strategy == 'lowercase':
                    df[column] = df[column].str.lower()
                elif fix_strategy == 'uppercase':
                    df[column] = df[column].str.upper()
                print(f"Fixed structural issues in column {column} using {fix_strategy} strategy.")

        elif strategy == 'handle_outliers':
            column = kwargs.get('column', None)
            if column and column in df.columns:
                q1 = df[column].quantile(0.25)
                q3 = df[column].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                df[column] = np.where(df[column] < lower_bound, lower_bound, df[column])
                df[column] = np.where(df[column] > upper_bound, upper_bound, df[column])
                print(f"Handled outliers in column {column} using the IQR method.")

        elif strategy == 'convert_dtype':
            column = kwargs.get('column')
            dtype = kwargs.get('dtype', 'float')
            if column in df.columns:
                df[column] = df[column].astype(dtype)
                print(f"Converted column {column} to data type {dtype}.")

        elif strategy == 'encode_categorical':
            columns = kwargs.get('columns', [])
            encoding = kwargs.get('encoding', 'onehot')
            if encoding == 'onehot':
                df = pd.get_dummies(df, columns=columns)
                print(f"Performed one-hot encoding for columns: {columns}.")

        elif strategy == 'scale':
            columns = kwargs.get('columns', df.select_dtypes(include=['number']).columns)
            scaler = kwargs.get('scaler', 'minmax')
            for col in columns:
                if scaler == 'minmax':
                    df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
                elif scaler == 'standard':
                    df[col] = (df[col] - df[col].mean()) / df[col].std()
            print(f"Scaled columns {columns} using {scaler} scaling.")

        elif strategy == 'filter':
            condition = kwargs.get('condition')
            df = df.query(condition)
            print(f"Filtered rows based on condition: {condition}.")

        elif strategy == 'split_column':
            column = kwargs.get('column')
            new_columns = kwargs.get('new_columns', [])
            delimiter = kwargs.get('delimiter', ' ')
            if column in df.columns:
                df[new_columns] = df[column].str.split(delimiter, expand=True)
                print(f"Split column {column} into {new_columns}.")

        elif strategy == 'validate':
            column = kwargs.get('column')
            min_value = kwargs.get('min_value', None)
            max_value = kwargs.get('max_value', None)
            if column in df.columns:
                df[column] = np.clip(df[column], min_value, max_value)
                print(f"Validated column {column} with range ({min_value}, {max_value}).")

        else:
            print("No valid strategy selected. Please provide a valid strategy.")

        logging.info(f"Data cleaned successfully using strategy: {strategy}")
        return df

    except Exception as e:
        logging.error(f"Data Cleaning Error: {str(e)}")
        raise Exception(f"Data Cleaning Error: {str(e)}")

def interactive_clean(df):
    """
    Interactive cleaning process for datasets with user-defined options.

    Parameters:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    try:
        while True:
            print("\nInteractive Cleaning Options:")
            print("1. Handle Missing Values")
            print("2. Remove Duplicates")
            print("3. Fix Structural Errors")
            print("4. Handle Outliers")
            print("5. Convert Data Types")
            print("6. Encode Categorical Variables")
            print("7. Scale Features")
            print("8. Filter Rows")
            print("9. Split Columns")
            print("10. Validate Data")
            print("11. Exit")

            option = input("Choose an option (1-11): ").strip()

            if option == '1':
                strategy = input("Enter strategy (mean/median/mode/fill): ").strip()
                value = eval(input("Enter value for 'fill' strategy (as a dictionary): ") or "{}")
                df = clean(df, strategy='handle_missing', missing_strategy=strategy, value=value)
            elif option == '2':
                df = clean(df, strategy='remove_duplicates')
            elif option == '3':
                column = input("Enter column to fix structural errors: ").strip()
                fix_strategy = input("Enter fix strategy (lowercase/uppercase): ").strip()
                df = clean(df, strategy='fix_structural', column=column, fix_strategy=fix_strategy)
            elif option == '4':
                column = input("Enter column to handle outliers: ").strip()
                df = clean(df, strategy='handle_outliers', column=column)
            elif option == '5':
                column = input("Enter column to convert data type: ").strip()
                dtype = input("Enter target data type (int/float/str): ").strip()
                df = clean(df, strategy='convert_dtype', column=column, dtype=dtype)
            elif option == '6':
                columns = input("Enter columns to encode (comma-separated): ").strip().split(',')
                df = clean(df, strategy='encode_categorical', columns=columns)
            elif option == '7':
                columns = input("Enter columns to scale (comma-separated): ").strip().split(',')
                scaler = input("Enter scaler type (minmax/standard): ").strip()
                df = clean(df, strategy='scale', columns=columns, scaler=scaler)
            elif option == '8':
                condition = input("Enter filter condition (e.g., Age > 30): ").strip()
                df = clean(df, strategy='filter', condition=condition)
            elif option == '9':
                column = input("Enter column to split: ").strip()
                new_columns = input("Enter new column names (comma-separated): ").strip().split(',')
                delimiter = input("Enter delimiter (default: space): ").strip()
                df = clean(df, strategy='split_column', column=column, new_columns=new_columns, delimiter=delimiter)
            elif option == '10':
                column = input("Enter column to validate: ").strip()
                min_value = float(input("Enter minimum value: ").strip())
                max_value = float(input("Enter maximum value: ").strip())
                df = clean(df, strategy='validate', column=column, min_value=min_value, max_value=max_value)
            elif option == '11':
                print("Exiting Interactive Cleaning.")
                break
            else:
                print("Invalid option. Please try again.")

        logging.info("Interactive cleaning completed successfully.")
        return df

    except Exception as e:
        logging.error("Interactive Cleaning Error: %s", str(e))
        raise DataCleaningError(f"Interactive Cleaning Error: {str(e)}")
