#config.py
import os

class Config:
    """Configuration class for paths, settings, and environment variables."""
    def __init__(self):
        """
    Initialize configuration settings for the quantum dot simulation.

    This constructor sets up various configuration parameters such as file paths,
    logging settings, interactive mode, plot types, quantum simulation parameters,
    and output directories. Default values are provided, which can be overridden
    via environment variables.

    Attributes:
        dataset_path (str): Path to the dataset file used for simulation.
        model_path (str): Path to the trained model file.
        log_level (str): Logging level for the simulation.
        log_file (str): Path to the log file for storing simulation logs.
        interactive_mode (bool): Whether the simulation runs in interactive mode.
        default_plot_type (str): Default type of plot for visualization.
        default_radius (float): Default radius for quantum dot simulation in meters.
        max_wavefunction_levels (int): Maximum wavefunction levels considered.
        energy_levels_file (str): Path to the file containing energy levels data.
        wavefunctions_file (str): Path to the file containing wavefunctions data.
        output_dir (str): Directory where output files are stored.
        debug_mode (bool): Flag indicating whether debug mode is enabled.
        """

        self.dataset_path = os.getenv(
            'DATASET_PATH', 
            r"C:\arjun-project\quantum_dot_sim\data\unified_combined_physics_dataset.npy"
        )
        self.model_path = os.getenv(
            'MODEL_PATH', 
            r"C:\arjun-project\quantum_dot_sim\models\quantum_dot_ml_model.joblib"
        )
    
        self.log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.log_file = os.getenv('LOG_FILE', r"C:\arjun-project\quantum_dot_sim\output\simulation.log")
    
        self.interactive_mode = os.getenv('INTERACTIVE_MODE', 'True').lower() == 'true'
        self.default_plot_type = os.getenv('DEFAULT_PLOT_TYPE', 'line')  
    
        self.default_radius = float(os.getenv('DEFAULT_RADIUS', 1e-9))  # in meters (1 nm by default)
        self.max_wavefunction_levels = int(os.getenv('MAX_WAVEFUNCTION_LEVELS', 5))  # Default 5
        
        self.energy_levels_file = os.getenv('ENERGY_LEVELS_FILE', r"C:\arjun-project\quantum_dot_sim\data\energy_levels.npy")
        self.wavefunctions_file = os.getenv('WAVEFUNCTIONS_FILE', r"C:\arjun-project\quantum_dot_sim\data\wavefunctions.npy")
        
        # directories for output are created
        self.output_dir = os.getenv('OUTPUT_DIR', r"C:\arjun-project\quantum_dot_sim\output")
        os.makedirs(self.output_dir, exist_ok=True)

        # Debug mode flag (useful for development)
        self.debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

    def print_config(self):
        """
        Print the current configuration of the simulation.

        This method prints all the configuration values to the console.
        """
        print(f"Dataset Path: {self.dataset_path}")
        print(f"Model Path: {self.model_path}")
        print(f"Log Level: {self.log_level}")
        print(f"Log File: {self.log_file}")
        print(f"Interactive Mode: {self.interactive_mode}")
        print(f"Default Plot Type: {self.default_plot_type}")
        print(f"Default Quantum Dot Radius: {self.default_radius} meters")
        print(f"Max Wavefunction Levels: {self.max_wavefunction_levels}")
        print(f"Energy Levels File: {self.energy_levels_file}")
        print(f"Wavefunctions File: {self.wavefunctions_file}")
        print(f"Output Directory: {self.output_dir}")
        print(f"Debug Mode: {self.debug_mode}")

# Instantiate CONFIG at the end of the file
CONFIG = Config()
