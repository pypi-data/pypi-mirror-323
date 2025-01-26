import os
import pandas as pd
import numpy as np
import pkg_resources


class DriftMeasurement:
    def __init__(self, value, uncertainty):
        """
        Represents a drift measurement with value and uncertainty.
        
        :param value: Mean drift value
        :param uncertainty: Uncertainty of the measurement
        """
        self.value = float(value)
        self.uncertainty = float(uncertainty)
    
    def __repr__(self):
        """String representation of the drift measurement"""
        return f"{self.value} ± {self.uncertainty}"
    
    def __str__(self):
        """Human-readable string representation"""
        return self.__repr__()

class AnalogNASBench:
    def __init__(self):
        """
        Initialize the NASBench Analog dataset.
        
        :param csv_path: Path to the CSV file containing benchmark data
        """
        csv_path = pkg_resources.resource_filename('analognasbench', 'benchmark_data.csv')
        self.data = pd.read_csv(csv_path)
        drift_columns = [
            'baseline_drift_60', 'baseline_drift_3600', 
            'baseline_drift_86400', 'baseline_drift_2592000', 
            'finetuned_drift_60', 'finetuned_drift_3600', 
            'finetuned_drift_86400', 'finetuned_drift_2592000'
        ]
        # Convert drift columns to DriftMeasurement objects
        for col in drift_columns:
            self.data[col] = self.data[col].apply(self._parse_drift)
        
        # List of all metrics for querying
        self.metrics = [
            'architecture', 'baseline_accuracy', 'ptq_accuracy', 
            'qat_accuracy', 'analog_accuracy', 'finetuned_accuracy'
        ] + drift_columns
        
    def _parse_drift(self, drift_str):
        """
        Parse drift string into DriftMeasurement object
        
        :param drift_str: String in format "value ± uncertainty"
        :return: DriftMeasurement object
        """
        # If it's already a float, return as is
        if isinstance(drift_str, (int, float)):
            return DriftMeasurement(drift_str, 0)
        
        # If it's a string representation of a number
        if isinstance(drift_str, str):
            drift_str = drift_str.strip()
            
            # Direct float conversion
            try:
                return DriftMeasurement(float(drift_str), 0)
            except ValueError:
                pass
            
            # Check for ± notation
            if '±' in drift_str:
                try:
                    # Split and convert
                    parts = drift_str.split('±')
                    value = float(parts[0].strip())
                    uncertainty = float(parts[1].strip())
                    return DriftMeasurement(value, uncertainty)
                except:
                    print(f"Warning: Could not parse drift string: {drift_str}")
                    return DriftMeasurement(0, 0)
        
        # Fallback
        return DriftMeasurement(0, 0)


    def query_metric(self, architecture, metric):
        """
        Query a specific metric for a given architecture ID.
        
        :param architecture: Architecture identifier
        :param metric: Metric to retrieve
        :return: Metric value or None if not found
        """
        if metric not in self.metrics:
            raise ValueError(f"Metric {metric} not found. Available metrics: {self.metrics}")
        
        result = self.data[self.data['architecture'] == str(architecture)]
        if result.empty:
            return None
        
        return result[metric].values[0]
    
    def get_architecture_details(self, architecture):
        """
        Retrieve full details for a specific architecture.
        
        :param architecture: Architecture identifier
        :return: Dictionary of architecture details
        """
        result = self.data[self.data['architecture'] == str(architecture)]
        if result.empty:
            return None
        
        return result.to_dict('records')[0]
    
    def list_available_architectures(self):
        """
        List all available architectures.
        
        :return: List of architectures
        """
        return self.data['architecture'].tolist()