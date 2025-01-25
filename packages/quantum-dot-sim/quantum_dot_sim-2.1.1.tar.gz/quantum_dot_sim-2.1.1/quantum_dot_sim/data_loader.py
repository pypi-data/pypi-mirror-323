# data_loader.py
import numpy as np
import tensorflow as tf
import os
import logging
from sklearn.preprocessing import StandardScaler
from .custom_exceptions import DatasetNotFoundError, ModelNotFoundError, InvalidDatasetFormatError

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def normalize_data(X):
    """
    Normalize the feature data using a StandardScaler.

    Parameters:
        X (ndarray): The feature data to be normalized.

    Returns:
        ndarray: The normalized feature data.
    """
    logging.info("Normalizing the feature data.")
    scaler = StandardScaler()
    return scaler.fit_transform(X)

def load_dataset(dataset_path):
    """
    Load a dataset from a file and unpack it into features and labels.

    Parameters:
        dataset_path (str): Path to the dataset file.

    Returns:
        X (ndarray): The feature data.
        Y (ndarray): The label data.

    Raises:
        DatasetNotFoundError: If the dataset file is not found.
        InvalidDatasetFormatError: If the dataset format is invalid.
    """
    if not os.path.exists(dataset_path):
        raise DatasetNotFoundError(
            dataset_path,
            message="Dataset file not found. Please check the path and ensure the file exists."
        )
    
    try:
        # Assuming the dataset is a .npy file; adjust logic if a different format is used
        data = np.load(dataset_path, allow_pickle=True)
        logging.info(f"Dataset successfully loaded from {dataset_path}.")
        
        # Assuming dataset contains two parts: features (X) and labels (Y)
        if len(data) == 2:
            X, Y = data
            logging.info("Dataset successfully unpacked into features and labels.")
            X = normalize_data(X)  # Normalize the feature data
            return X, Y
        else:
            raise InvalidDatasetFormatError(
                dataset_path,
                message="Dataset must contain exactly two parts: features (X) and labels (Y)."
            )
    except Exception as e:
        logging.error(f"Failed to load dataset: {e}")
        raise

def load_model(model_path):
    """
    Load a TensorFlow Keras model from a specified file path.
    This function attempts to load a saved model from the given path and performs
    error handling for common issues such as missing files or loading failures.
    Args:
        model_path (str): The file path to the saved model.
    Returns:
        tensorflow.keras.Model: The loaded Keras model object.
    Raises:
        ModelNotFoundError: If the model file does not exist at the specified path.
        Exception: If there is an error during model loading.
    Examples:
        >>> model = load_model("path/to/model.h5")
        >>> model.summary()
    """
    
    if not os.path.exists(model_path):
        raise ModelNotFoundError(
            model_path,
            message="Model file not found. Please check the path and ensure the file exists."
        )
    
    try:
        model = tf.keras.models.load_model(model_path)
        logging.info(f"Model successfully loaded from {model_path}.")
        return model
    except Exception as e:
        logging.error(f"Failed to load model: {e}")
        raise
