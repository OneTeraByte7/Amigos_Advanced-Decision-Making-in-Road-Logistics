"""
notification_system.py
──────────────────────
Notification and alerting system for fleet management.
Sends alerts for critical events, delays, and maintenance needs.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertType(Enum):
    """Types of alerts"""
    VEHICLE_BREAKDOWN = "vehicle_breakdown"
    DELIVERY_DELAY = "delivery_delay"
    FUEL_LOW = "fuel_low"
    MAINTENANCE_DUE = "maintenance_due"
    DRIVER_HOURS_EXCEEDED = "driver_hours_exceeded"
    LOAD_TIMEOUT = "load_timeout"
    ROUTE_DEVIATION = "route_deviation"
    WEATHER_ALERT = "weather_alert"
    TRAFFIC_CONGESTION = "traffic_congestion"
    REVENUE_OPPORTUNITY = "revenue_opportunity"


@dataclass
class Alert:
    """Alert message"""
    alert_id: str
    alert_type: AlertType
    level: AlertLevel
    title: str
    message: str
    timestamp: datetime
    vehicle_id: Optional[str] = None
    load_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None


class NotificationChannel:
    """Base class for notification channels"""
    
    def send(self, alert: Alert) -> bool:
        """Send alert through this channel"""
        raise NotImplementedError


class ConsoleChannel(NotificationChannel):
    """Console/log notification channel"""
    
    def send(self, alert: Alert) -> bool:
        """Print alert to console"""
        icon = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.CRITICAL: "🚨",
            AlertLevel.EMERGENCY: "🆘"
        }.get(alert.level, "📢")
        
        print(f"\n{icon} [{alert.level.value.upper()}] {alert.title}")
        print(f"   {alert.message}")
        if alert.vehicle_id:
            print(f"   Vehicle: {alert.vehicle_id}")
        if alert.load_id:
            print(f"   Load: {alert.load_id}")
        print(f"   Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        return True


class EmailChannel(NotificationChannel):
    """Email notification channel (simulated)"""
    
    def __init__(self, recipients: List[str]):
        self.recipients = recipients
    
    def send(self, alert: Alert) -> bool:
        """Simulate sending email"""
        print(f"📧 Email sent to {', '.join(self.recipients)}")
        print(f"   Subject: {alert.title}")
        print(f"   Level: {alert.level.value}")
        return True


class SMSChannel(NotificationChannel):
    """SMS notification channel (simulated)"""
    
    def __init__(self, phone_numbers: List[str]):
        self.phone_numbers = phone_numbers
    
    def send(self, alert: Alert) -> bool:
        """Simulate sending SMS"""
        print(f"📱 SMS sent to {', '.join(self.phone_numbers)}")
        print(f"   {alert.title}: {alert.message}")
        return True


class WebhookChannel(NotificationChannel):
    """Webhook notification channel (simulated)"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send(self, alert: Alert) -> bool:
        """Simulate webhook call"""
        payload = {
            'alert_id': alert.alert_id,
            'type': alert.alert_type.value,
            'level': alert.level.value,
            'title': alert.title,
            'message': alert.message,
            'timestamp': alert.timestamp.isoformat(),
            'vehicle_id': alert.vehicle_id,
            'load_id': alert.load_id,
            'metadata': alert.metadata
        }
        print(f"🔗 Webhook called: {self.webhook_url}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        return True


class NotificationSystem:
    """
    Central notification system for managing alerts and notifications
    """
    
    def __init__(self):
        self.channels: List[NotificationChannel] = []
        self.alert_history: List[Alert] = []
        self.alert_rules: Dict[AlertType, List[Callable]] = {}
        
        # Add default console channel
        self.add_channel(ConsoleChannel())
    
    def add_channel(self, channel: NotificationChannel):
        """Add a notification channel"""
        self.channels.append(channel)
    
    def send_alert(
        self,
        alert_type: AlertType,
        level: AlertLevel,
        title: str,
        message: str,
        vehicle_id: Optional[str] = None,
        load_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Alert:
        """
        Send an alert through all channels
        
        Args:
            alert_type: Type of alert
            level: Severity level
            title: Alert title
            message: Alert message
            vehicle_id: Optional vehicle ID
            load_id: Optional load ID
            metadata: Additional data
        
        Returns:
            Created Alert object
        """
        import uuid
        
        alert = Alert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            alert_type=alert_type,
            level=level,
            title=title,
            message=message,
            timestamp=datetime.now(),
            vehicle_id=vehicle_id,
            load_id=load_id,
            metadata=metadata or {}
        )
        
        # Send through all channels
        for channel in self.channels:
            try:
                channel.send(alert)
            except Exception as e:
                print(f"Failed to send alert through {channel.__class__.__name__}: {e}")
        
        # Store in history
        self.alert_history.append(alert)
        
        # Keep only last 1000 alerts
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
        
        return alert
    
    def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str
    ) -> bool:
        """
        Mark alert as acknowledged
        
        Args:
            alert_id: Alert ID
            acknowledged_by: User who acknowledged
        
        Returns:
            True if alert found and acknowledged
        """
        for alert in self.alert_history:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_at = datetime.now()
                alert.acknowledged_by = acknowledged_by
                return True
        return False
    
    def get_active_alerts(
        self,
        level: Optional[AlertLevel] = None,
        alert_type: Optional[AlertType] = None
    ) -> List[Alert]:
        """
        Get unacknowledged alerts
        
        Args:
            level: Filter by severity level
            alert_type: Filter by alert type
        
        Returns:
            List of active alerts
        """
        alerts = [a for a in self.alert_history if not a.acknowledged]
        
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        if alert_type:
            alerts = [a for a in alerts if a.alert_type == alert_type]
        
        return alerts
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        total_alerts = len(self.alert_history)
        active_alerts = len([a for a in self.alert_history if not a.acknowledged])
        
        # Count by level
        by_level = {}
        for level in AlertLevel:
            count = len([a for a in self.alert_history if a.level == level])
            by_level[level.value] = count
        
        # Count by type
        by_type = {}
        for alert_type in AlertType:
            count = len([a for a in self.alert_history if a.alert_type == alert_type])
            by_type[alert_type.value] = count
        
        return {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'acknowledged_alerts': total_alerts - active_alerts,
            'by_level': by_level,
            'by_type': by_type
        }


class AlertMonitor:
    """
    Monitor fleet conditions and generate alerts
    """
    
    def __init__(self, notification_system: NotificationSystem):
        self.notification_system = notification_system
    
    def check_vehicle_fuel(self, vehicles: List[Dict[str, Any]]):
        """Check for low fuel alerts"""
        for vehicle in vehicles:
            fuel_level = vehicle.get('fuel_level_percent', 100)
            vehicle_id = vehicle.get('vehicle_id')
            
            if fuel_level < 15:
                self.notification_system.send_alert(
                    alert_type=AlertType.FUEL_LOW,
                    level=AlertLevel.CRITICAL,
                    title=f"Critical Fuel Level: {vehicle_id}",
                    message=f"Vehicle {vehicle_id} has only {fuel_level:.1f}% fuel remaining. Immediate refueling required.",
                    vehicle_id=vehicle_id,
                    metadata={'fuel_percent': fuel_level}
                )
            elif fuel_level < 25:
                self.notification_system.send_alert(
                    alert_type=AlertType.FUEL_LOW,
                    level=AlertLevel.WARNING,
                    title=f"Low Fuel Warning: {vehicle_id}",
                    message=f"Vehicle {vehicle_id} has {fuel_level:.1f}% fuel remaining. Plan refueling stop.",
                    vehicle_id=vehicle_id,
                    metadata={'fuel_percent': fuel_level}
                )
    
    def check_driver_hours(self, vehicles: List[Dict[str, Any]]):
        """Check for driver hours violations"""
        for vehicle in vehicles:
            hours_remaining = vehicle.get('max_driving_hours_remaining', 11)
            vehicle_id = vehicle.get('vehicle_id')
            
            if hours_remaining < 1:
                self.notification_system.send_alert(
                    alert_type=AlertType.DRIVER_HOURS_EXCEEDED,
                    level=AlertLevel.CRITICAL,
                    title=f"Driver Hours Critical: {vehicle_id}",
                    message=f"Driver for {vehicle_id} has exceeded maximum driving hours. Mandatory rest required.",
                    vehicle_id=vehicle_id,
                    metadata={'hours_remaining': hours_remaining}
                )
            elif hours_remaining < 2:
                self.notification_system.send_alert(
                    alert_type=AlertType.DRIVER_HOURS_EXCEEDED,
                    level=AlertLevel.WARNING,
                    title=f"Driver Hours Warning: {vehicle_id}",
                    message=f"Driver for {vehicle_id} has {hours_remaining:.1f} hours remaining. Plan rest break.",
                    vehicle_id=vehicle_id,
                    metadata={'hours_remaining': hours_remaining}
                )
    
    def check_maintenance_due(self, vehicles: List[Dict[str, Any]]):
        """Check for maintenance alerts"""
        for vehicle in vehicles:
            total_km = vehicle.get('total_km_today', 0)
            vehicle_id = vehicle.get('vehicle_id')
            
            # Check if approaching maintenance interval (10,000 km)
            km_to_maintenance = 10000 - (total_km % 10000)
            
            if km_to_maintenance < 500:
                self.notification_system.send_alert(
                    alert_type=AlertType.MAINTENANCE_DUE,
                    level=AlertLevel.WARNING,
                    title=f"Maintenance Due Soon: {vehicle_id}",
                    message=f"Vehicle {vehicle_id} needs maintenance in {km_to_maintenance:.0f} km.",
                    vehicle_id=vehicle_id,
                    metadata={'km_to_maintenance': km_to_maintenance}
                )
    
    def check_delivery_delays(
        self,
        trips: List[Dict[str, Any]],
        threshold_hours: float = 2.0
    ):
        """Check for delayed deliveries"""
        current_time = datetime.now()
        
        for trip in trips:
            # Simplified delay check
            trip_id = trip.get('trip_id')
            vehicle_id = trip.get('vehicle_id')
            load_id = trip.get('load_id')
            
            # In a real system, compare against scheduled delivery time
            # For now, just check trip progress
            progress = trip.get('progress_percent', 0)
            
            if progress < 50 and progress > 0:  # Simulate delay detection
                self.notification_system.send_alert(
                    alert_type=AlertType.DELIVERY_DELAY,
                    level=AlertLevel.WARNING,
                    title=f"Potential Delivery Delay: {trip_id}",
                    message=f"Trip {trip_id} may be delayed. Current progress: {progress:.0f}%",
                    vehicle_id=vehicle_id,
                    load_id=load_id,
                    metadata={'progress': progress}
                )
    
    def check_unmatched_loads(
        self,
        loads: List[Dict[str, Any]],
        threshold_count: int = 10
    ):
        """Check for too many unmatched loads"""
        available_loads = [l for l in loads if l.get('status') == 'available']
        
        if len(available_loads) >= threshold_count:
            self.notification_system.send_alert(
                alert_type=AlertType.LOAD_TIMEOUT,
                level=AlertLevel.WARNING,
                title="High Unmatched Load Count",
                message=f"{len(available_loads)} loads are awaiting assignment. Consider increasing fleet capacity or adjusting pricing.",
                metadata={'unmatched_count': len(available_loads)}
            )
    
    def monitor_fleet(self, fleet_data: Dict[str, Any]):
        """
        Comprehensive fleet monitoring
        
        Args:
            fleet_data: Current fleet state data
        """
        vehicles = fleet_data.get('vehicles', [])
        loads = fleet_data.get('loads', [])
        trips = fleet_data.get('trips', [])
        
        # Run all checks
        self.check_vehicle_fuel(vehicles)
        self.check_driver_hours(vehicles)
        self.check_maintenance_due(vehicles)
        self.check_delivery_delays(trips)
        self.check_unmatched_loads(loads)


# Global notification system instance
notification_system = NotificationSystem()
alert_monitor = AlertMonitor(notification_system)


__all__ = [
    'AlertLevel',
    'AlertType',
    'Alert',
    'NotificationChannel',
    'ConsoleChannel',
    'EmailChannel',
    'SMSChannel',
    'WebhookChannel',
    'NotificationSystem',
    'AlertMonitor',
    'notification_system',
    'alert_monitor'
]
