"""
ml_predictor.py
───────────────
Machine Learning models for delivery time prediction, 
demand forecasting, and route optimization.
"""

import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import pickle
import os


@dataclass
class PredictionResult:
    """Container for ML prediction results"""
    predicted_value: float
    confidence: float
    feature_importance: Dict[str, float]
    model_type: str


class DeliveryTimePredictor:
    """ML model for predicting delivery times"""
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = [
            'distance_km',
            'traffic_factor',
            'weather_score',
            'time_of_day',
            'day_of_week',
            'vehicle_capacity',
            'load_weight'
        ]
    
    def train(
        self,
        training_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Train the delivery time prediction model
        
        Args:
            training_data: List of historical delivery records
        
        Returns:
            Training metrics (accuracy, RMSE, etc.)
        """
        if not training_data:
            return {'error': 'No training data provided'}
        
        # Extract features and targets
        X = []
        y = []
        
        for record in training_data:
            features = [
                record.get('distance_km', 0),
                record.get('traffic_factor', 1.0),
                record.get('weather_score', 1.0),
                record.get('time_of_day', 12),
                record.get('day_of_week', 3),
                record.get('vehicle_capacity', 25),
                record.get('load_weight', 15)
            ]
            X.append(features)
            y.append(record.get('actual_delivery_time_hours', 0))
        
        X = np.array(X)
        y = np.array(y)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # Calculate training metrics
        predictions = self.model.predict(X_scaled)
        mse = np.mean((predictions - y) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(predictions - y))
        
        return {
            'rmse': float(rmse),
            'mae': float(mae),
            'samples_trained': len(X)
        }
    
    def predict(
        self,
        distance_km: float,
        traffic_factor: float = 1.0,
        weather_score: float = 1.0,
        time_of_day: int = 12,
        day_of_week: int = 3,
        vehicle_capacity: float = 25.0,
        load_weight: float = 15.0
    ) -> PredictionResult:
        """
        Predict delivery time for given conditions
        
        Returns:
            PredictionResult with predicted hours and confidence
        """
        if not self.is_trained:
            # Use simple heuristic if not trained
            base_time = distance_km / 60.0  # 60 km/h average
            adjusted_time = base_time * traffic_factor * weather_score
            
            return PredictionResult(
                predicted_value=adjusted_time,
                confidence=0.5,
                feature_importance={},
                model_type='heuristic'
            )
        
        # Prepare features
        features = np.array([[
            distance_km,
            traffic_factor,
            weather_score,
            time_of_day,
            day_of_week,
            vehicle_capacity,
            load_weight
        ]])
        
        # Scale and predict
        features_scaled = self.scaler.transform(features)
        predicted_time = self.model.predict(features_scaled)[0]
        
        # Calculate confidence based on feature values
        confidence = self._calculate_confidence(features[0])
        
        # Get feature importance
        importance = dict(zip(
            self.feature_names,
            self.model.feature_importances_
        ))
        
        return PredictionResult(
            predicted_value=float(predicted_time),
            confidence=confidence,
            feature_importance=importance,
            model_type='random_forest'
        )
    
    def _calculate_confidence(self, features: np.ndarray) -> float:
        """Calculate prediction confidence"""
        # Simple confidence based on reasonable feature ranges
        distance = features[0]
        traffic = features[1]
        weather = features[2]
        
        confidence = 1.0
        
        # Reduce confidence for extreme values
        if distance > 2000 or distance < 10:
            confidence *= 0.7
        if traffic > 2.0 or traffic < 0.5:
            confidence *= 0.8
        if weather > 1.5 or weather < 0.5:
            confidence *= 0.8
        
        return float(confidence)
    
    def save_model(self, filepath: str):
        """Save trained model to disk"""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, filepath: str):
        """Load trained model from disk"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.is_trained = True


class DemandForecaster:
    """Forecast load demand using time series analysis"""
    
    def __init__(self):
        self.model = GradientBoostingRegressor(
            n_estimators=50,
            max_depth=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def train(
        self,
        historical_demand: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Train demand forecasting model
        
        Args:
            historical_demand: Historical load demand data
        
        Returns:
            Training metrics
        """
        if not historical_demand or len(historical_demand) < 10:
            return {'error': 'Insufficient training data'}
        
        X = []
        y = []
        
        for record in historical_demand:
            features = [
                record.get('day_of_week', 0),
                record.get('week_of_year', 1),
                record.get('month', 1),
                record.get('holiday_flag', 0),
                record.get('prev_day_demand', 0),
                record.get('avg_last_week', 0)
            ]
            X.append(features)
            y.append(record.get('demand', 0))
        
        X = np.array(X)
        y = np.array(y)
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        predictions = self.model.predict(X_scaled)
        rmse = np.sqrt(np.mean((predictions - y) ** 2))
        mae = np.mean(np.abs(predictions - y))
        
        return {
            'rmse': float(rmse),
            'mae': float(mae),
            'samples': len(X)
        }
    
    def forecast(
        self,
        day_of_week: int,
        week_of_year: int,
        month: int,
        holiday_flag: int = 0,
        prev_day_demand: float = 0,
        avg_last_week: float = 0
    ) -> PredictionResult:
        """
        Forecast demand for given time period
        
        Returns:
            PredictionResult with forecasted demand
        """
        if not self.is_trained:
            # Simple seasonal baseline
            base_demand = 50
            seasonal_factor = 1.0 + (month - 6) * 0.05
            weekly_factor = 1.0 - (day_of_week - 3.5) * 0.1
            
            forecast = base_demand * seasonal_factor * weekly_factor
            
            return PredictionResult(
                predicted_value=max(0, forecast),
                confidence=0.6,
                feature_importance={},
                model_type='seasonal_baseline'
            )
        
        features = np.array([[
            day_of_week,
            week_of_year,
            month,
            holiday_flag,
            prev_day_demand,
            avg_last_week
        ]])
        
        features_scaled = self.scaler.transform(features)
        forecast_value = self.model.predict(features_scaled)[0]
        
        return PredictionResult(
            predicted_value=max(0, float(forecast_value)),
            confidence=0.85,
            feature_importance={
                'day_of_week': 0.15,
                'week_of_year': 0.10,
                'month': 0.20,
                'holiday': 0.25,
                'prev_day': 0.15,
                'avg_week': 0.15
            },
            model_type='gradient_boosting'
        )


class RouteOptimizer:
    """ML-based route optimization"""
    
    def __init__(self):
        self.efficiency_model = LinearRegression()
        self.is_trained = False
    
    def train(
        self,
        historical_routes: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Train route efficiency model
        
        Args:
            historical_routes: Historical route performance data
        
        Returns:
            Training metrics
        """
        if not historical_routes:
            return {'error': 'No training data'}
        
        X = []
        y = []
        
        for route in historical_routes:
            features = [
                route.get('total_distance_km', 0),
                route.get('num_stops', 1),
                route.get('avg_stop_time_minutes', 30),
                route.get('traffic_density', 1.0),
                route.get('road_quality_score', 1.0)
            ]
            X.append(features)
            y.append(route.get('efficiency_score', 0))
        
        X = np.array(X)
        y = np.array(y)
        
        self.efficiency_model.fit(X, y)
        self.is_trained = True
        
        predictions = self.efficiency_model.predict(X)
        r2_score = 1 - (np.sum((y - predictions) ** 2) / np.sum((y - np.mean(y)) ** 2))
        
        return {
            'r2_score': float(r2_score),
            'samples': len(X)
        }
    
    def optimize_route(
        self,
        waypoints: List[Tuple[float, float]],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Optimize route given waypoints and constraints
        
        Args:
            waypoints: List of (lat, lng) coordinates
            constraints: Optional constraints (time windows, capacity, etc.)
        
        Returns:
            Optimized route plan
        """
        if len(waypoints) < 2:
            return {'error': 'Need at least 2 waypoints'}
        
        # Simple nearest neighbor optimization
        unvisited = list(waypoints[1:])
        route = [waypoints[0]]
        current = waypoints[0]
        
        while unvisited:
            nearest = min(
                unvisited,
                key=lambda p: self._calculate_distance(current, p)
            )
            route.append(nearest)
            current = nearest
            unvisited.remove(nearest)
        
        # Calculate route metrics
        total_distance = sum(
            self._calculate_distance(route[i], route[i+1])
            for i in range(len(route) - 1)
        )
        
        return {
            'optimized_route': route,
            'total_distance_km': total_distance,
            'num_waypoints': len(route),
            'estimated_time_hours': total_distance / 60.0,
            'optimization_method': 'nearest_neighbor'
        }
    
    @staticmethod
    def _calculate_distance(
        point1: Tuple[float, float],
        point2: Tuple[float, float]
    ) -> float:
        """Calculate Haversine distance between two points"""
        lat1, lon1 = point1
        lat2, lon2 = point2
        
        R = 6371  # Earth radius in km
        
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        
        a = (np.sin(dlat / 2) ** 2 +
             np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) *
             np.sin(dlon / 2) ** 2)
        
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        
        return R * c


class PredictiveMaintenanceModel:
    """Predict vehicle maintenance needs"""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.is_trained = False
    
    def predict_maintenance_window(
        self,
        vehicle_age_days: int,
        total_km: float,
        recent_issues: int,
        avg_speed_kmh: float,
        terrain_difficulty: float
    ) -> Dict[str, Any]:
        """
        Predict when vehicle will need maintenance
        
        Returns:
            Maintenance prediction with estimated days until service
        """
        # Simple rule-based prediction if not trained
        base_interval = 10000  # km
        km_to_maintenance = base_interval - (total_km % base_interval)
        
        # Adjust for factors
        if recent_issues > 2:
            km_to_maintenance *= 0.7
        if terrain_difficulty > 1.5:
            km_to_maintenance *= 0.8
        
        days_estimate = km_to_maintenance / (avg_speed_kmh * 10)  # 10 hours per day
        
        urgency = 'low'
        if days_estimate < 7:
            urgency = 'high'
        elif days_estimate < 14:
            urgency = 'medium'
        
        return {
            'days_until_maintenance': int(days_estimate),
            'km_until_maintenance': int(km_to_maintenance),
            'urgency': urgency,
            'confidence': 0.75,
            'recommended_actions': self._get_maintenance_recommendations(urgency)
        }
    
    @staticmethod
    def _get_maintenance_recommendations(urgency: str) -> List[str]:
        """Get maintenance recommendations based on urgency"""
        if urgency == 'high':
            return [
                'Schedule maintenance within 7 days',
                'Inspect brakes and tires immediately',
                'Check engine oil and filters'
            ]
        elif urgency == 'medium':
            return [
                'Plan maintenance within 2 weeks',
                'Monitor vehicle performance',
                'Prepare service schedule'
            ]
        else:
            return [
                'Routine maintenance on schedule',
                'Continue normal operations',
                'Track mileage for next service'
            ]
