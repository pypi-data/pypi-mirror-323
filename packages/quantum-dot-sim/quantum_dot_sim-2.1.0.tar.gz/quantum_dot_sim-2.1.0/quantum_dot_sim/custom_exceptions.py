class QuantumDotError(Exception):
    """Base class for all exceptions related to quantum dot simulations."""
    def __init__(self, message="An error occurred in the Quantum Dot simulation."):
        self.message = message
        super().__init__(self.message)

class InvalidRadiusError(QuantumDotError):
    """Exception raised for invalid radius values."""
    def __init__(self, radius, message="Invalid radius for quantum dot."):
        self.radius = radius
        self.message = f"{message} Given radius: {radius}"
        super().__init__(self.message)

class InvalidEnergyLevelError(QuantumDotError):
    """Exception raised for invalid energy levels."""
    def __init__(self, energy_level, message="Invalid energy level provided."):
        self.energy_level = energy_level
        self.message = f"{message} Given energy level: {energy_level}"
        super().__init__(self.message)

class DataNotFoundError(QuantumDotError):
    """Exception raised when data is not found."""
    def __init__(self, file_path, message="Data file not found."):
        self.file_path = file_path
        self.message = f"{message} File path: {file_path}"
        super().__init__(self.message)

class ModelNotFoundError(QuantumDotError):
    """Exception raised when the model file is not found."""
    def __init__(self, model_path, message="Model file not found."):
        self.model_path = model_path
        self.message = f"{message} Model path: {model_path}"
        super().__init__(self.message)

class InvalidWavefunctionError(QuantumDotError):
    """Exception raised for invalid wavefunction calculations."""
    def __init__(self, wavefunction, message="Invalid wavefunction calculation."):
        self.wavefunction = wavefunction
        self.message = f"{message} Given wavefunction: {wavefunction}"
        super().__init__(self.message)

class ConfigError(QuantumDotError):
    """Exception raised for configuration issues."""
    def __init__(self, config_name, message="Configuration error."):
        self.config_name = config_name
        self.message = f"{message} Config name: {config_name}"
        super().__init__(self.message)

class InvalidDatasetFormatError(QuantumDotError):
    """Exception raised when the dataset format is invalid."""
    def __init__(self, file_path, message="Dataset format is invalid."):
        self.file_path = file_path
        self.message = f"{message} File path: {file_path}"
        super().__init__(self.message)

class DatasetNotFoundError(QuantumDotError):
    """Exception raised when the dataset file is not found."""
    def __init__(self, file_path, message="Dataset file not found."):
        self.file_path = file_path
        self.message = f"{message} File path: {file_path}"
        super().__init__(self.message)

class InvalidUserInputError(QuantumDotError):
    """Exception raised for invalid user input."""
    def __init__(self, input_value, message="Invalid input provided by the user."):
        self.input_value = input_value
        self.message = f"{message} Given input: {input_value}"
        super().__init__(self.message)
