import pandas as pd
import logging
from dataanalysts.exceptions import DataLoadingError

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    filename='load.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def csv(file_path):
    """
    Load data from a CSV file.

    Parameters:
        file_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: Loaded data as a DataFrame.
    """
    try:
        df = pd.read_csv(file_path)
        logging.info(f"✅ CSV file '{file_path}' loaded successfully.")
        print(f"✅ CSV file '{file_path}' loaded successfully.")
        return df
    except Exception as e:
        logging.error(f"❌ CSV Loading Error: {str(e)}")
        raise DataLoadingError(f"❌ CSV Loading Error: {str(e)}")


def excel(file_path, sheet_name=0):
    """
    Load data from an Excel file.

    Parameters:
        file_path (str): Path to the Excel file.
        sheet_name (str/int): Sheet name or index.

    Returns:
        pd.DataFrame: Loaded data as a DataFrame.
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        logging.info(f"✅ Excel file '{file_path}' loaded successfully from sheet '{sheet_name}'.")
        print(f"✅ Excel file '{file_path}' loaded successfully from sheet '{sheet_name}'.")
        return df
    except Exception as e:
        logging.error(f"❌ Excel Loading Error: {str(e)}")
        raise DataLoadingError(f"❌ Excel Loading Error: {str(e)}")
