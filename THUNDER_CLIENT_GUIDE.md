# Fleet Monitoring API - Thunder Client Guide

Complete API testing guide with JSON bodies for Thunder Client / Postman

---

## 🚀 Base URL
```
http://localhost:8000
```

---

## 📋 API Endpoints for Thunder Client

### 1. Check API Status
**Method:** `GET`  
**URL:** `http://localhost:8000/`  
**Body:** None

**Expected Response:**
```json
{
  "service": "Fleet Monitoring API",
  "version": "1.0.0",
  "status": "running",
  "initialized": false
}
```

---

### 2. Initialize Fleet ⚡
**Method:** `POST`  
**URL:** `http://localhost:8000/api/initialize`  
**Headers:** `Content-Type: application/json`

**Request Body:**
```json
{
  "num_vehicles": 5,
  "num_loads": 8
}
```

**Expected Response:**
```json
{
  "message": "Fleet monitoring system initialized successfully",
  "num_vehicles": 5,
  "num_loads": 8
}
```

---

### 3. Get Fleet State
**Method:** `GET`  
**URL:** `http://localhost:8000/api/state`  
**Body:** None

**Expected Response:**
```json
{
  "snapshot_at": 1738328526.123,
  "vehicles": [
    {
      "vehicle_id": "v1",
      "driver_id": "driver1",
      "status": "idle",
      "current_location": {
        "lat": 28.6139,
        "lng": 77.209,
        "name": "Delhi"
      },
      "capacity_tons": 20.0,
      "current_load_tons": 0.0,
      "fuel_level_percent": 85.0,
      "last_updated_at": 1738328526.123,
      "total_km_today": 0.0,
      "loaded_km_today": 0.0,
      "idle_minutes_today": 0.0,
      "max_driving_hours_remaining": 10.0,
      "home_depot": null
    }
  ],
  "active_loads": [
    {
      "load_id": "l1",
      "status": "available",
      "origin": {
        "lat": 28.6139,
        "lng": 77.209,
        "name": "Delhi"
      },
      "destination": {
        "lat": 19.076,
        "lng": 72.8777,
        "name": "Mumbai"
      },
      "weight_tons": 15.0,
      "pickup_window_start": 1738328526.123,
      "pickup_window_end": 1738414926.123,
      "delivery_deadline": 1738501326.123,
      "offered_rate_per_km": 25.5,
      "distance_km": 1400.0,
      "assigned_vehicle_id": null,
      "created_at": 1738328526.123
    }
  ],
  "active_trips": [],
  "recent_events": []
}
```

---

### 4. Run Monitoring Cycle ⚡
**Method:** `POST`  
**URL:** `http://localhost:8000/api/cycle`  
**Body:** None

**Expected Response:**
```json
{
  "message": "Monitoring cycle completed",
  "snapshot_at": 1738328526.456,
  "vehicles_count": 5,
  "available_loads_count": 8,
  "events_count": 3
}
```

---

### 5. **Run Intelligent Load Matching** 🤖 (NEW - Uses Groq AI!)
**Method:** `POST`  
**URL:** `http://localhost:8000/api/match-loads`  
**Body:** None

**This uses Groq LLM to intelligently match vehicles with loads!**

**Expected Response:**
```json
{
  "message": "Intelligent load matching completed",
  "opportunities_analyzed": 15,
  "matches_created": 3,
  "llm_reasoning": "APPROVED MATCHES:\n- Vehicle v1 → Load l3: High profit margin (18%) with excellent utilization (87%). Pickup distance is minimal.\n- Vehicle v2 → Load l5: Strategic positioning for future Delhi loads. Good profit (15%).\n\nREASONING:\nPrioritized matches with profit margins above 12% target...",
  "approved_matches": [
    {"vehicle_id": "v1", "load_id": "l3"},
    {"vehicle_id": "v2", "load_id": "l5"}
  ]
}
```

---

### 6. Get All Vehicles
**Method:** `GET`  
**URL:** `http://localhost:8000/api/vehicles`  
**Body:** None

**Expected Response:**
```json
[
  {
    "vehicle_id": "v1",
    "driver_id": "driver1",
    "status": "idle",
    "current_location": {
      "lat": 28.6139,
      "lng": 77.209,
      "name": "Delhi"
    },
    "capacity_tons": 20.0,
    "current_load_tons": 0.0,
    "fuel_level_percent": 85.0,
    "last_updated_at": 1738328526.123,
    "total_km_today": 0.0,
    "loaded_km_today": 0.0,
    "idle_minutes_today": 0.0,
    "max_driving_hours_remaining": 10.0,
    "home_depot": null
  }
]
```

---

### 6. Get Vehicles by Status (Filter)
**Method:** `GET`  
**URL:** `http://localhost:8000/api/vehicles?status=idle`  
**Body:** None

**Available Status Values:**
- `idle`
- `en_route_loaded`
- `en_route_empty`
- `at_pickup`
- `at_delivery`
- `maintenance`
- `offline`

---

### 7. Get Specific Vehicle
**Method:** `GET`  
**URL:** `http://localhost:8000/api/vehicles/v1`  
**Body:** None

Replace `v1` with actual vehicle ID

---

### 8. Get All Loads
**Method:** `GET`  
**URL:** `http://localhost:8000/api/loads`  
**Body:** None

**Expected Response:**
```json
[
  {
    "load_id": "l1",
    "status": "available",
    "origin": {
      "lat": 28.6139,
      "lng": 77.209,
      "name": "Delhi"
    },
    "destination": {
      "lat": 19.076,
      "lng": 72.8777,
      "name": "Mumbai"
    },
    "weight_tons": 15.0,
    "pickup_window_start": 1738328526.123,
    "pickup_window_end": 1738414926.123,
    "delivery_deadline": 1738501326.123,
    "offered_rate_per_km": 25.5,
    "distance_km": 1400.0,
    "assigned_vehicle_id": null,
    "created_at": 1738328526.123
  }
]
```

---

### 9. Get Loads by Status (Filter)
**Method:** `GET`  
**URL:** `http://localhost:8000/api/loads?status=available`  
**Body:** None

**Available Status Values:**
- `available`
- `matched`
- `in_transit`
- `delivered`
- `cancelled`
- `expired`

---

### 10. Get Specific Load
**Method:** `GET`  
**URL:** `http://localhost:8000/api/loads/l1`  
**Body:** None

Replace `l1` with actual load ID

---

### 11. Get Recent Events
**Method:** `GET`  
**URL:** `http://localhost:8000/api/events?limit=20`  
**Body:** None

**Query Parameters:**
- `limit` (optional): Number of events (default: 50, max: 500)
- `event_type` (optional): Filter by event type

**Expected Response:**
```json
[
  {
    "event_id": "evt123abc",
    "event_type": "vehicle_position_update",
    "timestamp": 1738328526.789,
    "payload": {
      "vehicle_id": "v1",
      "lat": 28.65,
      "lng": 77.25
    }
  }
]
```

---

### 12. Get Events by Type (Filter)
**Method:** `GET`  
**URL:** `http://localhost:8000/api/events?event_type=vehicle_position_update&limit=10`  
**Body:** None

**Available Event Types:**
- `vehicle_position_update`
- `load_posted`
- `load_cancelled`
- `traffic_alert`
- `fuel_price_change`
- `delivery_delay`
- `vehicle_idle_timeout`
- `trip_completed`

---

### 13. Get Fleet Metrics ⚡
**Method:** `GET`  
**URL:** `http://localhost:8000/api/metrics`  
**Body:** None

**Expected Response:**
```json
{
  "total_vehicles": 5,
  "available_vehicles": 3,
  "idle_vehicles": 2,
  "en_route_vehicles": 1,
  "total_loads": 8,
  "available_loads": 6,
  "matched_loads": 1,
  "in_transit_loads": 1,
  "average_utilization": 0.65,
  "total_km_today": 450.5
}
```

---

## 🎯 Testing Workflow for Judges

### Step 1: Start Server
```bash
python api.py
```
Server will run on: `http://localhost:8000`

### Step 2: Test in Thunder Client

#### **Request 1 - Check Status**
```
GET http://localhost:8000/
```

#### **Request 2 - Initialize System**
```
POST http://localhost:8000/api/initialize
Content-Type: application/json

{
  "num_vehicles": 5,
  "num_loads": 8
}
```

#### **Request 3 - Get Current State**
```
GET http://localhost:8000/api/state
```

#### **Request 4 - Run Monitoring Cycle**
```
POST http://localhost:8000/api/cycle
```

#### **Request 5 - Get Metrics**
```
GET http://localhost:8000/api/metrics
```

#### **Request 6 - Get Available Vehicles**
```
GET http://localhost:8000/api/vehicles?status=idle
```

#### **Request 7 - Get Available Loads**
```
GET http://localhost:8000/api/loads?status=available
```

#### **Request 8 - Get Events**
```
GET http://localhost:8000/api/events?limit=10
```

---

## 📊 Sample Demo Flow

### 1. Initialize
**POST** `http://localhost:8000/api/initialize`
```json
{
  "num_vehicles": 10,
  "num_loads": 15
}
```

### 2. View Fleet
**GET** `http://localhost:8000/api/state`

### 3. Check Metrics
**GET** `http://localhost:8000/api/metrics`

### 4. Run Cycle (Simulate Time)
**POST** `http://localhost:8000/api/cycle`

### 5. Check Updated Metrics
**GET** `http://localhost:8000/api/metrics`

### 6. View Idle Vehicles
**GET** `http://localhost:8000/api/vehicles?status=idle`

### 7. View Available Loads
**GET** `http://localhost:8000/api/loads?status=available`

---

## 🎨 Thunder Client Collection Import

Copy this JSON to import all requests into Thunder Client:

```json
{
  "clientName": "Thunder Client",
  "collectionName": "Fleet Monitoring API",
  "collectionId": "fleet-monitor-api",
  "dateExported": "2026-01-31",
  "version": "1.0",
  "folders": [],
  "requests": [
    {
      "name": "1. Check API Status",
      "method": "GET",
      "url": "http://localhost:8000/",
      "headers": []
    },
    {
      "name": "2. Initialize Fleet",
      "method": "POST",
      "url": "http://localhost:8000/api/initialize",
      "headers": [
        {
          "name": "Content-Type",
          "value": "application/json"
        }
      ],
      "body": {
        "type": "json",
        "raw": "{\n  \"num_vehicles\": 5,\n  \"num_loads\": 8\n}"
      }
    },
    {
      "name": "3. Get Fleet State",
      "method": "GET",
      "url": "http://localhost:8000/api/state",
      "headers": []
    },
    {
      "name": "4. Run Monitoring Cycle",
      "method": "POST",
      "url": "http://localhost:8000/api/cycle",
      "headers": []
    },
    {
      "name": "5. Get All Vehicles",
      "method": "GET",
      "url": "http://localhost:8000/api/vehicles",
      "headers": []
    },
    {
      "name": "6. Get Idle Vehicles",
      "method": "GET",
      "url": "http://localhost:8000/api/vehicles?status=idle",
      "headers": []
    },
    {
      "name": "7. Get Specific Vehicle",
      "method": "GET",
      "url": "http://localhost:8000/api/vehicles/v1",
      "headers": []
    },
    {
      "name": "8. Get All Loads",
      "method": "GET",
      "url": "http://localhost:8000/api/loads",
      "headers": []
    },
    {
      "name": "9. Get Available Loads",
      "method": "GET",
      "url": "http://localhost:8000/api/loads?status=available",
      "headers": []
    },
    {
      "name": "10. Get Specific Load",
      "method": "GET",
      "url": "http://localhost:8000/api/loads/l1",
      "headers": []
    },
    {
      "name": "11. Get Recent Events",
      "method": "GET",
      "url": "http://localhost:8000/api/events?limit=20",
      "headers": []
    },
    {
      "name": "12. Get Fleet Metrics",
      "method": "GET",
      "url": "http://localhost:8000/api/metrics",
      "headers": []
    }
  ]
}
```

---

## ⚡ Quick Copy-Paste for Thunder Client

### Initialize (POST)
```
URL: http://localhost:8000/api/initialize
Method: POST
Body (JSON):
{
  "num_vehicles": 5,
  "num_loads": 8
}
```

### Get State (GET)
```
URL: http://localhost:8000/api/state
Method: GET
```

### Run Cycle (POST)
```
URL: http://localhost:8000/api/cycle
Method: POST
```

### Get Metrics (GET)
```
URL: http://localhost:8000/api/metrics
Method: GET
```

### Get Vehicles (GET)
```
URL: http://localhost:8000/api/vehicles
Method: GET
```

### Get Loads (GET)
```
URL: http://localhost:8000/api/loads
Method: GET
```

---

## 🌐 Live API Documentation

When server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Both provide interactive testing interfaces!

---

## 📝 Notes for Judges

1. **Start the server first:** `python api.py`
2. **Base URL:** All requests go to `http://localhost:8000`
3. **First request must be:** Initialize endpoint to set up the system
4. **All responses are JSON format**
5. **CORS is enabled** - works from any client
6. **Interactive docs available** at `/docs` endpoint
