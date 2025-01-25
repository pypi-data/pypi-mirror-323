import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def calculate_energy_levels(radius, material_properties):
    """
    Calculate energy levels of a quantum dot using the formula for spherical quantum dots.

    Parameters:
        radius (float): Radius of the quantum dot in meters.
        material_properties (dict): Material properties, should contain the effective mass of the electron.

    Returns:
        list: List of energy levels in joules.
    """
    # Check if material properties are provided
    if "effective_mass" not in material_properties:
        logging.warning("Effective mass not found in material properties, using default value for electron mass.")
        effective_mass = 9.1e-31  # Default to electron mass if not provided
    else:
        effective_mass = material_properties["effective_mass"]

    h_bar = 1.0545718e-34  # Reduced Planck's constant
    n_levels = 5  # Number of energy levels to calculate

    # Calculate energy levels using the formula for spherical quantum dots
    energy_levels = [
        (n ** 2 * np.pi ** 2 * h_bar ** 2) / (2 * effective_mass * radius ** 2)
        for n in range(1, n_levels + 1)
    ]
    
    # Log the results for the calculation
    logging.info(f"Calculated {n_levels} energy levels for a quantum dot with radius {radius} meters.")
    logging.debug(f"Energy levels: {energy_levels}")

    return energy_levels

def calculate_transition_energies(energy_levels):
    """
    Calculate transition energies between successive energy levels.

    Parameters:
        energy_levels (list): List of energy levels (in joules).

    Returns:
        list: Transition energies (in joules).
    """
    transition_energies = []
    for i in range(1, len(energy_levels)):
        transition_energy = energy_levels[i] - energy_levels[i - 1]
        transition_energies.append(abs(transition_energy))  # Ensure positive transition energies

    logging.info(f"Calculated {len(transition_energies)} transition energies.")
    logging.debug(f"Transition energies: {transition_energies}")

    return transition_energies
