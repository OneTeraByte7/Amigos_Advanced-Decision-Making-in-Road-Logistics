"""
report_generator.py
───────────────────
Generate comprehensive reports in various formats (JSON, CSV, HTML).
Creates executive summaries, performance reports, and analytics dashboards.
"""

import json
import csv
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from io import StringIO
import os


class ReportGenerator:
    """Generate various types of reports for fleet management"""
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize report generator
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def generate_executive_summary(
        self,
        fleet_data: Dict[str, Any],
        period_days: int = 7
    ) -> Dict[str, Any]:
        """
        Generate executive summary report
        
        Args:
            fleet_data: Current fleet state data
            period_days: Reporting period in days
        
        Returns:
            Executive summary dictionary
        """
        vehicles = fleet_data.get('vehicles', [])
        loads = fleet_data.get('loads', [])
        trips = fleet_data.get('trips', [])
        
        # Calculate key metrics
        total_revenue = sum(
            load.get('total_offered_revenue', 0) for load in loads
        )
        total_distance = sum(
            vehicle.get('total_km_today', 0) for vehicle in vehicles
        )
        
        active_vehicles = len([
            v for v in vehicles 
            if v.get('status') not in ['idle', 'maintenance']
        ])
        
        delivered_loads = len([
            l for l in loads 
            if l.get('status') == 'delivered'
        ])
        
        # Calculate utilization
        if vehicles:
            avg_utilization = sum(
                v.get('utilization_rate', 0) for v in vehicles
            ) / len(vehicles)
        else:
            avg_utilization = 0.0
        
        summary = {
            'report_title': 'Executive Summary',
            'period': f'Last {period_days} days',
            'generated_at': datetime.now().isoformat(),
            'key_metrics': {
                'total_revenue': f'${total_revenue:,.2f}',
                'total_distance_km': f'{total_distance:,.1f}',
                'active_vehicles': active_vehicles,
                'total_vehicles': len(vehicles),
                'delivered_loads': delivered_loads,
                'total_loads': len(loads),
                'avg_utilization': f'{avg_utilization * 100:.1f}%',
                'revenue_per_km': f'${total_revenue / total_distance:.2f}' if total_distance > 0 else '$0.00'
            },
            'fleet_status': {
                'idle': len([v for v in vehicles if v.get('status') == 'idle']),
                'en_route': len([v for v in vehicles if 'en_route' in v.get('status', '')]),
                'at_delivery': len([v for v in vehicles if v.get('status') == 'at_delivery']),
                'maintenance': len([v for v in vehicles if v.get('status') == 'maintenance'])
            },
            'load_status': {
                'available': len([l for l in loads if l.get('status') == 'available']),
                'matched': len([l for l in loads if l.get('status') == 'matched']),
                'in_transit': len([l for l in loads if l.get('status') == 'in_transit']),
                'delivered': delivered_loads
            },
            'recommendations': self._generate_executive_recommendations(
                vehicles, loads, avg_utilization
            )
        }
        
        return summary
    
    def _generate_executive_recommendations(
        self,
        vehicles: List[Dict[str, Any]],
        loads: List[Dict[str, Any]],
        avg_utilization: float
    ) -> List[str]:
        """Generate executive-level recommendations"""
        recommendations = []
        
        if avg_utilization < 0.6:
            recommendations.append(
                "⚠️ Fleet utilization is below target. Consider load consolidation strategies."
            )
        
        idle_count = len([v for v in vehicles if v.get('status') == 'idle'])
        if idle_count > len(vehicles) * 0.3:
            recommendations.append(
                f"⚠️ {idle_count} vehicles idle. Increase marketing efforts or reduce fleet size."
            )
        
        available_loads = len([l for l in loads if l.get('status') == 'available'])
        if available_loads > 10:
            recommendations.append(
                f"⚠️ {available_loads} unmatched loads. Review pricing strategy and capacity allocation."
            )
        
        if avg_utilization > 0.85:
            recommendations.append(
                "✅ Excellent utilization! Consider expanding fleet to capture more opportunities."
            )
        
        if not recommendations:
            recommendations.append("✅ Fleet operations are running efficiently.")
        
        return recommendations
    
    def generate_vehicle_performance_report(
        self,
        vehicles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate detailed vehicle performance report
        
        Args:
            vehicles: List of vehicle data
        
        Returns:
            Vehicle performance report
        """
        vehicle_metrics = []
        
        for vehicle in vehicles:
            total_km = vehicle.get('total_km_today', 0)
            loaded_km = vehicle.get('loaded_km_today', 0)
            
            metrics = {
                'vehicle_id': vehicle.get('vehicle_id'),
                'status': vehicle.get('status'),
                'total_km': total_km,
                'loaded_km': loaded_km,
                'empty_km': total_km - loaded_km,
                'utilization_rate': f"{vehicle.get('utilization_rate', 0) * 100:.1f}%",
                'fuel_level': f"{vehicle.get('fuel_level_percent', 0):.1f}%",
                'capacity_tons': vehicle.get('capacity_tons', 0),
                'current_load_tons': vehicle.get('current_load_tons', 0),
                'efficiency_score': self._calculate_efficiency_score(vehicle)
            }
            vehicle_metrics.append(metrics)
        
        # Sort by efficiency score
        vehicle_metrics.sort(key=lambda x: x['efficiency_score'], reverse=True)
        
        return {
            'report_title': 'Vehicle Performance Report',
            'generated_at': datetime.now().isoformat(),
            'total_vehicles': len(vehicles),
            'vehicles': vehicle_metrics,
            'top_performers': vehicle_metrics[:5],
            'bottom_performers': vehicle_metrics[-5:] if len(vehicle_metrics) > 5 else []
        }
    
    def _calculate_efficiency_score(self, vehicle: Dict[str, Any]) -> float:
        """Calculate overall efficiency score for a vehicle"""
        total_km = vehicle.get('total_km_today', 0)
        loaded_km = vehicle.get('loaded_km_today', 0)
        utilization = vehicle.get('utilization_rate', 0)
        
        if total_km == 0:
            return 0.0
        
        load_ratio = loaded_km / total_km
        efficiency = (load_ratio * 0.6) + (utilization * 0.4)
        
        return round(efficiency * 100, 2)
    
    def generate_financial_report(
        self,
        loads: List[Dict[str, Any]],
        vehicles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate financial performance report
        
        Args:
            loads: List of load data
            vehicles: List of vehicle data
        
        Returns:
            Financial report
        """
        # Revenue calculation
        total_revenue = sum(
            load.get('total_offered_revenue', 0) for load in loads
        )
        delivered_revenue = sum(
            load.get('total_offered_revenue', 0) 
            for load in loads 
            if load.get('status') == 'delivered'
        )
        
        # Cost estimation
        total_distance = sum(v.get('total_km_today', 0) for v in vehicles)
        fuel_cost = total_distance * 0.45  # $0.45 per km
        maintenance_cost = total_distance * 0.15  # $0.15 per km
        driver_cost = total_distance * 0.30  # $0.30 per km
        
        total_costs = fuel_cost + maintenance_cost + driver_cost
        net_profit = delivered_revenue - total_costs
        profit_margin = (net_profit / delivered_revenue * 100) if delivered_revenue > 0 else 0
        
        return {
            'report_title': 'Financial Performance Report',
            'generated_at': datetime.now().isoformat(),
            'revenue': {
                'total_potential': f'${total_revenue:,.2f}',
                'delivered': f'${delivered_revenue:,.2f}',
                'pending': f'${total_revenue - delivered_revenue:,.2f}'
            },
            'costs': {
                'fuel': f'${fuel_cost:,.2f}',
                'maintenance': f'${maintenance_cost:,.2f}',
                'driver': f'${driver_cost:,.2f}',
                'total': f'${total_costs:,.2f}'
            },
            'profitability': {
                'net_profit': f'${net_profit:,.2f}',
                'profit_margin': f'{profit_margin:.2f}%',
                'cost_per_km': f'${total_costs / total_distance:.2f}' if total_distance > 0 else '$0.00',
                'revenue_per_km': f'${delivered_revenue / total_distance:.2f}' if total_distance > 0 else '$0.00'
            },
            'breakdown': {
                'total_distance_km': f'{total_distance:,.1f}',
                'loads_delivered': len([l for l in loads if l.get('status') == 'delivered']),
                'avg_revenue_per_load': f'${delivered_revenue / len([l for l in loads if l.get("status") == "delivered"]):,.2f}' if len([l for l in loads if l.get('status') == 'delivered']) > 0 else '$0.00'
            }
        }
    
    def generate_load_analysis_report(
        self,
        loads: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate load analysis report
        
        Args:
            loads: List of load data
        
        Returns:
            Load analysis report
        """
        if not loads:
            return {
                'report_title': 'Load Analysis Report',
                'generated_at': datetime.now().isoformat(),
                'message': 'No load data available'
            }
        
        # Status breakdown
        status_counts = {}
        for load in loads:
            status = load.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Weight and distance analysis
        total_weight = sum(load.get('weight_tons', 0) for load in loads)
        avg_weight = total_weight / len(loads) if loads else 0
        
        distances = [load.get('distance_km', 0) for load in loads if load.get('distance_km', 0) > 0]
        avg_distance = sum(distances) / len(distances) if distances else 0
        
        # Revenue analysis
        revenues = [load.get('total_offered_revenue', 0) for load in loads]
        total_revenue = sum(revenues)
        avg_revenue = total_revenue / len(revenues) if revenues else 0
        
        return {
            'report_title': 'Load Analysis Report',
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_loads': len(loads),
                'status_breakdown': status_counts,
                'total_weight_tons': f'{total_weight:,.1f}',
                'avg_weight_tons': f'{avg_weight:.1f}',
                'avg_distance_km': f'{avg_distance:.1f}',
                'total_revenue': f'${total_revenue:,.2f}',
                'avg_revenue_per_load': f'${avg_revenue:,.2f}'
            },
            'top_routes': self._identify_top_routes(loads),
            'insights': self._generate_load_insights(loads)
        }
    
    def _identify_top_routes(
        self,
        loads: List[Dict[str, Any]],
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """Identify most common or profitable routes"""
        route_stats = {}
        
        for load in loads:
            origin = load.get('origin', {}).get('name', 'Unknown')
            destination = load.get('destination', {}).get('name', 'Unknown')
            route = f"{origin} → {destination}"
            
            if route not in route_stats:
                route_stats[route] = {
                    'count': 0,
                    'total_revenue': 0,
                    'total_weight': 0
                }
            
            route_stats[route]['count'] += 1
            route_stats[route]['total_revenue'] += load.get('total_offered_revenue', 0)
            route_stats[route]['total_weight'] += load.get('weight_tons', 0)
        
        # Sort by revenue
        sorted_routes = sorted(
            route_stats.items(),
            key=lambda x: x[1]['total_revenue'],
            reverse=True
        )
        
        return [
            {
                'route': route,
                'shipments': stats['count'],
                'revenue': f"${stats['total_revenue']:,.2f}",
                'weight': f"{stats['total_weight']:.1f}t"
            }
            for route, stats in sorted_routes[:top_n]
        ]
    
    def _generate_load_insights(
        self,
        loads: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate insights from load data"""
        insights = []
        
        available = len([l for l in loads if l.get('status') == 'available'])
        if available > len(loads) * 0.3:
            insights.append(
                f"High percentage ({available}/{len(loads)}) of loads unmatched. Review pricing or fleet capacity."
            )
        
        heavy_loads = len([l for l in loads if l.get('weight_tons', 0) > 20])
        if heavy_loads > 0:
            insights.append(
                f"{heavy_loads} heavy loads (>20 tons) require specialized vehicles."
            )
        
        long_distance = len([l for l in loads if l.get('distance_km', 0) > 1000])
        if long_distance > 0:
            insights.append(
                f"{long_distance} long-distance loads (>1000km) require careful driver scheduling."
            )
        
        return insights if insights else ["Load distribution appears balanced."]
    
    def save_report_to_json(
        self,
        report: Dict[str, Any],
        filename: str
    ) -> str:
        """
        Save report to JSON file
        
        Args:
            report: Report data
            filename: Output filename
        
        Returns:
            Full path to saved file
        """
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        return filepath
    
    def save_report_to_csv(
        self,
        data: List[Dict[str, Any]],
        filename: str
    ) -> str:
        """
        Save tabular data to CSV file
        
        Args:
            data: List of dictionaries
            filename: Output filename
        
        Returns:
            Full path to saved file
        """
        if not data:
            return ""
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        return filepath
    
    def generate_html_dashboard(
        self,
        reports: Dict[str, Any]
    ) -> str:
        """
        Generate HTML dashboard with all reports
        
        Args:
            reports: Dictionary of report data
        
        Returns:
            HTML string
        """
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Fleet Management Dashboard</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
        }}
        .metric {{
            display: inline-block;
            margin: 10px 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
            min-width: 200px;
        }}
        .metric-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #007bff;
            color: white;
        }}
        .recommendation {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 10px;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Fleet Management Dashboard</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Executive Summary</h2>
        <div class="metrics">
            {self._render_metrics(reports.get('executive_summary', {}).get('key_metrics', {}))}
        </div>
        
        <h2>Recommendations</h2>
        {self._render_recommendations(reports.get('executive_summary', {}).get('recommendations', []))}
        
        <h2>Top Performing Vehicles</h2>
        {self._render_vehicle_table(reports.get('vehicle_performance', {}).get('top_performers', []))}
        
        <h2>Financial Overview</h2>
        {self._render_financial_section(reports.get('financial', {}))}
        
    </div>
</body>
</html>
"""
        return html
    
    def _render_metrics(self, metrics: Dict[str, Any]) -> str:
        """Render metrics as HTML"""
        html = ""
        for label, value in metrics.items():
            html += f"""
            <div class="metric">
                <div class="metric-label">{label.replace('_', ' ')}</div>
                <div class="metric-value">{value}</div>
            </div>
            """
        return html
    
    def _render_recommendations(self, recommendations: List[str]) -> str:
        """Render recommendations as HTML"""
        html = ""
        for rec in recommendations:
            html += f'<div class="recommendation">{rec}</div>'
        return html
    
    def _render_vehicle_table(self, vehicles: List[Dict[str, Any]]) -> str:
        """Render vehicle table as HTML"""
        if not vehicles:
            return "<p>No vehicle data available</p>"
        
        html = "<table><thead><tr>"
        for key in vehicles[0].keys():
            html += f"<th>{key.replace('_', ' ').title()}</th>"
        html += "</tr></thead><tbody>"
        
        for vehicle in vehicles:
            html += "<tr>"
            for value in vehicle.values():
                html += f"<td>{value}</td>"
            html += "</tr>"
        
        html += "</tbody></table>"
        return html
    
    def _render_financial_section(self, financial: Dict[str, Any]) -> str:
        """Render financial section as HTML"""
        if not financial:
            return "<p>No financial data available</p>"
        
        revenue = financial.get('revenue', {})
        costs = financial.get('costs', {})
        profit = financial.get('profitability', {})
        
        html = f"""
        <div class="metrics">
            <div class="metric">
                <div class="metric-label">Total Revenue</div>
                <div class="metric-value">{revenue.get('delivered', '$0.00')}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Total Costs</div>
                <div class="metric-value">{costs.get('total', '$0.00')}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Net Profit</div>
                <div class="metric-value">{profit.get('net_profit', '$0.00')}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Profit Margin</div>
                <div class="metric-value">{profit.get('profit_margin', '0.00%')}</div>
            </div>
        </div>
        """
        return html
