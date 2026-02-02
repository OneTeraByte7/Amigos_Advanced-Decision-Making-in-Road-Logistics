"""
data_validator.py
─────────────────
Advanced data validation and sanitization utilities for fleet management.
Validates vehicle data, load data, coordinates, and business rules.
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import re


@dataclass
class ValidationResult:
    """Result of validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    sanitized_data: Optional[Dict[str, Any]] = None


class DataValidator:
    """Base validator class"""
    
    @staticmethod
    def is_valid_coordinate(lat: float, lng: float) -> bool:
        """Validate latitude and longitude"""
        return -90 <= lat <= 90 and -180 <= lng <= 180
    
    @staticmethod
    def is_positive_number(value: Any) -> bool:
        """Check if value is a positive number"""
        try:
            return float(value) > 0
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def is_non_negative(value: Any) -> bool:
        """Check if value is non-negative"""
        try:
            return float(value) >= 0
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def is_valid_percentage(value: Any) -> bool:
        """Check if value is a valid percentage (0-100)"""
        try:
            val = float(value)
            return 0 <= val <= 100
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Validate phone number format"""
        # Simple validation for international format
        pattern = r'^\+?[1-9]\d{1,14}$'
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)
        return bool(re.match(pattern, cleaned))
    
    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            value = str(value)
        
        # Remove leading/trailing whitespace
        value = value.strip()
        
        # Remove control characters
        value = ''.join(char for char in value if ord(char) >= 32 or char == '\n')
        
        # Truncate if needed
        if max_length and len(value) > max_length:
            value = value[:max_length]
        
        return value


class VehicleValidator(DataValidator):
    """Validator for vehicle data"""
    
    def validate(self, vehicle_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate vehicle data
        
        Args:
            vehicle_data: Vehicle data dictionary
        
        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []
        sanitized = vehicle_data.copy()
        
        # Required fields
        required_fields = ['vehicle_id', 'capacity_tons', 'status']
        for field in required_fields:
            if field not in vehicle_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate vehicle_id
        if 'vehicle_id' in vehicle_data:
            vehicle_id = self.sanitize_string(vehicle_data['vehicle_id'], max_length=50)
            if not vehicle_id:
                errors.append("vehicle_id cannot be empty")
            sanitized['vehicle_id'] = vehicle_id
        
        # Validate capacity
        if 'capacity_tons' in vehicle_data:
            capacity = vehicle_data['capacity_tons']
            if not self.is_positive_number(capacity):
                errors.append("capacity_tons must be a positive number")
            elif float(capacity) > 40:
                warnings.append(f"Unusually high capacity: {capacity} tons")
            sanitized['capacity_tons'] = float(capacity) if self.is_positive_number(capacity) else 0
        
        # Validate current load
        if 'current_load_tons' in vehicle_data:
            current_load = vehicle_data['current_load_tons']
            if not self.is_non_negative(current_load):
                errors.append("current_load_tons must be non-negative")
            elif 'capacity_tons' in sanitized:
                if float(current_load) > sanitized['capacity_tons']:
                    errors.append("current_load_tons exceeds vehicle capacity")
            sanitized['current_load_tons'] = float(current_load) if self.is_non_negative(current_load) else 0
        
        # Validate status
        valid_statuses = ['idle', 'en_route_loaded', 'en_route_empty', 'at_delivery', 'maintenance']
        if 'status' in vehicle_data:
            status = vehicle_data['status'].lower()
            if status not in valid_statuses:
                errors.append(f"Invalid status: {status}. Must be one of {valid_statuses}")
            sanitized['status'] = status
        
        # Validate coordinates
        if 'current_location' in vehicle_data:
            location = vehicle_data['current_location']
            if isinstance(location, dict):
                lat = location.get('lat')
                lng = location.get('lng')
                
                if lat is None or lng is None:
                    errors.append("Location must have lat and lng")
                elif not self.is_valid_coordinate(float(lat), float(lng)):
                    errors.append(f"Invalid coordinates: ({lat}, {lng})")
        
        # Validate fuel level
        if 'fuel_level_percent' in vehicle_data:
            fuel = vehicle_data['fuel_level_percent']
            if not self.is_valid_percentage(fuel):
                errors.append("fuel_level_percent must be between 0 and 100")
            elif float(fuel) < 10:
                warnings.append(f"Critical fuel level: {fuel}%")
            sanitized['fuel_level_percent'] = float(fuel) if self.is_valid_percentage(fuel) else 100
        
        # Validate kilometers
        if 'total_km_today' in vehicle_data:
            km = vehicle_data['total_km_today']
            if not self.is_non_negative(km):
                errors.append("total_km_today must be non-negative")
            elif float(km) > 2000:
                warnings.append(f"Very high daily mileage: {km} km")
            sanitized['total_km_today'] = float(km) if self.is_non_negative(km) else 0
        
        # Validate utilization rate
        if 'utilization_rate' in vehicle_data:
            util = vehicle_data['utilization_rate']
            if not self.is_non_negative(util):
                errors.append("utilization_rate must be non-negative")
            elif float(util) > 1.0:
                errors.append("utilization_rate cannot exceed 1.0")
            sanitized['utilization_rate'] = float(util) if 0 <= float(util) <= 1.0 else 0
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            sanitized_data=sanitized if len(errors) == 0 else None
        )


class LoadValidator(DataValidator):
    """Validator for load data"""
    
    def validate(self, load_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate load data
        
        Args:
            load_data: Load data dictionary
        
        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []
        sanitized = load_data.copy()
        
        # Required fields
        required_fields = ['load_id', 'origin', 'destination', 'weight_tons', 'status']
        for field in required_fields:
            if field not in load_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate load_id
        if 'load_id' in load_data:
            load_id = self.sanitize_string(load_data['load_id'], max_length=50)
            if not load_id:
                errors.append("load_id cannot be empty")
            sanitized['load_id'] = load_id
        
        # Validate weight
        if 'weight_tons' in load_data:
            weight = load_data['weight_tons']
            if not self.is_positive_number(weight):
                errors.append("weight_tons must be a positive number")
            elif float(weight) > 40:
                warnings.append(f"Heavy load: {weight} tons. May require special vehicle.")
            elif float(weight) < 0.5:
                warnings.append(f"Very light load: {weight} tons. Consider consolidation.")
            sanitized['weight_tons'] = float(weight) if self.is_positive_number(weight) else 0
        
        # Validate status
        valid_statuses = ['available', 'matched', 'in_transit', 'delivered', 'cancelled']
        if 'status' in load_data:
            status = load_data['status'].lower()
            if status not in valid_statuses:
                errors.append(f"Invalid status: {status}. Must be one of {valid_statuses}")
            sanitized['status'] = status
        
        # Validate origin
        if 'origin' in load_data:
            origin = load_data['origin']
            if isinstance(origin, dict):
                lat = origin.get('lat')
                lng = origin.get('lng')
                
                if lat is None or lng is None:
                    errors.append("Origin must have lat and lng")
                elif not self.is_valid_coordinate(float(lat), float(lng)):
                    errors.append(f"Invalid origin coordinates: ({lat}, {lng})")
        
        # Validate destination
        if 'destination' in load_data:
            destination = load_data['destination']
            if isinstance(destination, dict):
                lat = destination.get('lat')
                lng = destination.get('lng')
                
                if lat is None or lng is None:
                    errors.append("Destination must have lat and lng")
                elif not self.is_valid_coordinate(float(lat), float(lng)):
                    errors.append(f"Invalid destination coordinates: ({lat}, {lng})")
        
        # Validate origin != destination
        if 'origin' in load_data and 'destination' in load_data:
            origin = load_data['origin']
            destination = load_data['destination']
            
            if isinstance(origin, dict) and isinstance(destination, dict):
                if (origin.get('lat') == destination.get('lat') and
                    origin.get('lng') == destination.get('lng')):
                    errors.append("Origin and destination cannot be the same")
        
        # Validate distance
        if 'distance_km' in load_data:
            distance = load_data['distance_km']
            if not self.is_positive_number(distance):
                errors.append("distance_km must be a positive number")
            elif float(distance) > 5000:
                warnings.append(f"Very long distance: {distance} km")
            sanitized['distance_km'] = float(distance) if self.is_positive_number(distance) else 0
        
        # Validate revenue
        if 'total_offered_revenue' in load_data:
            revenue = load_data['total_offered_revenue']
            if not self.is_positive_number(revenue):
                errors.append("total_offered_revenue must be a positive number")
            sanitized['total_offered_revenue'] = float(revenue) if self.is_positive_number(revenue) else 0
        
        # Validate deadlines
        if 'pickup_deadline' in load_data:
            try:
                if isinstance(load_data['pickup_deadline'], str):
                    datetime.fromisoformat(load_data['pickup_deadline'].replace('Z', '+00:00'))
            except ValueError:
                errors.append("Invalid pickup_deadline format")
        
        if 'delivery_deadline' in load_data:
            try:
                if isinstance(load_data['delivery_deadline'], str):
                    datetime.fromisoformat(load_data['delivery_deadline'].replace('Z', '+00:00'))
            except ValueError:
                errors.append("Invalid delivery_deadline format")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            sanitized_data=sanitized if len(errors) == 0 else None
        )


class BusinessRuleValidator:
    """Validator for business rules"""
    
    @staticmethod
    def validate_load_assignment(
        vehicle: Dict[str, Any],
        load: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate that a load can be assigned to a vehicle
        
        Args:
            vehicle: Vehicle data
            load: Load data
        
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        # Check capacity
        vehicle_capacity = vehicle.get('capacity_tons', 0)
        load_weight = load.get('weight_tons', 0)
        current_load = vehicle.get('current_load_tons', 0)
        
        if current_load + load_weight > vehicle_capacity:
            errors.append(
                f"Load weight ({load_weight}t) + current load ({current_load}t) "
                f"exceeds vehicle capacity ({vehicle_capacity}t)"
            )
        
        # Check vehicle status
        vehicle_status = vehicle.get('status', '').lower()
        if vehicle_status not in ['idle', 'en_route_empty']:
            errors.append(f"Vehicle status '{vehicle_status}' not suitable for new load assignment")
        
        # Check load status
        load_status = load.get('status', '').lower()
        if load_status != 'available':
            errors.append(f"Load status '{load_status}' indicates it's not available for assignment")
        
        # Check fuel level
        fuel_level = vehicle.get('fuel_level_percent', 100)
        distance = load.get('distance_km', 0)
        
        # Rough estimate: 0.3L/km, 400L tank = ~1333km range
        estimated_fuel_needed = (distance / 1333) * 100
        
        if fuel_level < estimated_fuel_needed:
            warnings.append(
                f"Vehicle may not have enough fuel. Current: {fuel_level:.1f}%, "
                f"Estimated need: {estimated_fuel_needed:.1f}%"
            )
        
        # Check driver hours
        driver_hours = vehicle.get('max_driving_hours_remaining', 11)
        estimated_drive_time = distance / 60  # 60 km/h average
        
        if estimated_drive_time > driver_hours:
            warnings.append(
                f"Trip may exceed driver hours. Available: {driver_hours:.1f}h, "
                f"Estimated: {estimated_drive_time:.1f}h"
            )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    @staticmethod
    def validate_route_feasibility(
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        max_distance_km: float = 3000
    ) -> ValidationResult:
        """
        Validate route feasibility
        
        Args:
            origin: (lat, lng) tuple
            destination: (lat, lng) tuple
            max_distance_km: Maximum allowed distance
        
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        # Calculate straight-line distance (rough estimate)
        lat1, lon1 = origin
        lat2, lon2 = destination
        
        import math
        
        R = 6371  # Earth radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        # Road distance typically 1.2-1.5x straight-line
        estimated_road_distance = distance * 1.3
        
        if estimated_road_distance > max_distance_km:
            errors.append(
                f"Route exceeds maximum distance: {estimated_road_distance:.0f}km > {max_distance_km}km"
            )
        elif estimated_road_distance > max_distance_km * 0.8:
            warnings.append(
                f"Route is very long: {estimated_road_distance:.0f}km. "
                f"Consider multiple stops or relay."
            )
        
        if distance < 10:
            warnings.append("Route is very short. Consider local courier service.")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            sanitized_data={'estimated_distance_km': estimated_road_distance}
        )


class BatchValidator:
    """Validate multiple records at once"""
    
    def __init__(self):
        self.vehicle_validator = VehicleValidator()
        self.load_validator = LoadValidator()
    
    def validate_vehicles(
        self,
        vehicles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate multiple vehicles
        
        Returns:
            Summary of validation results
        """
        results = []
        valid_count = 0
        
        for vehicle in vehicles:
            result = self.vehicle_validator.validate(vehicle)
            results.append({
                'vehicle_id': vehicle.get('vehicle_id'),
                'is_valid': result.is_valid,
                'errors': result.errors,
                'warnings': result.warnings
            })
            if result.is_valid:
                valid_count += 1
        
        return {
            'total': len(vehicles),
            'valid': valid_count,
            'invalid': len(vehicles) - valid_count,
            'results': results
        }
    
    def validate_loads(
        self,
        loads: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate multiple loads
        
        Returns:
            Summary of validation results
        """
        results = []
        valid_count = 0
        
        for load in loads:
            result = self.load_validator.validate(load)
            results.append({
                'load_id': load.get('load_id'),
                'is_valid': result.is_valid,
                'errors': result.errors,
                'warnings': result.warnings
            })
            if result.is_valid:
                valid_count += 1
        
        return {
            'total': len(loads),
            'valid': valid_count,
            'invalid': len(loads) - valid_count,
            'results': results
        }


__all__ = [
    'ValidationResult',
    'DataValidator',
    'VehicleValidator',
    'LoadValidator',
    'BusinessRuleValidator',
    'BatchValidator'
]
