import numpy as np
import logging
import matplotlib.pyplot as plt
from .custom_exceptions import InvalidUserInputError

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class InteractiveModeManager:
    def __init__(self, model, dataset=None):
        self.model = model
        self.dataset = dataset
        self.prediction_cache = {}
        self.figure = None

    def validate_model(self):
        """Validate model input and output"""
        if self.model is None:
            raise ValueError("Model is not loaded properly")
        try:
            # Simple test input
            test_input = np.array([[1.0]])
            result = self.model(test_input)
            
            # Validate result is a numpy array
            if not isinstance(result, np.ndarray):
                result = np.array(result)
            if result.ndim == 1:
                result = result.reshape(1, -1)
            
            return True
        except Exception as e:
            logging.error(f"Model validation failed: {e}")
            return False

    def plot_prediction(self, prediction, input_data, radius=None):
        """Plot prediction results"""
        try:
            plt.close('all')
            fig = plt.figure(figsize=(10, 6))
            
            # Ensure prediction is numpy array
            prediction = np.atleast_2d(prediction)
            energy_levels = prediction[0]
            
            x_positions = np.arange(len(energy_levels))
            plt.bar(x_positions, energy_levels, color='blue', alpha=0.7)
            
            plt.xlabel('Energy Level Index')
            plt.ylabel('Energy (eV)')
            title = 'Predicted Energy Levels'
            if radius is not None:
                title += f'\nRadius: {radius:.2e} m'
            plt.title(title)
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            logging.error(f"Error plotting prediction: {e}")
            raise

    def get_user_input(self, prompt):
        while True:
            try:
                user_input = input(prompt).strip().lower()
                if user_input in ['stop', 'continue']:
                    return user_input
                elif user_input == '':
                    raise InvalidUserInputError("Empty input is not allowed")
                else:
                    try:
                        value = float(user_input)
                        if "radius" in prompt.lower():
                            if not (1e-10 <= value <= 1e-7):
                                raise InvalidUserInputError(
                                    "Please enter a radius between 1e-10 and 1e-7 meters (0.1 to 100 nm)"
                                )
                        return value
                    except ValueError:
                        raise InvalidUserInputError(
                            "Please enter a valid number or 'stop'/'continue'"
                        )
            except InvalidUserInputError as e:
                logging.warning(f"Invalid input: {e}")
                continue

    def run(self):
        logging.info("Starting interactive mode session")
        
        if not self.validate_model():
            logging.error("Model validation failed. Exiting interactive mode.")
            return
        
        while True:
            try:
                if self.dataset is not None:
                    # Dataset mode
                    sample_index = np.random.randint(0, len(self.dataset))
                    input_data = self.dataset[sample_index:sample_index + 1]
                    
                    if sample_index in self.prediction_cache:
                        prediction = self.prediction_cache[sample_index]
                        logging.info(f"Using cached prediction for sample {sample_index}")
                    else:
                        prediction = self.model(input_data)
                        prediction = np.atleast_2d(prediction)
                        self.prediction_cache[sample_index] = prediction
                        logging.info(f"New prediction for sample {sample_index}")
                    
                    self.plot_prediction(prediction, input_data)
                    
                else:
                    # Manual input mode
                    radius = self.get_user_input(
                        "Enter quantum dot radius in meters (or 'stop' to exit): "
                    )
                    if isinstance(radius, str):
                        break
                    
                    input_data = np.array([[radius]])
                    prediction = self.model(input_data)
                    prediction = np.atleast_2d(prediction)
                    self.plot_prediction(prediction, input_data, radius)
                    logging.info(f"Generated prediction for radius {radius:.2e} m")
                
                continue_response = self.get_user_input(
                    "Enter 'continue' for another prediction or 'stop' to exit: "
                )
                if continue_response == 'stop':
                    break
                
            except Exception as e:
                logging.error(f"Error in interactive mode: {e}")
                user_response = input("Enter 'continue' to retry or 'stop' to exit: ").strip().lower()
                if user_response != 'continue':
                    break

        logging.info("Interactive mode session ended")
        plt.close('all')

def interactive_mode(model, X=None):
    """
    Entry point function for interactive mode.
    
    Parameters:
        model: The trained quantum dot prediction model or callable
        X (optional): Dataset for random sampling mode
    """
    manager = InteractiveModeManager(model, X)
    manager.run()