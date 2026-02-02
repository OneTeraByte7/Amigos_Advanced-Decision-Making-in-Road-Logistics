"""
database.py
───────────
Database models and ORM for persistent storage of fleet data.
Uses SQLite for simplicity with SQLAlchemy ORM.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

Base = declarative_base()


class VehicleDB(Base):
    """Database model for vehicles"""
    __tablename__ = 'vehicles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(String(50), unique=True, nullable=False, index=True)
    plate_number = Column(String(20))
    capacity_tons = Column(Float, nullable=False)
    current_load_tons = Column(Float, default=0.0)
    status = Column(String(20), nullable=False)
    current_lat = Column(Float)
    current_lng = Column(Float)
    current_location_name = Column(String(100))
    fuel_level_percent = Column(Float, default=100.0)
    total_km_today = Column(Float, default=0.0)
    loaded_km_today = Column(Float, default=0.0)
    utilization_rate = Column(Float, default=0.0)
    max_driving_hours_remaining = Column(Float, default=11.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trips = relationship("TripDB", back_populates="vehicle")
    maintenance_records = relationship("MaintenanceRecordDB", back_populates="vehicle")


class LoadDB(Base):
    """Database model for loads"""
    __tablename__ = 'loads'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    load_id = Column(String(50), unique=True, nullable=False, index=True)
    origin_lat = Column(Float, nullable=False)
    origin_lng = Column(Float, nullable=False)
    origin_name = Column(String(100))
    destination_lat = Column(Float, nullable=False)
    destination_lng = Column(Float, nullable=False)
    destination_name = Column(String(100))
    weight_tons = Column(Float, nullable=False)
    distance_km = Column(Float)
    status = Column(String(20), nullable=False)
    total_offered_revenue = Column(Float)
    pickup_deadline = Column(DateTime)
    delivery_deadline = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trips = relationship("TripDB", back_populates="load")


class TripDB(Base):
    """Database model for trips"""
    __tablename__ = 'trips'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    trip_id = Column(String(50), unique=True, nullable=False, index=True)
    vehicle_id = Column(String(50), ForeignKey('vehicles.vehicle_id'), nullable=False)
    load_id = Column(String(50), ForeignKey('loads.load_id'), nullable=False)
    phase = Column(String(20), nullable=False)
    progress_percent = Column(Float, default=0.0)
    route_distance_km = Column(Float)
    route_coordinates = Column(Text)  # JSON string
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vehicle = relationship("VehicleDB", back_populates="trips")
    load = relationship("LoadDB", back_populates="trips")
    events = relationship("EventDB", back_populates="trip")


class EventDB(Base):
    """Database model for events"""
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(50), unique=True, nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    trip_id = Column(String(50), ForeignKey('trips.trip_id'))
    timestamp = Column(DateTime, nullable=False, index=True)
    payload = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    trip = relationship("TripDB", back_populates="events")


class MaintenanceRecordDB(Base):
    """Database model for maintenance records"""
    __tablename__ = 'maintenance_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(String(50), ForeignKey('vehicles.vehicle_id'), nullable=False)
    maintenance_type = Column(String(50), nullable=False)
    description = Column(Text)
    cost = Column(Float)
    performed_at = Column(DateTime, nullable=False)
    next_due_km = Column(Float)
    next_due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    vehicle = relationship("VehicleDB", back_populates="maintenance_records")


class PerformanceMetricDB(Base):
    """Database model for daily performance metrics"""
    __tablename__ = 'performance_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, index=True)
    total_vehicles = Column(Integer)
    active_vehicles = Column(Integer)
    total_loads = Column(Integer)
    delivered_loads = Column(Integer)
    total_revenue = Column(Float)
    total_distance_km = Column(Float)
    avg_utilization = Column(Float)
    avg_fuel_efficiency = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class DatabaseManager:
    """Manager for database operations"""
    
    def __init__(self, db_url: str = "sqlite:///fleet_management.db"):
        """
        Initialize database manager
        
        Args:
            db_url: SQLAlchemy database URL
        """
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        """Get a new database session"""
        return self.Session()
    
    def save_vehicle(self, vehicle_data: Dict[str, Any]) -> VehicleDB:
        """Save or update vehicle in database"""
        session = self.get_session()
        try:
            existing = session.query(VehicleDB).filter_by(
                vehicle_id=vehicle_data['vehicle_id']
            ).first()
            
            if existing:
                for key, value in vehicle_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                vehicle_db = existing
            else:
                vehicle_db = VehicleDB(**vehicle_data)
                session.add(vehicle_db)
            
            session.commit()
            return vehicle_db
        finally:
            session.close()
    
    def save_load(self, load_data: Dict[str, Any]) -> LoadDB:
        """Save or update load in database"""
        session = self.get_session()
        try:
            existing = session.query(LoadDB).filter_by(
                load_id=load_data['load_id']
            ).first()
            
            if existing:
                for key, value in load_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                load_db = existing
            else:
                load_db = LoadDB(**load_data)
                session.add(load_db)
            
            session.commit()
            return load_db
        finally:
            session.close()
    
    def save_trip(self, trip_data: Dict[str, Any]) -> TripDB:
        """Save or update trip in database"""
        session = self.get_session()
        try:
            # Convert route_coordinates to JSON string if present
            if 'route_coordinates' in trip_data and trip_data['route_coordinates']:
                trip_data['route_coordinates'] = json.dumps(trip_data['route_coordinates'])
            
            existing = session.query(TripDB).filter_by(
                trip_id=trip_data['trip_id']
            ).first()
            
            if existing:
                for key, value in trip_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                trip_db = existing
            else:
                trip_db = TripDB(**trip_data)
                session.add(trip_db)
            
            session.commit()
            return trip_db
        finally:
            session.close()
    
    def save_event(self, event_data: Dict[str, Any]) -> EventDB:
        """Save event in database"""
        session = self.get_session()
        try:
            # Convert payload to JSON string
            if 'payload' in event_data and event_data['payload']:
                event_data['payload'] = json.dumps(event_data['payload'])
            
            # Convert timestamp to datetime if it's a float
            if 'timestamp' in event_data and isinstance(event_data['timestamp'], float):
                event_data['timestamp'] = datetime.fromtimestamp(event_data['timestamp'])
            
            event_db = EventDB(**event_data)
            session.add(event_db)
            session.commit()
            return event_db
        finally:
            session.close()
    
    def save_maintenance_record(
        self,
        maintenance_data: Dict[str, Any]
    ) -> MaintenanceRecordDB:
        """Save maintenance record in database"""
        session = self.get_session()
        try:
            record = MaintenanceRecordDB(**maintenance_data)
            session.add(record)
            session.commit()
            return record
        finally:
            session.close()
    
    def save_daily_metrics(
        self,
        metrics_data: Dict[str, Any]
    ) -> PerformanceMetricDB:
        """Save daily performance metrics"""
        session = self.get_session()
        try:
            metrics = PerformanceMetricDB(**metrics_data)
            session.add(metrics)
            session.commit()
            return metrics
        finally:
            session.close()
    
    def get_vehicle(self, vehicle_id: str) -> Optional[VehicleDB]:
        """Get vehicle by ID"""
        session = self.get_session()
        try:
            return session.query(VehicleDB).filter_by(vehicle_id=vehicle_id).first()
        finally:
            session.close()
    
    def get_all_vehicles(self, status: Optional[str] = None) -> List[VehicleDB]:
        """Get all vehicles, optionally filtered by status"""
        session = self.get_session()
        try:
            query = session.query(VehicleDB)
            if status:
                query = query.filter_by(status=status)
            return query.all()
        finally:
            session.close()
    
    def get_load(self, load_id: str) -> Optional[LoadDB]:
        """Get load by ID"""
        session = self.get_session()
        try:
            return session.query(LoadDB).filter_by(load_id=load_id).first()
        finally:
            session.close()
    
    def get_all_loads(self, status: Optional[str] = None) -> List[LoadDB]:
        """Get all loads, optionally filtered by status"""
        session = self.get_session()
        try:
            query = session.query(LoadDB)
            if status:
                query = query.filter_by(status=status)
            return query.all()
        finally:
            session.close()
    
    def get_active_trips(self) -> List[TripDB]:
        """Get all active trips"""
        session = self.get_session()
        try:
            return session.query(TripDB).filter(
                TripDB.completed_at.is_(None)
            ).all()
        finally:
            session.close()
    
    def get_events(
        self,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[EventDB]:
        """Get recent events"""
        session = self.get_session()
        try:
            query = session.query(EventDB).order_by(EventDB.timestamp.desc())
            if event_type:
                query = query.filter_by(event_type=event_type)
            return query.limit(limit).all()
        finally:
            session.close()
    
    def get_vehicle_maintenance_history(
        self,
        vehicle_id: str
    ) -> List[MaintenanceRecordDB]:
        """Get maintenance history for a vehicle"""
        session = self.get_session()
        try:
            return session.query(MaintenanceRecordDB).filter_by(
                vehicle_id=vehicle_id
            ).order_by(MaintenanceRecordDB.performed_at.desc()).all()
        finally:
            session.close()
    
    def get_performance_metrics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[PerformanceMetricDB]:
        """Get performance metrics for date range"""
        session = self.get_session()
        try:
            return session.query(PerformanceMetricDB).filter(
                PerformanceMetricDB.date >= start_date,
                PerformanceMetricDB.date <= end_date
            ).order_by(PerformanceMetricDB.date).all()
        finally:
            session.close()
    
    def cleanup_old_events(self, days_to_keep: int = 30):
        """Delete events older than specified days"""
        session = self.get_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            deleted = session.query(EventDB).filter(
                EventDB.timestamp < cutoff_date
            ).delete()
            session.commit()
            return deleted
        finally:
            session.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        session = self.get_session()
        try:
            return {
                'total_vehicles': session.query(VehicleDB).count(),
                'total_loads': session.query(LoadDB).count(),
                'total_trips': session.query(TripDB).count(),
                'total_events': session.query(EventDB).count(),
                'active_trips': session.query(TripDB).filter(
                    TripDB.completed_at.is_(None)
                ).count()
            }
        finally:
            session.close()


from datetime import timedelta

# Export all models
__all__ = [
    'VehicleDB',
    'LoadDB',
    'TripDB',
    'EventDB',
    'MaintenanceRecordDB',
    'PerformanceMetricDB',
    'DatabaseManager',
    'Base'
]
