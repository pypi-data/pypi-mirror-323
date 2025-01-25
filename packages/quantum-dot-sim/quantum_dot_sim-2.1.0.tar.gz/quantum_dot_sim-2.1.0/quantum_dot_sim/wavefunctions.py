import numpy as np
import matplotlib.pyplot as plt

def calculate_wavefunctions(radius, n_levels=5):
    """
    Calculate normalized wavefunctions for a quantum dot.

    Parameters:
        radius (float): Radius of the quantum dot (in meters).
        n_levels (int): Number of wavefunctions to compute.

    Returns:
        list of functions: each function represents a wavefunction.
    """
    def wavefunction(n, r):
        """
        Calculate the wavefunction for a given quantum number and radius.
        
        Parameters:
            n (int): Quantum number (principal quantum number).
            r (float): Radial distance from the center of the quantum dot.

        Returns:
            float: The value of the wavefunction at radius r.
        """
        return np.sqrt(2 / radius) * np.sin(n * np.pi * r / radius)

    # Generate wavefunctions for the first n_levels
    return [lambda r, n=n: wavefunction(n, r) for n in range(1, n_levels + 1)]

def plot_wavefunctions(radius, n_levels=5):
    """
    Plot the wavefunctions for different quantum numbers in a quantum dot.

    Parameters:
        radius (float): Radius of the quantum dot (in meters).
        n_levels (int): Number of wavefunctions to plot.

    Returns:
        None
    """
    wavefunctions = calculate_wavefunctions(radius, n_levels)
    r_values = np.linspace(0, radius, 500)  # Radial distance values

    plt.figure(figsize=(8, 6))
    for n, wavefunc in enumerate(wavefunctions, start=1):
        plt.plot(r_values, wavefunc(r_values), label=f'n={n}')
    
    plt.title('Wavefunctions for Quantum Dot')
    plt.xlabel('Radial Distance (m)')
    plt.ylabel('Wavefunction Amplitude')
    plt.legend()
    plt.grid(True)
    plt.show()

def calculate_energy_levels(radius, n_levels=5, mass=9.11e-31):
    """
    Calculate the energy levels for a quantum dot based on its radius.

    Parameters:
        radius (float): Radius of the quantum dot (in meters).
        n_levels (int): Number of energy levels to calculate.
        mass (float): Electron mass (default is for electron).

    Returns:
        list: Energy levels for the quantum dot in joules.
    """
    h_bar = 1.0545718e-34  # Reduced Planck's constant (J·s)
    energies = []
    for n in range(1, n_levels + 1):
        # Formula for the energy levels in a quantum dot (particle in a box approximation)
        energy = (n**2 * np.pi**2 * h_bar**2) / (2 * mass * radius**2)
        energies.append(energy)
    return energies

def plot_energy_levels(radius, n_levels=5):
    """
    Plot the energy levels for different quantum numbers in a quantum dot.

    Parameters:
        radius (float): Radius of the quantum dot (in meters).
        n_levels (int): Number of energy levels to plot.

    Returns:
        None
    """
    energy_levels = calculate_energy_levels(radius, n_levels)
    plt.figure(figsize=(8, 6))
    plt.bar(range(1, n_levels + 1), energy_levels, color='b', alpha=0.6)
    plt.title('Energy Levels of Quantum Dot')
    plt.xlabel('Quantum Number (n)')
    plt.ylabel('Energy (J)')
    plt.grid(True)
    plt.show()

# Example usage
if __name__ == "__main__":
    radius = 1e-9  # Example quantum dot radius in meters (1 nm)
    n_levels = 5  # Number of wavefunctions and energy levels to compute

    # Plot the wavefunctions for the quantum dot
    plot_wavefunctions(radius, n_levels)

    # Plot the energy levels for the quantum dot
    plot_energy_levels(radius, n_levels)
