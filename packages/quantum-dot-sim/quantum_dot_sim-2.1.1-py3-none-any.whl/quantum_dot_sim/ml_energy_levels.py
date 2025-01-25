# ml_energy_levels.py
import numpy as np
import joblib
import logging
from sklearn.ensemble import RandomForestRegressor
from .energy_levels import calculate_energy_levels

class MLEnergyLevelPredictor:
    """ML-enhanced energy level predictor for quantum dots."""
    
    def __init__(self, model_path=r'C:\arjun-project\quantum_dot_sim\models\quantum_dot_ml_model.joblib'):
        """
        Initialize the predictor with a trained model.
        
        Parameters:
            model_path (str): Path to the saved model file
        """
        try:
            model_data = joblib.load(model_path)
            self.model = model_data['model']
            self.scaler_X = model_data['scaler_X']
            self.scaler_y = model_data['scaler_y']
            self.feature_names = model_data['feature_names']
            logging.info("ML model loaded successfully")
        except FileNotFoundError:
            logging.warning("ML model not found. Falling back to analytical calculations only.")
            self.model = None
    
    def predict_energy_levels(self, radius, material_properties, temperature=300, use_ml=True):
        """
        Calculate energy levels using ML model with fallback to analytical calculation.
        
        Parameters:
            radius (float): Quantum dot radius in meters
            material_properties (dict): Material properties
            temperature (float): Temperature in Kelvin
            use_ml (bool): Whether to use ML prediction (if available)
            
        Returns:
            numpy.ndarray: Predicted energy levels
        """
        # First get analytical calculation
        analytical_levels = calculate_energy_levels(radius, material_properties)
        
        if not use_ml or self.model is None:
            return analytical_levels
        
        try:
            # Prepare features for ML prediction
            effective_mass = material_properties.get('effective_mass', 9.1e-31)
            features = np.array([[radius, effective_mass, temperature]])
            features_scaled = self.scaler_X.transform(features)
            
            # Make ML prediction
            predictions_scaled = self.model.predict(features_scaled)
            ml_levels = self.scaler_y.inverse_transform(predictions_scaled)[0]
            
            # Combine ML and analytical predictions (weighted average)
            combined_levels = 0.7 * ml_levels + 0.3 * analytical_levels
            
            logging.info("Successfully predicted energy levels using ML model")
            return combined_levels
            
        except Exception as e:
            logging.error(f"ML prediction failed: {str(e)}. Using analytical calculation.")
            return analytical_levels
    
    def get_prediction_uncertainty(self, radius, material_properties, temperature=300):
        """
        Estimate uncertainty in the ML predictions using ensemble variance.
        
        Returns:
            numpy.ndarray: Estimated uncertainty for each energy level
        """
        if not isinstance(self.model, RandomForestRegressor):
            return None
            
        effective_mass = material_properties.get('effective_mass', 9.1e-31)
        features = np.array([[radius, effective_mass, temperature]])
        features_scaled = self.scaler_X.transform(features)
        
        # Get predictions from all trees in the forest
        predictions = np.array([tree.predict(features_scaled) 
                              for tree in self.model.estimators_])
        
        # Calculate standard deviation across predictions
        uncertainty = np.std(predictions, axis=0)
        return self.scaler_y.inverse_transform(uncertainty.reshape(1, -1))[0]