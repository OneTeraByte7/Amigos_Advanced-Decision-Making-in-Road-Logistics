"""
analytics.py
──────────────
Advanced analytics and data analysis for fleet operations.
Provides statistical insights, trend analysis, and performance metrics.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from core.models import Vehicle, Load, Trip, FleetState


@dataclass
class AnalyticsReport:
    """Container for analytics results"""
    period_start: datetime
    period_end: datetime
    total_revenue: float
    total_distance_km: float
    total_trips: int
    avg_utilization: float
    avg_revenue_per_km: float
    top_performing_vehicles: List[Dict[str, Any]]
    route_efficiency_score: float
    fuel_efficiency_score: float
    recommendations: List[str]


class FleetAnalytics:
    """Advanced analytics engine for fleet performance"""
    
    def __init__(self):
        self.historical_data: List[Dict[str, Any]] = []
        self.performance_cache: Dict[str, Any] = {}
    
    def analyze_fleet_performance(
        self,
        vehicles: List[Vehicle],
        loads: List[Load],
        trips: List[Trip],
        time_period_days: int = 7
    ) -> AnalyticsReport:
        """
        Comprehensive fleet performance analysis
        
        Args:
            vehicles: List of vehicles to analyze
            loads: List of loads delivered
            trips: List of completed trips
            time_period_days: Analysis time window
        
        Returns:
            AnalyticsReport with comprehensive insights
        """
        period_end = datetime.now()
        period_start = period_end - timedelta(days=time_period_days)
        
        # Calculate core metrics
        total_revenue = sum(load.total_offered_revenue for load in loads)
        total_distance = sum(vehicle.total_km_today for vehicle in vehicles)
        total_trips = len(trips)
        
        # Calculate average utilization
        utilization_rates = [v.utilization_rate for v in vehicles if v.total_km_today > 0]
        avg_utilization = np.mean(utilization_rates) if utilization_rates else 0.0
        
        # Revenue per kilometer
        avg_revenue_per_km = total_revenue / total_distance if total_distance > 0 else 0.0
        
        # Identify top performers
        top_performers = self._identify_top_performers(vehicles, loads)
        
        # Calculate efficiency scores
        route_efficiency = self._calculate_route_efficiency(vehicles, trips)
        fuel_efficiency = self._calculate_fuel_efficiency(vehicles)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            vehicles, loads, avg_utilization, fuel_efficiency
        )
        
        return AnalyticsReport(
            period_start=period_start,
            period_end=period_end,
            total_revenue=total_revenue,
            total_distance_km=total_distance,
            total_trips=total_trips,
            avg_utilization=avg_utilization,
            avg_revenue_per_km=avg_revenue_per_km,
            top_performing_vehicles=top_performers,
            route_efficiency_score=route_efficiency,
            fuel_efficiency_score=fuel_efficiency,
            recommendations=recommendations
        )
    
    def _identify_top_performers(
        self,
        vehicles: List[Vehicle],
        loads: List[Load]
    ) -> List[Dict[str, Any]]:
        """Identify top performing vehicles"""
        vehicle_performance = []
        
        for vehicle in vehicles:
            if vehicle.total_km_today == 0:
                continue
            
            performance_score = (
                vehicle.utilization_rate * 0.4 +
                (vehicle.loaded_km_today / vehicle.total_km_today) * 0.3 +
                (1.0 - vehicle.fuel_level_percent / 100.0) * 0.3
            )
            
            vehicle_performance.append({
                'vehicle_id': vehicle.vehicle_id,
                'score': performance_score,
                'total_km': vehicle.total_km_today,
                'utilization': vehicle.utilization_rate * 100,
                'efficiency': (vehicle.loaded_km_today / vehicle.total_km_today * 100) if vehicle.total_km_today > 0 else 0
            })
        
        # Sort by score and return top 5
        vehicle_performance.sort(key=lambda x: x['score'], reverse=True)
        return vehicle_performance[:5]
    
    def _calculate_route_efficiency(
        self,
        vehicles: List[Vehicle],
        trips: List[Trip]
    ) -> float:
        """Calculate overall route efficiency score (0-100)"""
        if not vehicles or not trips:
            return 0.0
        
        # Efficiency based on empty miles ratio
        total_km = sum(v.total_km_today for v in vehicles)
        loaded_km = sum(v.loaded_km_today for v in vehicles)
        
        if total_km == 0:
            return 0.0
        
        efficiency = (loaded_km / total_km) * 100
        return min(efficiency, 100.0)
    
    def _calculate_fuel_efficiency(self, vehicles: List[Vehicle]) -> float:
        """Calculate fleet fuel efficiency score"""
        if not vehicles:
            return 0.0
        
        # Average fuel remaining indicates efficiency
        avg_fuel = np.mean([v.fuel_level_percent for v in vehicles])
        
        # Better score if fuel is being used efficiently
        efficiency_score = 100 - avg_fuel
        return max(0.0, min(efficiency_score, 100.0))
    
    def _generate_recommendations(
        self,
        vehicles: List[Vehicle],
        loads: List[Load],
        avg_utilization: float,
        fuel_efficiency: float
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if avg_utilization < 0.6:
            recommendations.append(
                f"Low utilization ({avg_utilization*100:.1f}%). Consider consolidating loads or reducing fleet size."
            )
        
        if fuel_efficiency < 50:
            recommendations.append(
                f"Poor fuel efficiency ({fuel_efficiency:.1f}%). Review routing and driver behavior."
            )
        
        idle_vehicles = [v for v in vehicles if v.status.value == 'idle']
        if len(idle_vehicles) > len(vehicles) * 0.3:
            recommendations.append(
                f"{len(idle_vehicles)} vehicles idle. Increase load matching aggressiveness."
            )
        
        available_loads = [l for l in loads if l.status.value == 'available']
        if len(available_loads) > 5:
            recommendations.append(
                f"{len(available_loads)} unmatched loads. Review pricing and capacity allocation."
            )
        
        if not recommendations:
            recommendations.append("Fleet operating efficiently. Maintain current strategy.")
        
        return recommendations
    
    def calculate_profitability_metrics(
        self,
        vehicles: List[Vehicle],
        loads: List[Load]
    ) -> Dict[str, float]:
        """Calculate detailed profitability metrics"""
        total_revenue = sum(load.total_offered_revenue for load in loads)
        total_distance = sum(v.total_km_today for v in vehicles)
        
        # Estimated costs
        fuel_cost_per_km = 0.45  # USD per km
        maintenance_cost_per_km = 0.15
        driver_cost_per_km = 0.25
        
        total_costs = total_distance * (
            fuel_cost_per_km + maintenance_cost_per_km + driver_cost_per_km
        )
        
        profit = total_revenue - total_costs
        profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            'total_revenue': total_revenue,
            'total_costs': total_costs,
            'profit': profit,
            'profit_margin_percent': profit_margin,
            'cost_per_km': total_costs / total_distance if total_distance > 0 else 0,
            'revenue_per_km': total_revenue / total_distance if total_distance > 0 else 0
        }
    
    def predict_demand_trend(
        self,
        historical_loads: List[Dict[str, Any]],
        forecast_days: int = 7
    ) -> Dict[str, List[float]]:
        """Predict load demand trends using simple moving average"""
        if not historical_loads:
            return {'dates': [], 'predicted_loads': []}
        
        # Convert to pandas DataFrame for easier analysis
        df = pd.DataFrame(historical_loads)
        
        if 'timestamp' not in df.columns:
            return {'dates': [], 'predicted_loads': []}
        
        # Group by date and count loads
        df['date'] = pd.to_datetime(df['timestamp'], unit='s')
        daily_counts = df.groupby(df['date'].dt.date).size()
        
        # Simple moving average for prediction
        window = min(7, len(daily_counts))
        if window > 0:
            moving_avg = daily_counts.rolling(window=window).mean().iloc[-1]
        else:
            moving_avg = 0
        
        # Generate forecast
        last_date = daily_counts.index[-1] if len(daily_counts) > 0 else datetime.now().date()
        forecast_dates = [
            last_date + timedelta(days=i) for i in range(1, forecast_days + 1)
        ]
        predicted_values = [moving_avg] * forecast_days
        
        return {
            'dates': [str(d) for d in forecast_dates],
            'predicted_loads': predicted_values
        }
    
    def calculate_vehicle_roi(self, vehicle: Vehicle) -> Dict[str, float]:
        """Calculate return on investment for a specific vehicle"""
        # Estimated vehicle cost and operational costs
        vehicle_purchase_cost = 120000  # USD
        daily_operational_cost = 450  # USD
        
        # Revenue generated (estimated from utilization and distance)
        estimated_revenue = vehicle.total_km_today * 2.5  # $2.5 per km
        
        # Simple ROI calculation
        daily_profit = estimated_revenue - daily_operational_cost
        payback_days = vehicle_purchase_cost / daily_profit if daily_profit > 0 else float('inf')
        
        return {
            'estimated_daily_revenue': estimated_revenue,
            'daily_operational_cost': daily_operational_cost,
            'daily_profit': daily_profit,
            'estimated_payback_days': payback_days,
            'utilization_rate': vehicle.utilization_rate * 100
        }


class StatisticalAnalyzer:
    """Statistical analysis tools for fleet data"""
    
    @staticmethod
    def calculate_percentile(values: List[float], percentile: float) -> float:
        """Calculate percentile value"""
        if not values:
            return 0.0
        return float(np.percentile(values, percentile))
    
    @staticmethod
    def calculate_standard_deviation(values: List[float]) -> float:
        """Calculate standard deviation"""
        if not values:
            return 0.0
        return float(np.std(values))
    
    @staticmethod
    def calculate_correlation(x: List[float], y: List[float]) -> float:
        """Calculate correlation coefficient between two variables"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        return float(np.corrcoef(x, y)[0, 1])
    
    @staticmethod
    def detect_outliers(values: List[float], threshold: float = 2.0) -> List[int]:
        """Detect outliers using z-score method"""
        if not values:
            return []
        
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:
            return []
        
        z_scores = [(v - mean) / std for v in values]
        outlier_indices = [i for i, z in enumerate(z_scores) if abs(z) > threshold]
        
        return outlier_indices
    
    @staticmethod
    def calculate_trend_direction(values: List[float]) -> str:
        """Determine if trend is increasing, decreasing, or stable"""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear regression slope
        x = np.arange(len(values))
        y = np.array(values)
        
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
