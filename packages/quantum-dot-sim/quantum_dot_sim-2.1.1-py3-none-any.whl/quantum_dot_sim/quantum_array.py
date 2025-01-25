import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from .utils import load_data_from_file
from .custom_exceptions import InvalidDatasetFormatError

# Function: Calculate Coulomb Interaction
def calculate_coulomb_interaction(radius, spacing):
    """
    Calculate Coulomb interaction energy between two quantum dots.

    Parameters:
        radius (float): Radius of the quantum dot in meters.
        spacing (float): Distance between quantum dots in meters.

    Returns:
        float: Coulomb interaction energy in Joules.
    """
    epsilon_0 = 8.85e-12  # Permittivity of free space
    charge = 1.6e-19  # Elementary charge (Coulomb)
    energy = (charge ** 2) / (4 * np.pi * epsilon_0 * spacing)
    return energy

# Function: Load and Combine Multiple Datasets (CSV and .npy)
def load_and_combine_datasets(csv_files, npy_file):
    """
    Load and combine datasets from CSV and NPY files.

    Parameters:
        csv_files (list): List of CSV file paths.
        npy_file (str): Path to the NPY file.

    Returns:
        pd.DataFrame: Combined dataset.
    """
    combined_data = pd.DataFrame()
    
    # Load and combine CSV files
    for csv_file in csv_files:
        try:
            data = pd.read_csv(csv_file)
            combined_data = pd.concat([combined_data, data], ignore_index=True)
        except Exception as e:
            print(f"Error loading CSV file {csv_file}: {e}")
    
    # Load NPY file and combine it with the DataFrame
    try:
        npy_data = np.load(npy_file)
        npy_df = pd.DataFrame(npy_data)
        combined_data = pd.concat([combined_data, npy_df], ignore_index=True)
    except Exception as e:
        print(f"Error loading NPY file {npy_file}: {e}")

    # Ensure no NaN values are present
    combined_data = combined_data.dropna()
    
    return combined_data

# Function: Train Real ML Model
def train_real_ml_model(csv_files, npy_file):
    """
    Train an ML model on real quantum dot data from multiple datasets.

    Parameters:
        csv_files (list): List of CSV file paths.
        npy_file (str): Path to the NPY file.

    Returns:
        model: Trained ML model.
    """
    # Load and combine datasets
    try:
        data = load_and_combine_datasets(csv_files, npy_file)
    except InvalidDatasetFormatError as e:
        print(f"Error loading data: {e}")
        return None
    
    # Assuming 'radius', 'spacing', 'material_property' are columns in the data
    # Adjust based on actual dataset structure
    X = data[['radius', 'spacing', 'material_property']].values
    y = data['tunneling_probability'].values

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train a model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    print(f"Model R^2 score: {model.score(X_test, y_test):.3f}")
    return model

# Function: Visualize Quantum Dot Array
def visualize_quantum_dot_array(radii, spacings, model, color="blues"):
    """
    Visualize an array of quantum dots and their properties.

    Parameters:
        radii (list): List of radii for quantum dots.
        spacings (list): List of spacings between quantum dots.
        model: Trained ML model.
        color (str): Color scale of the quantum dots.
    """
    fig = go.Figure()
    for i, radius in enumerate(radii):
        for j, spacing in enumerate(spacings):
            phi = np.linspace(0, 2 * np.pi, 50)
            theta = np.linspace(0, np.pi, 50)
            x = radius * np.outer(np.sin(theta), np.cos(phi)) + i * spacing
            y = radius * np.outer(np.sin(theta), np.sin(phi)) + j * spacing
            z = radius * np.outer(np.cos(theta), np.ones_like(phi))
            tunneling_prob = model.predict([[radius, spacing, 1.0]])[0]  # Assume 1.0 for a placeholder material property
            fig.add_trace(go.Surface(
                z=z, x=x, y=y, colorscale=color, showscale=False,
                opacity=min(1.0, tunneling_prob)  # Use tunneling prob for transparency
            ))
    
    fig.update_layout(
        title="Quantum Dot Array with ML-Driven Properties",
        scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z"),
    )
    fig.show()

# Function: Plot Interaction Heatmap
def plot_interaction_heatmap(radii, spacings, model):
    """
    Plot a heatmap of interaction energies and tunneling probabilities.

    Parameters:
        radii (list): List of radii values.
        spacings (list): List of spacing values.
        model: Trained ML model.
    """
    R, S = np.meshgrid(radii, spacings)
    energies = np.zeros_like(R)
    tunneling = np.zeros_like(R)

    for i in range(R.shape[0]):
        for j in range(R.shape[1]):
            radius = R[i, j]
            spacing = S[i, j]
            energies[i, j] = calculate_coulomb_interaction(radius, spacing)
            tunneling[i, j] = model.predict([[radius, spacing, 1.0]])[0]

    # Plot interaction heatmap
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    im1 = axes[0].imshow(energies, extent=[radii.min(), radii.max(), spacings.min(), spacings.max()],
                          origin='lower', aspect='auto', cmap='hot')
    axes[0].set_title('Coulomb Interaction Energy (J)')
    axes[0].set_xlabel('Radius (m)')
    axes[0].set_ylabel('Spacing (m)')
    fig.colorbar(im1, ax=axes[0])

    im2 = axes[1].imshow(tunneling, extent=[radii.min(), radii.max(), spacings.min(), spacings.max()],
                          origin='lower', aspect='auto', cmap='cool')
    axes[1].set_title('Tunneling Probability')
    axes[1].set_xlabel('Radius (m)')
    axes[1].set_ylabel('Spacing (m)')
    fig.colorbar(im2, ax=axes[1])

    plt.tight_layout()
    plt.show()

# Function: Save Results
def save_results_to_csv(radii, spacings, energies, tunneling, filename):
    """
    Save simulation results to a CSV file.

    Parameters:
        radii (array): Radii values.
        spacings (array): Spacing values.
        energies (array): Coulomb interaction energies.
        tunneling (array): Tunneling probabilities.
        filename (str): Output filename.
    """
    data = {
        'Radius (m)': radii.flatten(),
        'Spacing (m)': spacings.flatten(),
        'Coulomb Energy (J)': energies.flatten(),
        'Tunneling Probability': tunneling.flatten()
    }
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Results saved to {filename}")

# Main Script
if __name__ == "__main__":
    # Step 1: Define your CSV and NPY files
    csv_files = ["dataset1.csv", "dataset2.csv"]  # Replace with actual paths
    npy_file = "dataset.npy"  # Replace with actual NPY file path

    # Step 2: Train the ML model
    model = train_real_ml_model(csv_files, npy_file)

    if model is None:
        print("Failed to train model. Exiting.")
        exit()

    # Step 3: Define parameters
    radii = np.linspace(1e-9, 5e-9, 10)  # Radii from 1 nm to 5 nm
    spacings = np.linspace(1e-9, 5e-9, 10)  # Spacing from 1 nm to 5 nm

    # Step 4: Visualize quantum dot array
    visualize_quantum_dot_array(radii, spacings, model)

    # Step 5: Generate and plot heatmaps
    plot_interaction_heatmap(radii, spacings, model)

    # Step 6: Save results to CSV
    R, S = np.meshgrid(radii, spacings)
    energies = np.array([[calculate_coulomb_interaction(r, s) for r in radii] for s in spacings])
    tunneling = np.array([[model.predict([[r, s, 1.0]])[0] for r in radii] for s in spacings])
    save_results_to_csv(R, S, energies, tunneling, "quantum_dot_simulation_results.csv")
