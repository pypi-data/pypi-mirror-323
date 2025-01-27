
class DataCleaningError(Exception):
    """
    Exception raised for errors during data cleaning operations.

    Attributes:
        message (str): Explanation of the error.
    """
    def __init__(self, message="An error occurred during data cleaning."):
        super().__init__(message)

class DataTransformationError(Exception):
    """
    Exception raised for errors during data transformation operations.

    Attributes:
        message (str): Explanation of the error.
    """
    def __init__(self, message="An error occurred during data transformation."):
        super().__init__(message)

class DataVisualizationError(Exception):
    """
    Exception raised for errors during data visualization operations.

    Attributes:
        message (str): Explanation of the error.
    """
    def __init__(self, message="An error occurred during data visualization."):
        super().__init__(message)

class DataValidationError(Exception):
    """
    Exception raised for errors during data validation operations.

    Attributes:
        message (str): Explanation of the error.
    """
    def __init__(self, message="An error occurred during data validation."):
        super().__init__(message)

class DataLoadingError(Exception):
    """
    Exception raised for errors during data loading operations.

    Attributes:
        message (str): Explanation of the error.
    """
    def __init__(self, message="An error occurred during data loading."):
        super().__init__(message)

class DataExportError(Exception):
    """
    Exception raised for errors during data export operations.

    Attributes:
        message (str): Explanation of the error.
    """
    def __init__(self, message="An error occurred during data export."):
        super().__init__(message)

class DataIntegrationError(Exception):
    """
    Exception raised for errors during data integration processes.

    Attributes:
        message (str): Explanation of the error.
    """
    def __init__(self, message="An error occurred during data integration."):
        super().__init__(message)

class DataProcessingError(Exception):
    """
    General exception raised for errors during data processing steps.

    Attributes:
        message (str): Explanation of the error.
    """
    def __init__(self, message="An error occurred during data processing."):
        super().__init__(message)

