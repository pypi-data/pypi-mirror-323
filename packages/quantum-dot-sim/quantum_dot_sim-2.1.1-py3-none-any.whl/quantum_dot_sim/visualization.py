import matplotlib.pyplot as plt
import numpy as np
from .spectra import calculate_absorption_spectrum
from .utils import convert_energy_to_wavelength

def plot_energy_levels(energy_df):
    """
    Plots energy levels from a DataFrame.

    Parameters:
    energy_df (DataFrame): A DataFrame containing quantum numbers and their corresponding energy levels.

    Columns expected in `energy_df`:
        - "Quantum Number": The quantum number.
        - "Energy Level": The corresponding energy level.
    """
    try:
        plt.figure(figsize=(8, 6))
        plt.scatter(energy_df["Quantum Number"], energy_df["Energy Level"], color='blue', label='Energy Levels')
        plt.xlabel("Quantum Number")
        plt.ylabel("Energy Level")
        plt.title("Energy Levels vs Quantum Numbers")
        plt.legend()
        plt.grid(True)
        plt.show()
    except KeyError as e:
        print(f"Error: Missing column in DataFrame - {e}")
    except Exception as e:
        print(f"Unexpected error during plot generation: {e}")


def plot_custom_graph(x, y, xlabel="X", ylabel="Y", title="Custom Plot"):
    """
    Plot a user-defined graph.

    Parameters:
        x (array-like): X-axis data.
        y (array-like): Y-axis data.
        xlabel (str): Label for the X-axis.
        ylabel (str): Label for the Y-axis.
        title (str): Title of the graph.

    Returns:
        None
    """
    plt.figure()
    plt.plot(x, y, marker='o')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid()
    plt.show()

def plot_absorption_spectrum(energy_levels, temperature=300, model=None):
    """
    Plot the absorption spectrum for quantum dots.

    Parameters:
        energy_levels (list): List of energy levels in joules.
        temperature (float): Temperature in Kelvin.
        model: Optional machine learning model to adjust the absorption spectrum.

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

def plot_energy_levels_vs_wavelength(energy_levels):
    """
    Plot energy levels versus corresponding wavelengths for quantum dots.

    Parameters:
        energy_levels (list): List of energy levels in joules.

    Returns:
        None
    """
    wavelengths = convert_energy_to_wavelength(energy_levels)
    
    plt.figure(figsize=(8, 6))
    plt.plot(wavelengths, energy_levels, marker='o', label="Energy Levels vs Wavelength")
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Energy Level (J)')
    plt.title('Energy Levels vs Wavelength for Quantum Dots')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_interactive_spectrum(energy_levels, quantum_numbers, temperature=300, model=None):
    """
    Plot an interactive absorption spectrum and allow user to adjust parameters.

    Parameters:
        energy_levels (list): List of energy levels.
        quantum_numbers (list): Corresponding quantum numbers for the energy levels.
        temperature (float): Temperature in Kelvin.
        model: Optional machine learning model to adjust the absorption spectrum.

    Returns:
        None
    """
    result = calculate_absorption_spectrum(energy_levels, temperature, model)
    
    plt.figure(figsize=(8, 6))
    plt.plot(result['wavelengths'], result['absorption'], label="Absorption Spectrum")
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Absorption')
    plt.title('Absorption Spectrum of Quantum Dots (Interactive)')
    plt.legend()
    plt.grid(True)
    
    # Allow interactive adjustments (for demonstration purposes)
    plt.subplots_adjust(left=0.15, bottom=0.15)
    plt.show()

def plot_multiple_spectra(energy_levels_sets, labels, temperature=300, model=None):
    """
    Plot multiple absorption spectra on the same graph for comparison.

    Parameters:
        energy_levels_sets (list of lists): A list of lists, where each list contains energy levels.
        labels (list of str): A list of labels for each energy level set.
        temperature (float): Temperature in Kelvin.
        model: Optional machine learning model to adjust the absorption spectrum.

    Returns:
        None
    """
    plt.figure(figsize=(10, 7))
    
    for energy_levels, label in zip(energy_levels_sets, labels):
        result = calculate_absorption_spectrum(energy_levels, temperature, model)
        plt.plot(result['wavelengths'], result['absorption'], label=label)
    
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Absorption')
    plt.title('Multiple Absorption Spectra for Comparison')
    plt.legend()
    plt.grid(True)
    plt.show()

# Example usage
if __name__ == "__main__":
    energy_levels = np.linspace(1e-19, 5e-18, 100)  # Example energy levels in joules
    quantum_numbers = np.arange(1, len(energy_levels) + 1)  # Example quantum numbers
    
    # Plot a simple absorption spectrum
    plot_absorption_spectrum(energy_levels, temperature=300)
    
    # Plot energy levels vs wavelength
    plot_energy_levels_vs_wavelength(energy_levels)
    
    # Plot multiple spectra for comparison
    energy_levels_sets = [np.linspace(1e-19, 5e-18, 100), np.linspace(2e-19, 6e-18, 100)]
    labels = ['Set 1', 'Set 2']
    plot_multiple_spectra(energy_levels_sets, labels)
