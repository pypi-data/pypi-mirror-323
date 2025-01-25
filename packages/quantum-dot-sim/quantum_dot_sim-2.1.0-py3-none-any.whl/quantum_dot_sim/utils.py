import pandas as pd
import numpy as np
import joblib
from .spectra import calculate_absorption_spectrum
import matplotlib.pyplot as plt
import os

def load_data_from_file(file_path):
    """
    Load data from a file and return it.

    Parameters:
        file_path (str): Path to the file to load.

    Returns:
        object: The loaded data. This can be a numpy array if the file is a .npy file
            or a pandas DataFrame if the file is a .csv file.

    Raises:
        ValueError: If the file extension is not .npy or .csv.
    """
    file_extension = os.path.splitext(file_path)[1]
    
    if file_extension == '.npy':
        return np.load(file_path)
    elif file_extension == '.csv':
        return pd.read_csv(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

def energy_levels_to_dataframe(energy_levels, quantum_numbers):
    """
    Convert energy levels into a pandas DataFrame.

    Parameters:
        energy_levels (list): List of energy levels.
        quantum_numbers (list): List of corresponding quantum numbers.

    Returns:
        pd.DataFrame: DataFrame with energy levels and quantum numbers.
    """
    data = {"Quantum Number": quantum_numbers, "Energy Level (J)": energy_levels}
    return pd.DataFrame(data)

def save_model(model, filename):
    """
    Save a trained model to a file.

    Parameters:
        model: The trained machine learning model.
        filename (str): Path to save the model.

    Returns:
        None
    """
    joblib.dump(model, filename)

def load_model(filename):
    """
    Load a trained machine learning model from a file.

    Parameters:
        filename (str): Path to the model file.

    Returns:
        model: The loaded machine learning model.
    """
    return joblib.load(filename)

def plot_spectrum_with_ml_adjustments(energy_levels, temperature=300, model=None):
    """
    Plot the absorption spectrum for quantum dots, with optional machine learning adjustments.

    Parameters:
        energy_levels (list): List of energy levels.
        temperature (float): Temperature in Kelvin.
        model: Optional machine learning model to adjust absorption spectrum.

    Returns:
        None
    """
    result = calculate_absorption_spectrum(energy_levels, temperature, model)
    
    plt.figure(figsize=(8, 6))
    plt.plot(result['wavelengths'], result['absorption'], label="Absorption Spectrum")
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Absorption')
    plt.title('Absorption Spectrum of Quantum Dots')
    plt.legend()
    plt.grid(True)
    plt.show()

def convert_energy_to_wavelength(energy_levels):
    """
    Convert a list of energy levels to corresponding wavelengths.

    Parameters:
        energy_levels (list): List of energy levels in joules.

    Returns:
        list: Corresponding wavelengths in nanometers.
    """
    wavelengths = 1e9 * 6.626e-34 * 3e8 / np.array(energy_levels)  # Convert energy to wavelength (nm)
    return wavelengths

def save_spectrum_to_csv(energy_levels, quantum_numbers, temperature=300, model=None, filename="spectrum.csv"):
    """
    Save the absorption spectrum to a CSV file, including energy levels and quantum numbers.

    Parameters:
        energy_levels (list): List of energy levels.
        quantum_numbers (list): List of quantum numbers.
        temperature (float): Temperature in Kelvin.
        model: Optional machine learning model to adjust the absorption spectrum.
        filename (str): Path to save the CSV file.

    Returns:
        None
    """
    # Convert energy levels to wavelengths
    wavelengths = convert_energy_to_wavelength(energy_levels)
    
    # Calculate absorption spectrum
    result = calculate_absorption_spectrum(energy_levels, temperature, model)
    
    # Prepare the data to be saved
    data = {
        "Quantum Number": quantum_numbers,
        "Energy Level (J)": energy_levels,
        "Wavelength (nm)": wavelengths,
        "Absorption": result['absorption']
    }
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Spectrum saved to {filename}")

# Example usage of the new utility function
if __name__ == "__main__":
    energy_levels = np.linspace(1e-19, 5e-18, 100)  # Example energy levels in joules
    quantum_numbers = np.arange(1, len(energy_levels) + 1)  # Example quantum numbers
    
    # Save the energy levels to CSV with model adjustments
    model = load_model("quantum_unifiedphysics_model.h5")  # Example model path
    save_spectrum_to_csv(energy_levels, quantum_numbers, temperature=300, model=model, filename="spectrum.csv")
