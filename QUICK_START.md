# 🚀 Quick Start Guide - New Python Features

## 📦 Installation

```bash
# Install new dependencies
pip install -r requirements.txt

# Verify installation
python -c "import sqlalchemy; import numpy; import pandas; import sklearn; print('✅ All dependencies installed!')"
```

---

## 🎯 Quick Examples

### 1. Analytics - Fleet Performance

```python
from utils.analytics import FleetAnalytics

analytics = FleetAnalytics()

# Analyze fleet
report = analytics.analyze_fleet_performance(
    vehicles=vehicle_list,
    loads=load_list,
    trips=trip_list
)

print(f"Revenue: ${report.total_revenue:,.2f}")
print(f"Distance: {report.total_distance_km:,.0f} km")
print(f"Utilization: {report.avg_utilization*100:.1f}%")
print("\nRecommendations:")
for rec in report.recommendations:
    print(f"  • {rec}")
```

### 2. Machine Learning - Predict Delivery Time

```python
from utils.ml_predictor import DeliveryTimePredictor

predictor = DeliveryTimePredictor()

# Predict delivery time
result = predictor.predict(
    distance_km=500,
    traffic_factor=1.2,
    weather_score=0.9,
    time_of_day=14
)

print(f"Predicted: {result.predicted_value:.1f} hours")
print(f"Confidence: {result.confidence*100:.0f}%")
```

### 3. Database - Save and Query

```python
from utils.database import DatabaseManager

db = DatabaseManager()

# Save vehicle
db.save_vehicle({
    'vehicle_id': 'V001',
    'capacity_tons': 25,
    'status': 'idle',
    'current_lat': 40.7128,
    'current_lng': -74.0060
})

# Query vehicles
idle_vehicles = db.get_all_vehicles(status='idle')
print(f"Found {len(idle_vehicles)} idle vehicles")
```

### 4. Reports - Generate Executive Summary

```python
from utils.report_generator import ReportGenerator

generator = ReportGenerator()

# Generate report
summary = generator.generate_executive_summary(fleet_data)

# Save to JSON
generator.save_report_to_json(summary, "report.json")

print(summary['key_metrics'])
```

### 5. Cache - Store and Retrieve

```python
from utils.cache_manager import CacheManager

cache = CacheManager(max_size_mb=50.0)

# Cache data
cache.set("route:NYC-LA", route_data, ttl_seconds=3600)

# Retrieve
cached = cache.get("route:NYC-LA")

# Stats
stats = cache.get_statistics()
print(f"Hit rate: {stats['hit_rate_percent']:.1f}%")
```

### 6. Notifications - Send Alerts

```python
from utils.notification_system import notification_system, AlertType, AlertLevel

# Send alert
alert = notification_system.send_alert(
    alert_type=AlertType.FUEL_LOW,
    level=AlertLevel.CRITICAL,
    title="Critical Fuel Level",
    message="Vehicle V001 has 8% fuel remaining",
    vehicle_id="V001"
)

# Get active alerts
active = notification_system.get_active_alerts(level=AlertLevel.CRITICAL)
print(f"{len(active)} critical alerts")
```

### 7. Validation - Check Data Quality

```python
from utils.data_validator import VehicleValidator, LoadValidator

# Validate vehicle
validator = VehicleValidator()
result = validator.validate(vehicle_data)

if result.is_valid:
    print("✅ Vehicle data is valid")
    clean_data = result.sanitized_data
else:
    print("❌ Validation failed:")
    for error in result.errors:
        print(f"  • {error}")
```

---

## 🌐 API Quick Reference

### Analytics
```bash
# Fleet performance
curl http://localhost:8000/api/analytics/fleet-performance

# Profitability
curl -X POST http://localhost:8000/api/analytics/profitability
```

### Machine Learning
```bash
# Predict delivery time
curl -X POST "http://localhost:8000/api/ml/predict-delivery-time?distance_km=500&traffic_factor=1.2"
```

### Reports
```bash
# Executive summary
curl http://localhost:8000/api/reports/executive-summary

# Financial report
curl http://localhost:8000/api/reports/financial
```

### Monitoring
```bash
# Active alerts
curl http://localhost:8000/api/notifications/active

# Run health check
curl -X POST http://localhost:8000/api/monitoring/check-fleet

# Alert statistics
curl http://localhost:8000/api/notifications/statistics
```

### Cache
```bash
# Cache stats
curl http://localhost:8000/api/cache/statistics

# Clear cache
curl -X POST "http://localhost:8000/api/cache/clear?cache_type=all"
```

### Validation
```bash
# Validate vehicle
curl -X POST http://localhost:8000/api/validation/vehicle \
  -H "Content-Type: application/json" \
  -d '{"vehicle_id": "V001", "capacity_tons": 25, "status": "idle"}'

# Validate load
curl -X POST http://localhost:8000/api/validation/load \
  -H "Content-Type: application/json" \
  -d '{"load_id": "L001", "weight_tons": 15, "status": "available"}'
```

### Database
```bash
# Database statistics
curl http://localhost:8000/api/database/statistics
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific module tests
pytest tests/test_new_modules.py -v

# Run with coverage
pytest tests/ --cov=utils --cov-report=html

# Run specific test class
pytest tests/test_new_modules.py::TestFleetAnalytics -v
```

---

## 📊 Module Import Guide

```python
# Analytics
from utils.analytics import FleetAnalytics, StatisticalAnalyzer

# Machine Learning
from utils.ml_predictor import (
    DeliveryTimePredictor,
    DemandForecaster,
    RouteOptimizer,
    PredictiveMaintenanceModel
)

# Database
from utils.database import DatabaseManager, VehicleDB, LoadDB

# Reports
from utils.report_generator import ReportGenerator

# Cache
from utils.cache_manager import (
    CacheManager,
    RouteCacheManager,
    APIResponseCache,
    cache_result  # decorator
)

# Notifications
from utils.notification_system import (
    NotificationSystem,
    AlertMonitor,
    AlertType,
    AlertLevel
)

# Validation
from utils.data_validator import (
    VehicleValidator,
    LoadValidator,
    BusinessRuleValidator,
    BatchValidator
)
```

---

## 🔧 Configuration

### Database
```python
# Custom database URL
db = DatabaseManager(db_url="sqlite:///custom_fleet.db")
```

### Cache
```python
# Configure cache size and TTL
cache = CacheManager(
    max_size_mb=100.0,
    default_ttl_seconds=7200
)
```

### Reports
```python
# Custom output directory
generator = ReportGenerator(output_dir="custom_reports")
```

---

## 💡 Pro Tips

1. **Caching**: Use `@cache_result` decorator for expensive functions
2. **Validation**: Always validate external input before processing
3. **Monitoring**: Run `check-fleet` endpoint periodically
4. **Reports**: Generate reports daily for trend analysis
5. **Database**: Use `db.cleanup_old_events()` to manage size
6. **ML**: Retrain models periodically with new data
7. **Analytics**: Track KPIs over time for insights

---

## 🆘 Troubleshooting

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Database Errors
```python
# Reset database
import os
if os.path.exists('fleet_management.db'):
    os.remove('fleet_management.db')
db = DatabaseManager()  # Will recreate
```

### Cache Issues
```python
# Clear all caches
from utils.cache_manager import route_cache, api_cache
route_cache.cache.clear()
api_cache.cache.clear()
```

---

## 📚 More Information

- **Full Documentation**: See `PYTHON_MODULES_GUIDE.md`
- **Enhancement Summary**: See `PYTHON_ENHANCEMENT_SUMMARY.md`
- **Mission Status**: See `MISSION_ACCOMPLISHED.md`
- **API Documentation**: Built-in at `http://localhost:8000/docs`

---

**Quick Start Version**: 1.0  
**Last Updated**: 2026-02-02  
**Status**: ✅ Ready to use!
