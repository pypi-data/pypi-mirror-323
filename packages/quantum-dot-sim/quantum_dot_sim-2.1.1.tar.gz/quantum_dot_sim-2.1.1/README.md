#### By: Arjun Skanda Ananda - a middle schooler with a lot of free time...

# Quantum Dot Simulation Package (V2.1.1)

## Overview

The Quantum Dot Simulation Package is a Python library designed to simulate quantum dots, including their energy levels, wavefunctions, and absorption spectra, and provide 3D visualizations. This package allows users to model quantum dots in different materials and sizes and gain insights into their quantum mechanical properties, which are essential for applications in quantum computing, solar energy, and nanotechnology.

### Features
* **Energy Levels Calculation:** Simulate energy levels in quantum dots based on material properties.
* **Wavefunctions Calculation:** Calculate wavefunctions for quantum dots to analyze the behavior of electrons.
* **Absorption Spectra:** Compute absorption spectra to understand light absorption properties.
* **Visualization:** Generate 2D and 3D plots of quantum dots, energy levels, absorption spectra, an dinteraction wiht plasma.
* **Sketching:** Create 3D visual representations of quantum dots.
* **Utility Functions:** Convert energy levels and other outputs into data structures like Pandas DataFrames.
* **Plasma Interaction Simulation:** Simulate the interaction of quantum dots with plasmas, using PlasmaPy library.
* **Multi-Material Heterostructures:** Model quantum dots made from multiple materials, each with its own energy level calculation.

### Contributing
I welcome contributions! If you would like to improve the package, please do this:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Open a pull request and add a description of your changes.

### License
[Quantum Dot Simulation Package](https:/https://github.com/ArjunSkanda/quantum_dot_sim) © 2024 by Arjun Skanda Ananda is licensed under [MIT License](https://opensource.org/license/mit)

### Installation

To install the Quantum Dot Simulation package, clone the repository and install it using `pip`:
```bash
git clone https://github.com/ArjunSkanda/quantum_dot_sim.git
cd quantum_dot_sim
pip install -e .
```
Alternatively, you can use the `setup.py` file for installation 
```bash
python setup.py install
```
### Usage

Here is an example of how to use the `quantum_dot_sim` package:

```python
from quantum_dot_sim import calculate_energy_levels, plot_custom_graph

radius = 5e-9
material_props = {"effective_mass": 9.1e-31}
energy_levels = calculate_energy_levels(material_props, radius)
plot_custom_graph(range(len(energy_levels)), energy_levels, xlabel="Quantum Number", ylabel="Energy (eV)", title="Energy Levels of Quantum Dot")
```
 
You can use the functions described below to calculate quantum dot properties and visualize results.

## Modules

### CONFIG

The `quantum_dot_sim` package uses a flexible configuration system that can be customized through environment variables. All settings have sensible defaults but can be overridden to suit your specific needs.

#### Basic Configuration

All configuration options can be customized using environment variables:

**Environment Variable:** `DATASET_PATH` **Default Value:** `./data/unified_combined_physics_dataset.npy` **Description:** Path to the dataset file


**Environment Variable:** `MODEL_PATH` **Default Value:** `./models/quantum_unifiedphysics_model.h5` **Description:** Path to the trained model


**Environment Variable:** `LOG_LEVEL` **Default Value:** `INFO` **Description:** Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)


**Environment Variable:** `LOG_FILE` **Default Value:** `./output/simulation.log` **Description:** Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)


**Environment Variable:** `INTERACTIVE_MODE` **Default Value:** `True` **Description:** Enable/disable interactive visualization


**Environment Variable:** `DEFAULT_PLOT_TYPE` **Default Value:** `line` **Description:** Default visualization style


**Environment Variable:** `DEFAULT_RADIUS` **Default Value:** `1e-9` **Description:** Default quantum dot radius in meters


**Environment Variable:** `MAX_WAVEFUNCTION_LEVELS` **Default Value:** `5` **Description:** Maximum number of wavefunction levels


**Environment Variable:** `ENERGY_LEVELS_FILE` **Default Value:** `./data/energy_levels.npy` **Description:** Path to energy levels data


**Environment Variable:** `WAVEFUNCTIONS_FILE` **Default Value:** `./data/wavefunctions.npy` **Description:** Path to wavefunctions data


**Environment Variable:** `OUTPUT_DIR` **Default Value:** `./output` **Description:** Directory for output files


**Environment Variable:** `DEBUG_MODE` **Default Value:** `False` **Description:** Enable/disable debug mode

#### Usage Examples

1. Basic Usage with Defaults

```python
from quantum_dot_sim import CONFIG

# Print current configuration
CONFIG.print_config()
```

2. Customizing via Environment Variables

```bash
# Linux/Mac
export LOG_LEVEL=DEBUG
export DEFAULT_RADIUS=2e-9
export INTERACTIVE_MODE=false

# Windows
set LOG_LEVEL=DEBUG
set DEFAULT_RADIUS=2e-9
set INTERACTIVE_MODE=false
```

3. Custom Output Directory
```python
import os
os.environ['OUTPUT_DIR'] = '/path/to/custom/output'
from quantum_dot_sim import CONFIG
```

#### Important Notes

* All paths are automatically created if they don't exist
* The `OUTPUT_DIR` will be created automatically during initialization
* Log levels follow the standard Python logging hierarchy
* The quantum dot radius is specified in meters (default is 1 nm)
* Setting DEBUG_MODE=True enables additional logging and error information

#### Advanced Configuration

For more complex configurations, you can create a configuration file or subclass the `Config` class:

```python
from quantum_dot_sim import Config

class CustomConfig(Config):
    def __init__(self):
        super().__init__()
        self.custom_parameter = os.getenv('CUSTOM_PARAM', 'default_value')
```

#### Performance Considerations

* Setting `INTERACTIVE_MODE=False` can improve performance for batch processing
* Adjust `MAX_WAVEFUNCTION_LEVELS` based on your computational resources
* Use `DEBUG_MODE=True` only when necessary as it may impact performance

### data_loader

The `data_loader` module provides functionality for loading and preprocessing quantum dot simulation datasets and models. It includes robust error handling and logging capabilities to ensure reliable data operations.

#### Key Features

* Dataset loading with automatic normalization
* Model loading with error handling
* Standardized data preprocessing
* Comprehensive logging
* Custom exception handling

#### Functions

`normalize_data(X)`

Normalizes feature data using `scikit-learn`'s StandardScaler for consistent processing across different datasets.

```python
from quantum_dot_sim.data_loader import normalize_data

normalized_features = normalize_data(feature_data)
```

`load_dataset(dataset_path)`

Loads and unpacks a dataset from a NumPy file, returning normalized features and corresponding labels.

```python
from quantum_dot_sim.data_loader import load_dataset

features, labels = load_dataset("path/to/dataset.npy")
```
Dataset format must contain exactly two arrays
1. Feature data (X)
2. Label data (Y)

`load_model(model_path)`

Loads a pre-trained TensorFlow Keras model from a specified file path.

```python
from quantum_dot_sim.data_loader import load_model

model = load_model("path/to/model.h5")
```

#### Error Handling

The module implements custom exceptions for common error cases:

* `DatasetNotFoundError`: Raised when the specified dataset file doesn't exist
* `ModelNotFoundError`: Raised when the specified model file doesn't exist
* `InvalidDatasetFormatError`: Raised when the dataset structure doesn't match expected format

#### Dependencies

* `numpy`
* `tensorflow`
* `scikit-learn`
* `logging` (Python standard library)
* `os` (Python standard library)

#### Logging 

The module automatically logs important operations and errors using Python's logging module. Log messages include timestamps and severity levels, making it easier to track and debug data loading operations.

Example log output: 

```bash
2025-01-07 10:30:15 - INFO - Dataset successfully loaded from data/quantum_dots.npy
2025-01-07 10:30:15 - INFO - Normalizing the feature data.
2025-01-07 10:30:15 - INFO - Dataset successfully unpacked into features and labels.
```
### energy_levels

The `energy_levels` module is designed to calculate the energy levels of a quantum dot and determine the transition energies between successive levels. This module is part of the `quantum_dot_sim package`, which provides tools for simulating quantum dot physics and analyzing their behavior.

#### Features

**Calculate Energy Levels:**

* Uses the formula for spherical quantum dots to compute discrete energy levels.
* Parameters:
         `radius` (float): Radius of the quantum dot (in meters).
         `material_properties` (dict): Dictionary containing material-specific properties, such as the effective mass of the electron.
* Returns 
          A list of transition energies in joules.

**Usage**
```python
from energy_levels import calculate_energy_levels, calculate_transition_energies

# Example inputs
radius = 5e-9  # Quantum dot radius in meters
material_properties = {"effective_mass": 1.2e-31}  # Effective mass in kilograms

# Calculate energy levels
energy_levels = calculate_energy_levels(radius, material_properties)
print("Energy Levels (in joules):", energy_levels)

# Calculate transition energies
transition_energies = calculate_transition_energies(energy_levels)
print("Transition Energies (in joules):", transition_energies)
```

#### Logging

The module uses Python's logging library to log important information:
* INFO level logs provide details on the number of calculated energy levels and transitions.
* DEBUG level logs include detailed results for energy levels and transitions (can be enabled by configuring the logging level).

#### Dependencies 

* `numpy`: For numerial calculations
* Python 3.6 or higher (due to f-string support and enhanced logging).

#### Notes

* If the `material_properties` dictionary does not include the `effective_mass` key, the module defaults to using the electron mass (`9.1e-31` kg).
* Ensure the `radius` is in meters and the `effective_mass` is in kilograms for correct results.

### wavefunctions

The `wavefunctions` module provides functionality to compute and visualize wavefunctions and energy levels of a quantum dot. This is an essential component of the `quantum_dot_sim` package for studying quantum mechanical properties in nanoscale systems. 






















### spectra

This module allows you to compute the absorption spectra of a quantum dot.

**Function:** `calculate_absorption_spectrum(radius, material_properties)`

* `radius`: Radius of the quantum dot

* `material_properties`: A dictionary containing material properties like band gap

**Example:**
```python
absorption_spectrum = calculate_absorption_spectrum(5e-9, {"band_gap": 1.5})
```

### visualization

This module provides functions for visualizing data and plotting graphs

**Function:** `plot_custom_graph(x, y, xlabel, ylabel, title)`

* `x`: X axis data
* `y`: Y axis data
* `xlabel`: Label for X axis
* `ylabel`: Label for Y axis
* `title`: Title of graph

**Example:**
```python
plot_custom_graph(range(10), [i**2 for i in range(10)], xlabel="X", ylabel="Y", title="name-of-ur-graph")
```
### sketch

This module contains the function to draw a 3d sketch of a quantum dot.

**Function:** `draw_quantum_dot(radius)`

* `energy_levels`: A list of energy levels (in eV)

**Example:**
```python
draw_quantum_dot(5e-9)  #5 nm quantum dot
```

![quantum-dot-sketch.jpg](https://ibb.co/n1kMjBF)
### utils

This module includes utility functions, such as converting energy levels into a Pandas data frame.

**Function:** `energy_levels_to_dataframe(energy_levels)`

* `energy_levels`: A list of energy levels (in eV)

**Example:**
```python
import pandas as pd
from quantum_dot_sim.utils import energy_levels_to_dataframe

energy_levels = [1.2, 2.3, 3.4]
df = energy_levels_to_dataframe(energy_levels)
print(df)
```
### interactive_mode
This new module provides an interactive mode for continuous predictions and training on quantum dot datasets.

**Function:** start_interactive_mode()

* Starts an interactive session to load a dataset, train a model, and predict on new data with options to continue or stop after one prediction.



## Compatibility


This package is designed to work seamlessly with other scientific computing libraries, such as Numpy, SciPy, matplotlib, Pandas, and SymPy.

You can easily integrate this package with other scientific tools. This package can be a good addition to your project and work if you work with molecular dynamics simulations or other simulations that rely on physics principles.

#### Thank you for taking the time to read this!
