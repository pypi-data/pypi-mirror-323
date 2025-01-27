
import dataanalysts as da
import pandas as pd
import time
from google.colab import files

# Step 1: Upload Dataset Files
print("\nStep 1: Upload Dataset Files")
uploaded = files.upload()

# Check uploaded files
for filename in uploaded.keys():
    print(f"Uploaded file: {filename}")

# Step 2: Load Dataset Based on File Extension
print("\nStep 2: Load Dataset")
try:
    for filename in uploaded.keys():
        if filename.endswith('.csv'):
            df = da.load_csv(filename)
        elif filename.endswith('.xlsx'):
            df = da.load_excel(filename)
        else:
            print(f"Unsupported file format: {filename}")
            df = None

    if df is not None:
        print("\nDataset Preview:")
        print(df.head())
except da.DataLoadingError as e:
    print(e)

# Step 3: Data Cleaning
print("\nStep 3: Data Cleaning")
try:
    # Clean missing values with mean strategy
    df_cleaned = da.clean(df, strategy='mean')
    print("\nCleaned Dataset Preview:")
    print(df_cleaned.head())

    # Handle outliers
    df_cleaned_outliers = da.clean(df_cleaned, handle_outliers=True)
    print("\nDataset after Outlier Handling:")
    print(df_cleaned_outliers.head())

    # Interactive Cleaning (Uncomment to test)
    # df_interactive_clean = da.interactive_clean(df)
except da.DataCleaningError as e:
    print(e)

# Step 4: Data Transformation
print("\nStep 4: Data Transformation")
try:
    # Apply Standard Scaling
    df_transformed = da.transform(df_cleaned_outliers, strategy='standard')
    print("\nTransformed Dataset Preview:")
    print(df_transformed.head())

    # Apply Dimensionality Reduction with PCA
    df_pca = da.transform(df_transformed, reduce_dimensionality=True, n_components=3)
    print("\nDataset after PCA (3 Components):")
    print(df_pca.head())

    # Interactive Transformation (Uncomment to test)
    # df_interactive_transform = da.interactive_transform(df_cleaned_outliers)
except da.DataTransformationError as e:
    print(e)

# Step 5: Data Visualization
print("\nStep 5: Data Visualization")
try:
    # Histogram
    da.histogram(df_transformed, column=df_transformed.columns[0], bins=20, kde=True)

    # Bar Chart
    da.barchart(df_transformed, x_col=df_transformed.columns[0], y_col=df_transformed.columns[1])

    # Line Chart
    da.linechart(df_transformed, x_col=df_transformed.columns[0], y_col=df_transformed.columns[1])

    # Scatter Plot with optional hue
    da.scatter(df_transformed, x_col=df_transformed.columns[0], y_col=df_transformed.columns[1], hue=None)

    # Heatmap
    da.heatmap(df_transformed)

    # Pair Plot
    da.pairplot(df_transformed)

    # Box Plot
    da.boxplot(df_transformed, x_col=df_transformed.columns[0], y_col=df_transformed.columns[1])

    # Violin Plot
    da.violinplot(df_transformed, x_col=df_transformed.columns[0], y_col=df_transformed.columns[1])

    # Interactive Plot (Uncomment to test)
    # da.interactive_plot(df_transformed)
except da.DataVisualizationError as e:
    print(e)

# Final Message
print("\nAll Steps Completed Successfully!")
