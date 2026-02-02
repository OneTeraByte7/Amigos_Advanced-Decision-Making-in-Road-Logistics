"""
test_new_modules.py
───────────────────
Test suite for new Python modules: analytics, ML, database, reports, cache, notifications, and validation.
"""

import pytest
from datetime import datetime, timedelta
from utils.analytics import FleetAnalytics, StatisticalAnalyzer
from utils.ml_predictor import DeliveryTimePredictor, DemandForecaster, RouteOptimizer
from utils.cache_manager import CacheManager, RouteCacheManager
from utils.notification_system import NotificationSystem, AlertLevel, AlertType, AlertMonitor
from utils.data_validator import VehicleValidator, LoadValidator, BusinessRuleValidator
from utils.report_generator import ReportGenerator


class TestFleetAnalytics:
    """Test fleet analytics module"""
    
    def test_analytics_initialization(self):
        """Test analytics engine initialization"""
        analytics = FleetAnalytics()
        assert analytics is not None
        assert isinstance(analytics.historical_data, list)
    
    def test_fleet_performance_analysis(self):
        """Test fleet performance analysis"""
        analytics = FleetAnalytics()
        
        # Mock data
        vehicles = [
            {
                'vehicle_id': 'V001',
                'total_km_today': 500,
                'loaded_km_today': 400,
                'utilization_rate': 0.8,
                'fuel_level_percent': 60,
                'capacity_tons': 25,
                'current_load_tons': 20,
                'status': 'en_route_loaded'
            }
        ]
        
        loads = [
            {
                'load_id': 'L001',
                'total_offered_revenue': 5000,
                'status': 'delivered'
            }
        ]
        
        trips = []
        
        report = analytics.analyze_fleet_performance(vehicles, loads, trips)
        
        assert report is not None
        assert report.total_revenue > 0
        assert report.total_distance_km > 0
        assert len(report.recommendations) > 0
    
    def test_profitability_calculation(self):
        """Test profitability metrics calculation"""
        analytics = FleetAnalytics()
        
        vehicles = [
            {'vehicle_id': 'V001', 'total_km_today': 500}
        ]
        
        loads = [
            {'total_offered_revenue': 2000, 'status': 'delivered'}
        ]
        
        metrics = analytics.calculate_profitability_metrics(vehicles, loads)
        
        assert 'total_revenue' in metrics
        assert 'total_costs' in metrics
        assert 'profit' in metrics
        assert 'profit_margin_percent' in metrics


class TestStatisticalAnalyzer:
    """Test statistical analysis tools"""
    
    def test_percentile_calculation(self):
        """Test percentile calculation"""
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        p50 = StatisticalAnalyzer.calculate_percentile(values, 50)
        assert p50 == 5.5
    
    def test_standard_deviation(self):
        """Test standard deviation calculation"""
        values = [2, 4, 6, 8, 10]
        std = StatisticalAnalyzer.calculate_standard_deviation(values)
        assert std > 0
    
    def test_outlier_detection(self):
        """Test outlier detection"""
        values = [10, 12, 13, 11, 10, 12, 100, 11, 13]
        outliers = StatisticalAnalyzer.detect_outliers(values, threshold=2.0)
        assert len(outliers) > 0
    
    def test_trend_direction(self):
        """Test trend direction analysis"""
        increasing = [1, 2, 3, 4, 5]
        decreasing = [5, 4, 3, 2, 1]
        stable = [5, 5, 5, 5, 5]
        
        assert StatisticalAnalyzer.calculate_trend_direction(increasing) == "increasing"
        assert StatisticalAnalyzer.calculate_trend_direction(decreasing) == "decreasing"
        assert StatisticalAnalyzer.calculate_trend_direction(stable) == "stable"


class TestMLPredictors:
    """Test machine learning predictors"""
    
    def test_delivery_time_predictor_initialization(self):
        """Test predictor initialization"""
        predictor = DeliveryTimePredictor()
        assert predictor is not None
        assert not predictor.is_trained
    
    def test_delivery_time_prediction_without_training(self):
        """Test prediction with heuristic model"""
        predictor = DeliveryTimePredictor()
        
        result = predictor.predict(
            distance_km=100,
            traffic_factor=1.0,
            weather_score=1.0
        )
        
        assert result is not None
        assert result.predicted_value > 0
        assert 0 <= result.confidence <= 1
        assert result.model_type == 'heuristic'
    
    def test_demand_forecaster(self):
        """Test demand forecasting"""
        forecaster = DemandForecaster()
        
        result = forecaster.forecast(
            day_of_week=3,
            week_of_year=20,
            month=5
        )
        
        assert result is not None
        assert result.predicted_value >= 0
    
    def test_route_optimizer(self):
        """Test route optimization"""
        optimizer = RouteOptimizer()
        
        waypoints = [
            (40.7128, -74.0060),  # New York
            (34.0522, -118.2437), # Los Angeles
            (41.8781, -87.6298)   # Chicago
        ]
        
        result = optimizer.optimize_route(waypoints)
        
        assert 'optimized_route' in result
        assert 'total_distance_km' in result
        assert result['total_distance_km'] > 0


class TestCacheManager:
    """Test caching system"""
    
    def test_cache_initialization(self):
        """Test cache initialization"""
        cache = CacheManager(max_size_mb=10.0, default_ttl_seconds=60)
        assert cache is not None
        assert cache.current_size_bytes == 0
    
    def test_cache_set_and_get(self):
        """Test cache set and get operations"""
        cache = CacheManager()
        
        cache.set("key1", "value1")
        value = cache.get("key1")
        
        assert value == "value1"
        assert cache.hits == 1
    
    def test_cache_miss(self):
        """Test cache miss"""
        cache = CacheManager()
        value = cache.get("nonexistent")
        
        assert value is None
        assert cache.misses == 1
    
    def test_cache_expiration(self):
        """Test cache expiration"""
        cache = CacheManager()
        
        cache.set("key1", "value1", ttl_seconds=1)
        
        import time
        time.sleep(2)
        
        value = cache.get("key1")
        assert value is None
        assert cache.expirations > 0
    
    def test_route_cache(self):
        """Test route caching"""
        route_cache = RouteCacheManager()
        
        route_data = {
            'distance_km': 500,
            'coordinates': [[40.7, -74.0], [41.8, -87.6]]
        }
        
        route_cache.cache_route(40.7, -74.0, 41.8, -87.6, route_data)
        
        cached = route_cache.get_route(40.7, -74.0, 41.8, -87.6)
        
        assert cached is not None
        assert cached['distance_km'] == 500


class TestNotificationSystem:
    """Test notification system"""
    
    def test_notification_system_initialization(self):
        """Test notification system initialization"""
        system = NotificationSystem()
        assert system is not None
        assert len(system.channels) > 0
    
    def test_send_alert(self):
        """Test sending an alert"""
        system = NotificationSystem()
        
        alert = system.send_alert(
            alert_type=AlertType.FUEL_LOW,
            level=AlertLevel.WARNING,
            title="Test Alert",
            message="This is a test",
            vehicle_id="V001"
        )
        
        assert alert is not None
        assert alert.alert_type == AlertType.FUEL_LOW
        assert alert.level == AlertLevel.WARNING
        assert alert.vehicle_id == "V001"
    
    def test_acknowledge_alert(self):
        """Test alert acknowledgment"""
        system = NotificationSystem()
        
        alert = system.send_alert(
            alert_type=AlertType.MAINTENANCE_DUE,
            level=AlertLevel.INFO,
            title="Test",
            message="Test message"
        )
        
        success = system.acknowledge_alert(alert.alert_id, "test_user")
        
        assert success is True
        assert alert.acknowledged is True
        assert alert.acknowledged_by == "test_user"
    
    def test_get_active_alerts(self):
        """Test getting active alerts"""
        system = NotificationSystem()
        
        system.send_alert(
            alert_type=AlertType.FUEL_LOW,
            level=AlertLevel.WARNING,
            title="Alert 1",
            message="Message 1"
        )
        
        system.send_alert(
            alert_type=AlertType.DELIVERY_DELAY,
            level=AlertLevel.CRITICAL,
            title="Alert 2",
            message="Message 2"
        )
        
        active = system.get_active_alerts()
        assert len(active) >= 2
    
    def test_alert_monitor(self):
        """Test alert monitoring"""
        system = NotificationSystem()
        monitor = AlertMonitor(system)
        
        vehicles = [
            {
                'vehicle_id': 'V001',
                'fuel_level_percent': 10,
                'max_driving_hours_remaining': 0.5,
                'total_km_today': 500
            }
        ]
        
        monitor.check_vehicle_fuel(vehicles)
        monitor.check_driver_hours(vehicles)
        
        active_alerts = system.get_active_alerts()
        assert len(active_alerts) > 0


class TestDataValidators:
    """Test data validation"""
    
    def test_vehicle_validator(self):
        """Test vehicle data validation"""
        validator = VehicleValidator()
        
        valid_vehicle = {
            'vehicle_id': 'V001',
            'capacity_tons': 25,
            'current_load_tons': 15,
            'status': 'idle',
            'fuel_level_percent': 80
        }
        
        result = validator.validate(valid_vehicle)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_vehicle_validator_invalid_data(self):
        """Test vehicle validation with invalid data"""
        validator = VehicleValidator()
        
        invalid_vehicle = {
            'vehicle_id': 'V001',
            'capacity_tons': -5,  # Invalid
            'current_load_tons': 30,
            'status': 'invalid_status',  # Invalid
            'fuel_level_percent': 150  # Invalid
        }
        
        result = validator.validate(invalid_vehicle)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    def test_load_validator(self):
        """Test load data validation"""
        validator = LoadValidator()
        
        valid_load = {
            'load_id': 'L001',
            'origin': {'lat': 40.7128, 'lng': -74.0060, 'name': 'NYC'},
            'destination': {'lat': 34.0522, 'lng': -118.2437, 'name': 'LA'},
            'weight_tons': 15,
            'status': 'available',
            'distance_km': 4500
        }
        
        result = validator.validate(valid_load)
        
        assert result.is_valid is True
    
    def test_load_validator_same_origin_destination(self):
        """Test validation fails when origin equals destination"""
        validator = LoadValidator()
        
        invalid_load = {
            'load_id': 'L001',
            'origin': {'lat': 40.7128, 'lng': -74.0060, 'name': 'NYC'},
            'destination': {'lat': 40.7128, 'lng': -74.0060, 'name': 'NYC'},
            'weight_tons': 15,
            'status': 'available'
        }
        
        result = validator.validate(invalid_load)
        
        assert result.is_valid is False
        assert any('same' in error.lower() for error in result.errors)
    
    def test_business_rule_validator(self):
        """Test business rule validation"""
        vehicle = {
            'vehicle_id': 'V001',
            'capacity_tons': 25,
            'current_load_tons': 5,
            'status': 'idle',
            'fuel_level_percent': 80
        }
        
        load = {
            'load_id': 'L001',
            'weight_tons': 15,
            'status': 'available',
            'distance_km': 500
        }
        
        result = BusinessRuleValidator.validate_load_assignment(vehicle, load)
        
        assert result.is_valid is True
    
    def test_business_rule_validator_capacity_exceeded(self):
        """Test validation fails when capacity exceeded"""
        vehicle = {
            'vehicle_id': 'V001',
            'capacity_tons': 25,
            'current_load_tons': 20,
            'status': 'idle'
        }
        
        load = {
            'load_id': 'L001',
            'weight_tons': 10,  # Total would be 30 > 25
            'status': 'available'
        }
        
        result = BusinessRuleValidator.validate_load_assignment(vehicle, load)
        
        assert result.is_valid is False


class TestReportGenerator:
    """Test report generation"""
    
    def test_report_generator_initialization(self):
        """Test report generator initialization"""
        generator = ReportGenerator()
        assert generator is not None
    
    def test_executive_summary_generation(self):
        """Test executive summary generation"""
        generator = ReportGenerator()
        
        fleet_data = {
            'vehicles': [
                {
                    'vehicle_id': 'V001',
                    'status': 'idle',
                    'total_km_today': 500,
                    'utilization_rate': 0.8
                }
            ],
            'loads': [
                {
                    'load_id': 'L001',
                    'status': 'delivered',
                    'total_offered_revenue': 5000
                }
            ],
            'trips': []
        }
        
        summary = generator.generate_executive_summary(fleet_data)
        
        assert 'key_metrics' in summary
        assert 'fleet_status' in summary
        assert 'recommendations' in summary
    
    def test_vehicle_performance_report(self):
        """Test vehicle performance report"""
        generator = ReportGenerator()
        
        vehicles = [
            {
                'vehicle_id': 'V001',
                'status': 'en_route_loaded',
                'total_km_today': 500,
                'loaded_km_today': 400,
                'utilization_rate': 0.8,
                'fuel_level_percent': 60,
                'capacity_tons': 25,
                'current_load_tons': 20
            }
        ]
        
        report = generator.generate_vehicle_performance_report(vehicles)
        
        assert 'vehicles' in report
        assert 'top_performers' in report
        assert len(report['vehicles']) > 0
    
    def test_financial_report(self):
        """Test financial report generation"""
        generator = ReportGenerator()
        
        loads = [
            {'total_offered_revenue': 5000, 'status': 'delivered'}
        ]
        
        vehicles = [
            {'vehicle_id': 'V001', 'total_km_today': 500}
        ]
        
        report = generator.generate_financial_report(loads, vehicles)
        
        assert 'revenue' in report
        assert 'costs' in report
        assert 'profitability' in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
