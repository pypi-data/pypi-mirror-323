# __init__.py
# Import configuration
from .config import CONFIG

# Import custom exceptions
from .custom_exceptions import (
    DatasetNotFoundError,
    ModelNotFoundError,
    InvalidDatasetFormatError,
    QuantumDotError,
    InvalidRadiusError,
    InvalidEnergyLevelError,
    DataNotFoundError,
    InvalidWavefunctionError,
    ConfigError,
    InvalidUserInputError
)
from .data_loader import (
    load_dataset,
    normalize_data,
    load_model as load_model_data 
)

from .energy_levels import (
    calculate_energy_levels,
    calculate_transition_energies
)

from .interactive_mode import interactive_mode

from .sketch import (
    draw_quantum_dot,
    draw_quantum_dot_array_with_ml,
    visualize_multiple_dots
)

from .spectra import (
    calculate_absorption_spectrum,
    plot_absorption_spectrum
)

from .utils import (
    energy_levels_to_dataframe,
    save_model,
    load_model as load_model_utils, 
    save_spectrum_to_csv
)

from .visualization import (
    plot_energy_levels,
    plot_absorption_spectrum as plot_absorption_spectrum_vis
)

from .wavefunctions import (
    calculate_wavefunctions,
    plot_wavefunctions
)

from .quantum_simulation import Material, Light, Particle, QuantumDot, run_simulation

from .ml_energy_levels import MLEnergyLevelPredictor



# Package metadata
__version__ = "2.1.1"
__author__ = "Arjun Skanda Ananda"
__description__ = (
    "The Quantum Dot Simulation Package is a Python library designed to "
    "simulate quantum dots, including their energy levels, wavefunctions, and "
    "absorption spectra, and provide 3D visualizations. This package allows users "
    "to model quantum dots in different materials and sizes and gain insights "
    "into their quantum mechanical properties, which are essential for applications "
    "in quantum computing, solar energy, and nanotechnology."
)
load_model = load_model_data

# Explicitly define the public API of the package
__all__ = [
    # Configuration
    "CONFIG",
    
    # Simulations
    "run_simulation",
    "Material",
    "Light",
    "Particle",
    "QuantumDot",
    
    # Core data functions
    "load_dataset",
    "normalize_data",
    "load_model",
    
    # Physics calculations
    "calculate_energy_levels",
    "calculate_transition_energies",
    "calculate_wavefunctions",
    "MLEnergyLevelPredictor",
    
    # Visualization and plotting
    "draw_quantum_dot",
    "draw_quantum_dot_array_with_ml",
    "visualize_multiple_dots",
    "plot_wavefunctions",
    "plot_energy_levels",
    "plot_absorption_spectrum",
    
    # Spectra analysis
    "calculate_absorption_spectrum",
    
    # Interactive features
    "interactive_mode",
    
    # Simulations 
    "ElectronSimulation",
    "QuantumSimulation",
    
    # Utility functions
    "energy_levels_to_dataframe",
    "save_model",
    "save_spectrum_to_csv",
    
    # Custom exceptions
    "DatasetNotFoundError",
    "ModelNotFoundError",
    "InvalidDatasetFormatError"
    "QuantumDotError",
    "InvalidRadiusError",
    "InvalidEnergyLevelError",
    "DataNotFoundError",
    "InvalidWavefunctionError",
    "ConfigError",
    "InvalidUserInputError",
]