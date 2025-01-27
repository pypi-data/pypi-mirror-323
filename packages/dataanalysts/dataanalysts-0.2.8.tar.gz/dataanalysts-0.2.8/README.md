# DataAnalysts Package

**DataAnalysts** is a robust and versatile Python library meticulously designed to simplify and enhance the data analysis process. It caters to users across diverse domains, including students, professional data analysts, researchers, and enthusiasts. The library integrates powerful modules for data cleaning, transformation, and visualization, enabling seamless handling of datasets with minimal coding effort.

Whether you're dealing with messy datasets or preparing sophisticated visualizations, DataAnalysts offers an intuitive and interactive interface to perform your tasks with precision and efficiency.
---


### **Data Loading:**

- **CSV Files:**

  - Easily load datasets from CSV files with automatic logging.

- **Excel Files:**

  - Load data from Excel sheets with customizable sheet selection.

---

### **Error Handling:**

- **Robust Exception Handling:**

  - Provides clear error messages for debugging and ensures smooth execution.

---

### **Interactive Tools:**

- **Data Cleaning:**

  - Step-by-step interactive data cleaning options.

- **Data Transformation:**

  - Hands-on transformation with flexible menu options.

- **Data Visualization:**

  - Interactive plotting with multiple customization options.



---

## 🛠️ **Installation Steps**

### **1. Install the Package from PyPI**
To use the library in Google Colab or your local environment, install it directly from PyPI:

```bash
pip install dataanalysts
!pip install dataanalysts
```

---

## 💡 **Usage Examples**

### **1. Import the Library**
```python
import dataanalysts as da
import pandas as pd
```

### **2. Load Data**
```python
df = da.csv('data.csv')
df_excel = da.excel('data.xlsx', sheet_name='Sheet1')
```

### Data Summary 

The **Data Summary ** simplifies the exploration of datasets by providing a comprehensive summary of your DataFrame in a single step. This module is designed to give users a complete overview of their data, including column-level statistics and metadata, in a tabular format.

---

### Key Features

1. **Column Overview:**
   - Lists all columns in the DataFrame.
   - Displays the data type of each column.

2. **Data Completeness:**
   - Shows the number of non-null values per column.
   - Highlights columns with missing data.

3. **Uniqueness:**
   - Reports the number of unique values per column.

4. **Descriptive Statistics (Numeric Columns):**
   - Minimum, maximum, mean, and median values.

5. **Descriptive Statistics (Categorical Columns):**
   - Most frequent ("Top") value and its frequency.

6. **Single-Line Syntax:**
   - Access all of the above information with one simple command.

---

### Syntax and Examples

#### Generate Summary

Use the `da.summary()` function to generate a summary of your DataFrame.

**Syntax:**
```python
da.summary(df)
```

**Example:**
```python
import pandas as pd
import dataanalysts as da

# Sample dataset
data = {
    'Name': ['Alice', 'Bob', 'Charlie', 'Alice', 'Bob'],
    'Age': [25, 30, 35, None, 30],
    'Gender': ['F', 'M', 'M', 'F', None],
    'Score': [85, 90, 78, 92, 88]
}
df = pd.DataFrame(data)

# Generate and display summary
summary_df = da.summary(df)
print(summary_df)
```

**Output:**
| Column   | Data Type   | Non-Null Count | Unique Values | Min   | Max   | Mean  | Median | Top      | Frequency |
|----------|-------------|----------------|---------------|-------|-------|-------|--------|----------|-----------|
| Name     | object      | 5              | 3             | None  | None  | None  | None   | Alice    | 2         |
| Age      | float64     | 4              | 3             | 25.0  | 35.0  | 30.0  | 30.0   | None     | None      |
| Gender   | object      | 4              | 2             | None  | None  | None  | None   | F        | 2         |
| Score    | int64       | 5              | 5             | 78    | 92    | 86.6  | 88.0   | None     | None      |

---

### How It Works

1. **Numeric Columns:**
   - Calculates key statistics like min, max, mean, and median.

2. **Categorical Columns:**
   - Identifies the most frequent value ("Top") and its frequency.

3. **General Information:**
   - Reports column data types, non-null counts, and unique values for all columns.

---

### Logging

- All operations are logged to ensure traceability.
- Errors during summary generation are recorded for debugging purposes.

---

This module provides a quick and easy way to understand your data's structure and key characteristics, making it ideal for analysts, data scientists, and developers.



### **Data Cleaning**

The **Data Cleaning** module simplifies common data preprocessing tasks like handling missing values, removing duplicates, fixing structural errors, and more. With this module, you can efficiently prepare your data for analysis or modeling using intuitive and flexible one-line commands.

---

### Key Features

1. **Remove Duplicates**: Automatically detect and remove duplicate rows from your dataset.
2. **Handle Missing Values**: Fill or drop missing values using customizable strategies (mean, median, mode, or specific values).
3. **Fix Structural Errors**: Standardize text data by converting it to lowercase or uppercase and correcting inconsistencies.
4. **Handle Outliers**: Detect and handle outliers in numerical columns using the Interquartile Range (IQR) method or custom thresholds.
5. **Convert Data Types**: Convert columns to specific data types like integer, float, or string.
6. **Encode Categorical Variables**: Perform one-hot encoding or label encoding for categorical columns.
7. **Scale Features**: Normalize or standardize numerical columns using Min-Max or Standard scaling.
8. **Filter Rows**: Filter rows based on conditions like column values or ranges.
9. **Split Columns**: Split a single column into multiple columns using a specified delimiter.
10. **Validate Data**: Ensure numerical values are within specified ranges and clip those that fall outside.
11. **Interactive Cleaning**: Provides an interactive menu to perform various cleaning tasks step by step.

---

### Syntax and Examples

#### 1. **Remove Duplicates**
Remove duplicate rows from the dataset.

**Syntax:**
```python
da.clean(df, strategy='remove_duplicates')
```
**Example:**
```python
cleaned_df = da.clean(df, strategy='remove_duplicates')
```

---

#### 2. **Handle Missing Values**
Fill or drop missing values using various strategies.

**Syntax:**
```python
da.clean(df, strategy='handle_missing', missing_strategy='mean')
```
**Options:**
- `missing_strategy`: 'mean', 'median', 'mode', or 'fill'
- `value`: Custom value for filling (required if `missing_strategy='fill'`)

**Example:**
```python
# Fill missing values with mean
cleaned_df = da.clean(df, strategy='handle_missing', missing_strategy='mean')

# Fill missing values with custom values
cleaned_df = da.clean(df, strategy='handle_missing', missing_strategy='fill', value={'Age': 25, 'Gender': 'Unknown'})
```

---

#### 3. **Fix Structural Errors**
Standardize text data by fixing structural inconsistencies.

**Syntax:**
```python
da.clean(df, strategy='fix_structural', column='Category', fix_strategy='lowercase')
```
**Options:**
- `column`: Column to clean.
- `fix_strategy`: 'lowercase' or 'uppercase'.

**Example:**
```python
cleaned_df = da.clean(df, strategy='fix_structural', column='Category', fix_strategy='lowercase')
```

---

#### 4. **Handle Outliers**
Detect and handle outliers in numerical columns.

**Syntax:**
```python
da.clean(df, strategy='handle_outliers', column='Score')
```
**Options:**
- `column`: Column to handle outliers.

**Example:**
```python
cleaned_df = da.clean(df, strategy='handle_outliers', column='Score')
```

---

#### 5. **Convert Data Types**
Convert columns to specific data types.

**Syntax:**
```python
da.clean(df, strategy='convert_dtype', column='Age', dtype='int')
```
**Options:**
- `column`: Column to convert.
- `dtype`: Target data type ('int', 'float', 'str').

**Example:**
```python
cleaned_df = da.clean(df, strategy='convert_dtype', column='Age', dtype='int')
```

---

#### 6. **Encode Categorical Variables**
Perform one-hot encoding for categorical variables.

**Syntax:**
```python
da.clean(df, strategy='encode_categorical', columns=['Category'])
```
**Options:**
- `columns`: List of categorical columns.

**Example:**
```python
cleaned_df = da.clean(df, strategy='encode_categorical', columns=['Category'])
```

---

#### 7. **Scale Features**
Normalize or standardize numerical columns.

**Syntax:**
```python
da.clean(df, strategy='scale', columns=['Age'], scaler='minmax')
```
**Options:**
- `columns`: List of numerical columns to scale.
- `scaler`: 'minmax' or 'standard'.

**Example:**
```python
cleaned_df = da.clean(df, strategy='scale', columns=['Age'], scaler='minmax')
```

---

#### 8. **Filter Rows**
Filter rows based on conditions.

**Syntax:**
```python
da.clean(df, strategy='filter', condition="Age > 30")
```
**Options:**
- `condition`: String condition to filter rows.

**Example:**
```python
cleaned_df = da.clean(df, strategy='filter', condition="Age > 30")
```

---

#### 9. **Split Columns**
Split a single column into multiple columns using a specified delimiter.

**Syntax:**
```python
da.clean(df, strategy='split_column', column='FullName', new_columns=['FirstName', 'LastName'], delimiter=' ')
```
**Options:**
- `column`: Column to split.
- `new_columns`: List of new column names.
- `delimiter`: Delimiter to use for splitting.

**Example:**
```python
cleaned_df = da.clean(df, strategy='split_column', column='FullName', new_columns=['FirstName', 'LastName'], delimiter=' ')
```

---

#### 10. **Validate Data**
Ensure numerical values are within specified ranges.

**Syntax:**
```python
da.clean(df, strategy='validate', column='Score', min_value=0, max_value=100)
```
**Options:**
- `column`: Column to validate.
- `min_value`: Minimum acceptable value.
- `max_value`: Maximum acceptable value.

**Example:**
```python
cleaned_df = da.clean(df, strategy='validate', column='Score', min_value=0, max_value=100)
```

---

#### 11. **Interactive Cleaning**
Perform interactive cleaning step by step using a menu-based approach.

**Syntax:**
```python
da.interactive_clean(df)
```

**Example:**
```python
cleaned_df = da.interactive_clean(df)
```

---

### Comprehensive Example
Here’s how you can use the `clean` function to perform multiple cleaning operations:

```python
import dataanalysts as da
import pandas as pd

# Sample dataset
data = {
    'Name': ['Alice', 'Bob', 'Alice'],
    'Age': [25, None, 25],
    'Gender': ['F', 'M', None],
    'FullName': ['Alice Smith', 'Bob Johnson', 'Alice Smith']
}
df = pd.DataFrame(data)

# Remove duplicates
cleaned_df = da.clean(df, strategy='remove_duplicates')

# Handle missing values
cleaned_df = da.clean(cleaned_df, strategy='handle_missing', missing_strategy='fill', value={'Age': 30, 'Gender': 'Unknown'})

# Fix structural errors
cleaned_df = da.clean(cleaned_df, strategy='fix_structural', column='Gender', fix_strategy='uppercase')

# Split column
cleaned_df = da.clean(cleaned_df, strategy='split_column', column='FullName', new_columns=['FirstName', 'LastName'], delimiter=' ')

# Interactive cleaning
cleaned_df = da.interactive_clean(cleaned_df)
```

---

### Logging
- Logs are stored in the `cleaner.log` file.
- Each cleaning step is logged with details about the operation and parameters used.
- Errors during cleaning are logged for debugging purposes.

This module simplifies data cleaning, making it accessible and efficient for analysts, researchers, and developers alike.



### **4. Data Transformation**

The **Data Transformation Module** enables comprehensive data preprocessing and transformation for datasets, including scaling, dimensionality reduction, encoding, and more. The module supports both direct and interactive transformation methods.

---

### **Key Features**

- **Scaling**: Standard, Min-Max, and Robust scaling strategies for numeric columns.
- **Encoding**: Label encoding for categorical columns.
- **Dimensionality Reduction**: Principal Component Analysis (PCA) to reduce dataset dimensions.
- **Duplicate Removal**: Automatically remove duplicate rows.
- **Low-Variance Feature Removal**: Remove features with variance below a defined threshold.
- **Interactive Transformation**: Choose transformation steps interactively.

---

### **Syntax and Examples**

#### **1. Scaling**

Scales numeric columns based on the selected strategy:

- **Standard Scaling**: Centers data around mean (0) with standard deviation (1).
- **Min-Max Scaling**: Scales data to a range of [0, 1].
- **Robust Scaling**: Handles outliers by scaling data based on the interquartile range (IQR).

**Syntax**:
```python
import dataanalysts as da

# Standard Scaling
df_transformed = da.transform(df, strategy='standard')

# Min-Max Scaling
df_transformed = da.transform(df, strategy='minmax')

# Robust Scaling
df_transformed = da.transform(df, strategy='robust')
```

---

#### **2. Encoding**

Encodes categorical columns into numeric values using label encoding. This is particularly useful for machine learning models that require numeric data.

**Syntax**:
```python
# Encode categorical columns
df_transformed = da.transform(df, encode_categorical=True)
```

---

#### **3. Duplicate Removal**

Automatically removes duplicate rows from the dataset.

**Syntax**:
```python
# Remove duplicate rows
df_transformed = da.transform(df, remove_duplicates=True)
```

---

#### **4. Low-Variance Feature Removal**

Removes features with variance below a specified threshold to reduce noise in the data.

**Syntax**:
```python
# Remove features with variance below 0.01
df_transformed = da.transform(df, remove_low_variance=True, variance_threshold=0.01)
```

---

#### **5. Dimensionality Reduction (PCA)**

Uses Principal Component Analysis to reduce the number of features while retaining most of the variance in the dataset.

**Syntax**:
```python
# Apply PCA to retain 3 components
df_pca = da.transform(df_transformed, reduce_dimensionality=True, n_components=3)
```

---

#### **6. Interactive Transformation**

Provides an interactive menu for selecting transformation steps one at a time.

**Menu Options**:

1. Apply Standard Scaling
2. Apply Min-Max Scaling
3. Apply Robust Scaling
4. Encode Categorical Columns
5. Remove Duplicates
6. Remove Low-Variance Features
7. Apply PCA for Dimensionality Reduction
8. Exit Transformation

**Syntax**:
```python
# Perform interactive transformation
df_interactive_transform = da.interactive_transform(df)
```

---

### **Comprehensive Example**

Here’s an end-to-end example combining multiple transformations:

```python
import dataanalysts as da
import pandas as pd

# Sample dataset
data = {
    'Age': [25, 30, 35, 40, 45],
    'Salary': [50000, 60000, 70000, 80000, 90000],
    'Department': ['HR', 'IT', 'Finance', 'IT', 'HR']
}
df = pd.DataFrame(data)

# Step 1: Apply standard scaling
df_transformed = da.transform(df, strategy='standard')

# Step 2: Apply PCA to reduce dimensions to 2 components
df_pca = da.transform(df_transformed, reduce_dimensionality=True, n_components=2)

# Step 3: Perform additional transformations interactively
df_final = da.interactive_transform(df_pca)

print(df_final)
```

---

### **Logging**

- Logs are stored in the `transformer.log` file.
- Each transformation step is logged with details about the operation and parameters used.
- Errors during transformations are also logged for debugging purposes.


### **5. Data Visualization**

The **Data Visualization ** provides advanced tools for creating insightful and customized visual representations of your dataset. With this module, you can generate a variety of plots, including histograms, scatter plots, heatmaps, and more, with customization options for size, titles, and styles.

---

### **Key Features**

- **Histogram**: Visualize the distribution of a single numeric column.
- **Bar Chart**: Compare values across categories.
- **Line Chart**: Display trends over time or sequential data.
- **Scatter Plot**: Show relationships between two numeric columns.
- **Heatmap**: Visualize correlations between numeric columns.
- **Pair Plot**: Display pairwise relationships in a dataset.
- **Box Plot**: Compare distributions of a numeric column across categories.
- **Violin Plot**: Combine box plot and density plot for richer insights.
- **Interactive Visualization**: Select and generate plots interactively.

---

### **Syntax and Examples**

#### **1. Histogram**
Visualize the distribution of a single numeric column.

**Syntax**:
```python
da.histogram(df, column='age', bins=30, kde=True)
```

**Customization Options**:
- `bins`: Number of bins for the histogram.
- `kde`: Whether to display the Kernel Density Estimate.
- `size`: Tuple specifying figure size.
- `title_fontsize`: Font size for the title.
- `axis_fontsize`: Font size for axis labels.
- `custom_title`: Custom title for the chart.

---

#### **2. Bar Chart**
Compare values across categories.

**Syntax**:
```python
da.barchart(df, x_col='city', y_col='population')
```

**Customization Options**:
- `size`: Tuple specifying figure size.
- `title_fontsize`: Font size for the title.
- `axis_fontsize`: Font size for axis labels.
- `custom_title`: Custom title for the chart.

---

#### **3. Line Chart**
Display trends over time or sequential data.

**Syntax**:
```python
da.linechart(df, x_col='date', y_col='sales')
```

**Customization Options**:
- `size`: Tuple specifying figure size.
- `title_fontsize`: Font size for the title.
- `axis_fontsize`: Font size for axis labels.
- `custom_title`: Custom title for the chart.

---

#### **4. Scatter Plot**
Show relationships between two numeric columns.

**Syntax**:
```python
da.scatter(df, x_col='height', y_col='weight', hue='gender')
```

**Customization Options**:
- `hue`: Column for color encoding.
- `size`: Tuple specifying figure size.
- `title_fontsize`: Font size for the title.
- `axis_fontsize`: Font size for axis labels.
- `custom_title`: Custom title for the chart.

---

#### **5. Heatmap**
Visualize correlations between numeric columns.

**Syntax**:
```python
da.heatmap(df)
```

**Customization Options**:
- `annot`: Whether to annotate the heatmap with correlation values.
- `cmap`: Colormap for the heatmap.
- `size`: Tuple specifying figure size.
- `title_fontsize`: Font size for the title.
- `custom_title`: Custom title for the chart.

---

#### **6. Pair Plot**
Display pairwise relationships in a dataset.

**Syntax**:
```python
da.pairplot(df, hue='category')
```

**Customization Options**:
- `hue`: Column for color encoding.
- `size`: Tuple specifying figure size for each subplot.
- `title_fontsize`: Font size for the title.
- `custom_title`: Custom title for the chart.

---

#### **7. Box Plot**
Compare distributions of a numeric column across categories.

**Syntax**:
```python
da.boxplot(df, x_col='region', y_col='sales')
```

**Customization Options**:
- `size`: Tuple specifying figure size.
- `title_fontsize`: Font size for the title.
- `axis_fontsize`: Font size for axis labels.
- `custom_title`: Custom title for the chart.

---

#### **8. Violin Plot**
Combine box plot and density plot for richer insights.

**Syntax**:
```python
da.violinplot(df, x_col='region', y_col='sales')
```

**Customization Options**:
- `size`: Tuple specifying figure size.
- `title_fontsize`: Font size for the title.
- `axis_fontsize`: Font size for axis labels.
- `custom_title`: Custom title for the chart.

---

#### **9. Interactive Visualization**

Provides an interactive menu for generating various plots one at a time.

**Menu Options**:
1. Histogram
2. Bar Chart
3. Line Plot
4. Scatter Plot
5. Heatmap
6. Pair Plot
7. Box Plot
8. Violin Plot
9. Exit Visualization

**Syntax**:
```python
# Perform interactive visualization
da.interactive_plot(df)
```

---

### **Comprehensive Example**

Here’s how you can use the `visualizer` functions to create multiple plots:

```python
import dataanalysts as da
import pandas as pd

# Sample dataset
data = {
    'age': [25, 30, 35, 40, 45],
    'salary': [50000, 60000, 70000, 80000, 90000],
    'city': ['NY', 'LA', 'SF', 'CHI', 'HOU'],
    'gender': ['M', 'F', 'F', 'M', 'M']
}
df = pd.DataFrame(data)

# Histogram
da.histogram(df, column='age', bins=20, kde=True)

# Bar Chart
da.barchart(df, x_col='city', y_col='salary')

# Scatter Plot
da.scatter(df, x_col='age', y_col='salary', hue='gender')

# Heatmap
da.heatmap(df)

# Interactive Visualization
da.interactive_plot(df)
```

---

### **Logging**

- Logs are stored in the `visualizer.log` file.
- Each visualization step is logged with details about the operation and parameters used.
- Errors during visualizations are also logged for debugging purposes.

---

This module provides highly customizable and interactive visualizations to gain insights from your data effectively.

---

## 🤝 **Contributing**
Contributions are welcome! Please submit a pull request via our GitHub Repository.

---

## 📜 **License**
This project is licensed under the MIT License. See the LICENSE file for details.

---

## 🛠️ **Support**
If you encounter any issues, feel free to open an issue on our GitHub Issues page.

