
import pandas as pd
import numpy as np
import logging
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, LabelEncoder, OneHotEncoder
from sklearn.decomposition import PCA
from sklearn.feature_selection import VarianceThreshold
from dataanalysts.exceptions import DataTransformationError

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    filename='transformer.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def transform(
    df,
    strategy='standard',
    encode_categorical=False,
    remove_duplicates=True,
    reduce_dimensionality=False,
    n_components=None,
    remove_low_variance=False,
    variance_threshold=0.01
):
    """
    Perform comprehensive transformation of the dataset including scaling, encoding, deduplication, dimensionality reduction,
    and removal of low-variance features.

    Parameters:
        df (pd.DataFrame): Input DataFrame.
        strategy (str): Scaling strategy ('standard', 'minmax', 'robust').
        encode_categorical (bool): If True, encodes categorical columns.
        remove_duplicates (bool): If True, removes duplicate rows.
        reduce_dimensionality (bool): If True, applies PCA for dimensionality reduction.
        n_components (int or None): Number of components to keep for PCA (used if reduce_dimensionality=True).
        remove_low_variance (bool): If True, removes features with low variance.
        variance_threshold (float): Threshold for variance to filter features (used if remove_low_variance=True).

    Returns:
        pd.DataFrame: Transformed DataFrame.
    """
    try:
        # Remove duplicates if specified
        if remove_duplicates:
            initial_rows = len(df)
            df.drop_duplicates(inplace=True)
            dropped_rows = initial_rows - len(df)
            if dropped_rows > 0:
                print(f"Removed {dropped_rows} duplicate rows.")

        # Handle scaling for numeric columns
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns

        if not numeric_columns.empty:
            if strategy == 'standard':
                scaler = StandardScaler()
            elif strategy == 'minmax':
                scaler = MinMaxScaler()
            elif strategy == 'robust':
                scaler = RobustScaler()
            else:
                raise ValueError("Invalid strategy: Choose 'standard', 'minmax', or 'robust'")

            df[numeric_columns] = scaler.fit_transform(df[numeric_columns])
            print(f"{strategy.capitalize()} scaling applied on numeric columns.")
        else:
            print("No numeric columns found for scaling.")

        # Encode categorical columns if specified
        if encode_categorical:
            categorical_columns = df.select_dtypes(include=['object', 'category']).columns

            if not categorical_columns.empty:
                encoder = LabelEncoder()
                for col in categorical_columns:
                    df[col] = encoder.fit_transform(df[col])
                print("Categorical columns encoded successfully.")
            else:
                print("No categorical columns found for encoding.")

        # Remove low-variance features if specified
        if remove_low_variance:
            selector = VarianceThreshold(threshold=variance_threshold)
            df = pd.DataFrame(
                selector.fit_transform(df),
                columns=[col for col, var in zip(df.columns, selector.variances_) if var > variance_threshold]
            )
            print(f"Removed features with variance below {variance_threshold}.")

        # Apply dimensionality reduction if specified
        if reduce_dimensionality:
            if n_components is None:
                n_components = min(len(df.columns), len(df))
            pca = PCA(n_components=n_components)
            df = pd.DataFrame(
                pca.fit_transform(df),
                columns=[f"PCA_{i+1}" for i in range(n_components)]
            )
            print(f"Applied PCA and reduced dimensions to {n_components} components.")

        logging.info(
            "Transformation completed successfully with strategy: %s, encode_categorical: %s, remove_duplicates: %s, reduce_dimensionality: %s, n_components: %s, remove_low_variance: %s, variance_threshold: %s",
            strategy, encode_categorical, remove_duplicates, reduce_dimensionality, n_components, remove_low_variance, variance_threshold
        )
        return df

    except Exception as e:
        logging.error("Transformation Error: %s", str(e))
        raise DataTransformationError(f"Transformation Error: {str(e)}")

def interactive_transform(df):
    """
    Interactive Transformation Tool for Advanced Dataset Cleaning and Scaling.

    Parameters:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: Transformed DataFrame.
    """
    try:
        while True:
            print("\nInteractive Transformation Options:")
            print("1. Apply Standard Scaling")
            print("2. Apply Min-Max Scaling")
            print("3. Apply Robust Scaling")
            print("4. Encode Categorical Columns")
            print("5. Remove Duplicates")
            print("6. Remove Low-Variance Features")
            print("7. Apply PCA for Dimensionality Reduction")
            print("8. Exit Transformation")

            option = input("Enter your choice (1-8): ").strip()

            if option == '1':
                df = transform(df, strategy='standard')
            elif option == '2':
                df = transform(df, strategy='minmax')
            elif option == '3':
                df = transform(df, strategy='robust')
            elif option == '4':
                df = transform(df, encode_categorical=True)
            elif option == '5':
                df = transform(df, remove_duplicates=True)
            elif option == '6':
                threshold = float(input("Enter variance threshold (e.g., 0.01): ").strip())
                df = transform(df, remove_low_variance=True, variance_threshold=threshold)
            elif option == '7':
                components = int(input("Enter the number of components for PCA: ").strip())
                df = transform(df, reduce_dimensionality=True, n_components=components)
            elif option == '8':
                print("Exiting Transformation.")
                break
            else:
                print("Invalid option. Please try again.")

        logging.info("Interactive transformation completed successfully.")
        return df

    except Exception as e:
        logging.error("Interactive Transformation Error: %s", str(e))
        raise DataTransformationError(f"Interactive Transformation Error: {str(e)}")
