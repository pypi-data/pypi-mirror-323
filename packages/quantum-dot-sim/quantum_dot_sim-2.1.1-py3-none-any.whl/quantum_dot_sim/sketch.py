import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import plotly.graph_objects as go
import joblib

def draw_quantum_dot(radius, spacing=0, color='b', alpha=0.6):
    """
    Draw a 3D sketch of a spherical quantum dot.

    Parameters:
        radius (float): Radius of the quantum dot (arbitrary units).
        spacing (float): Spacing between quantum dots (default 0 for a single dot).
        color (str): Color of the quantum dot surface (default 'b' for blue).
        alpha (float): Transparency of the dot surface (default 0.6).

    Returns:
        None
    """
    phi = np.linspace(0, 2 * np.pi, 100)
    theta = np.linspace(0, np.pi, 100)
    x = radius * np.outer(np.sin(theta), np.cos(phi)) + spacing
    y = radius * np.outer(np.sin(theta), np.sin(phi)) + spacing
    z = radius * np.outer(np.cos(theta), np.ones_like(phi))

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(x, y, z, color=color, alpha=alpha, edgecolor='k')
    ax.set_title("Quantum Dot Sketch")
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_zlabel("Z-axis")
    plt.show()

def visualize_multiple_dots(radii, spacings, model, color="blues"):
    """
    Visualize multiple quantum dots in a 3D plot, incorporating ML-driven properties such as tunneling probabilities.

    Parameters:
        radii (list): List of radii for quantum dots.
        spacings (list): List of spacings between quantum dots.
        model: Trained ML model.
        color (str): Color scale of the quantum dots.

    Returns:
        None
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

# Example function call: Visualizing multiple dots with ML model
def draw_quantum_dot_array_with_ml(model):
    """
    Generate a 3D visualization of a quantum dot array with ML-driven tunneling probabilities.

    Parameters:
        model: Trained ML model for tunneling probability prediction.

    Returns:
        None
    """
    radii = np.linspace(1e-9, 5e-9, 5)  # Radii from 1 nm to 5 nm
    spacings = np.linspace(1e-9, 5e-9, 5)  # Spacing from 1 nm to 5 nm
    visualize_multiple_dots(radii, spacings, model)

if __name__ == "__main__":
    # Load the trained ML model
    model = joblib.load(r"C:\arjun-project\quantum_dot_sim\models\quantum_dot_ml_model.h5")  # Adjust path as needed
    
    # Visualize the quantum dot array
    draw_quantum_dot_array_with_ml(model)
