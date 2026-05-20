# API Testing Guide

This guide provides curl commands and examples for testing all AgroSmart Backend API endpoints.

## Setup

Start the server before testing:
```bash
npm run dev
```

## 1. Authentication Endpoints

### Register User

```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Farmer",
    "email": "john@example.com",
    "password": "SecurePass123",
    "role": "farmer",
    "phone": "9999999999",
    "location": "Bangalore"
  }'
```

Response:
```json
{
  "message": "Registration successful",
  "userId": 1
}
```

### Login User

```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

Response:
```json
{
  "message": "Login successful",
  "user": {
    "userId": 1,
    "name": "John Farmer",
    "email": "john@example.com",
    "role": "farmer",
    "location": "Bangalore",
    "photo": null
  }
}
```

### Get Current User

```bash
curl -X GET http://localhost:3000/api/auth/current-user \
  -b cookies.txt
```

Response:
```json
{
  "user": {
    "userId": 1,
    "name": "John Farmer",
    "email": "john@example.com",
    "role": "farmer",
    "location": "Bangalore",
    "photo": null
  }
}
```

### Update Profile

```bash
curl -X POST http://localhost:3000/api/auth/profile \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Updated",
    "email": "john.updated@example.com",
    "phone": "9888888888",
    "location": "Mysore"
  }'
```

Response:
```json
{
  "message": "Profile updated successfully",
  "user": {
    "name": "John Updated",
    "email": "john.updated@example.com",
    "phone": "9888888888",
    "location": "Mysore"
  }
}
```

### Logout

```bash
curl -X POST http://localhost:3000/api/auth/logout \
  -b cookies.txt
```

Response:
```json
{
  "message": "Logged out successfully"
}
```

## 2. Machinery Endpoints

### Get All Machinery

```bash
curl -X GET http://localhost:3000/api/machinery
```

Response:
```json
{
  "machines": [
    {
      "id": 1,
      "name": "Tractor",
      "location": "Bangalore",
      "price_per_day": 500,
      "owner_contact": "9999999997",
      "image_url": "/static/machinery/tractor.jpg",
      "tracking_location": null
    }
  ]
}
```

### Get Machinery by ID

```bash
curl -X GET http://localhost:3000/api/machinery/1
```

Response:
```json
{
  "machine": {
    "id": 1,
    "name": "Tractor",
    "location": "Bangalore",
    "price_per_day": 500,
    "owner_contact": "9999999997",
    "image_url": "/static/machinery/tractor.jpg"
  }
}
```

### Create Machinery (Admin Only)

```bash
curl -X POST http://localhost:3000/api/machinery \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Harvester",
    "location": "Mysore",
    "price_per_day": 800,
    "owner_contact": "9999999996",
    "image_url": "/static/machinery/harvester.jpg"
  }'
```

Response:
```json
{
  "message": "Machinery created successfully",
  "machineId": 2
}
```

## 3. Booking Endpoints

### Create Booking

```bash
curl -X POST http://localhost:3000/api/bookings \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{
    "machineId": 1,
    "startDate": "2024-06-15",
    "endDate": "2024-06-17",
    "notes": "Need tractor for field preparation"
  }'
```

Response:
```json
{
  "message": "Booking request submitted successfully",
  "bookingId": 1,
  "totalCost": 1500
}
```

### Get User Bookings

```bash
curl -X GET http://localhost:3000/api/bookings \
  -b cookies.txt
```

Response:
```json
{
  "bookings": [
    {
      "id": 1,
      "machine_name": "Tractor",
      "machine_image": "/static/machinery/tractor.jpg",
      "machine_location": "Bangalore",
      "start_date": "2024-06-15",
      "end_date": "2024-06-17",
      "total_cost": 1500,
      "status": "pending",
      "notes": "Need tractor for field preparation"
    }
  ]
}
```

### Get Booking Details

```bash
curl -X GET http://localhost:3000/api/bookings/1 \
  -b cookies.txt
```

Response:
```json
{
  "booking": {
    "id": 1,
    "machine_name": "Tractor",
    "machine_location": "Bangalore",
    "user_location": "Mysore",
    "start_date": "2024-06-15",
    "end_date": "2024-06-17",
    "total_cost": 1500,
    "status": "pending"
  }
}
```

### Cancel Booking

```bash
curl -X POST http://localhost:3000/api/bookings/1/cancel \
  -b cookies.txt
```

Response:
```json
{
  "message": "Booking cancelled successfully"
}
```

### Get Booking Tracking

```bash
curl -X GET http://localhost:3000/api/bookings/1/track \
  -b cookies.txt
```

Response:
```json
{
  "booking": {
    "id": 1,
    "machine_name": "Tractor",
    "machine_location": "Bangalore",
    "admin_location": "Belgaum",
    "user_location": "Mysore",
    "admin_phone": "9999999995",
    "admin_vehicle_number": "KA-01-AB-1234",
    "status": "approved"
  }
}
```

## 4. Admin Endpoints

### Get Dashboard Stats

```bash
curl -X GET http://localhost:3000/api/admin/stats \
  -b admin_cookies.txt
```

Response:
```json
{
  "stats": {
    "user_count": 10,
    "machinery_count": 5,
    "price_count": 150,
    "booking_count": 25,
    "pending_bookings": 5,
    "top_machines": [
      {
        "machine_name": "Tractor",
        "booking_count": 8
      }
    ]
  }
}
```

### Get All Bookings

```bash
curl -X GET http://localhost:3000/api/admin/bookings \
  -b admin_cookies.txt
```

Response:
```json
{
  "bookings": [
    {
      "id": 1,
      "machine_name": "Tractor",
      "user_name": "John Farmer",
      "user_email": "john@example.com",
      "user_location": "Bangalore",
      "start_date": "2024-06-15",
      "end_date": "2024-06-17",
      "total_cost": 1500,
      "status": "pending"
    }
  ]
}
```

### Get Pending Bookings

```bash
curl -X GET http://localhost:3000/api/admin/bookings/pending \
  -b admin_cookies.txt
```

### Approve Booking

```bash
curl -X POST http://localhost:3000/api/admin/bookings/1/approve \
  -b admin_cookies.txt \
  -H "Content-Type: application/json" \
  -d '{
    "admin_phone": "9999999995",
    "admin_vehicle_number": "KA-01-AB-1234",
    "admin_location": "Belgaum"
  }'
```

Response:
```json
{
  "message": "Booking approved successfully"
}
```

### Reject Booking

```bash
curl -X POST http://localhost:3000/api/admin/bookings/1/reject \
  -b admin_cookies.txt
```

Response:
```json
{
  "message": "Booking rejected successfully"
}
```

## 5. Prices Endpoints

### Get Crop Prices

```bash
curl -X GET "http://localhost:3000/api/prices?state=Karnataka&district=Bangalore&commodity=Rice"
```

Response:
```json
{
  "prices": [
    {
      "id": 1,
      "state": "Karnataka",
      "district": "Bangalore",
      "market": "Bangalore Market",
      "commodity": "Rice",
      "variety": "Basmati",
      "grade": "A",
      "arrival_date": "2024-01-15",
      "min_price": 2000,
      "max_price": 2500,
      "modal_price": 2200,
      "kannada_name": "ಅಕ್ಕಿ"
    }
  ]
}
```

### Get States

```bash
curl -X GET http://localhost:3000/api/prices/states
```

Response:
```json
{
  "states": ["Karnataka", "Andhra Pradesh", "Tamil Nadu"]
}
```

### Get Districts

```bash
curl -X GET "http://localhost:3000/api/prices/districts?state=Karnataka"
```

Response:
```json
{
  "districts": ["Bangalore", "Mysore", "Belgaum", "Hubli"]
}
```

### Get Commodities

```bash
curl -X GET "http://localhost:3000/api/prices/commodities?district=Bangalore"
```

Response:
```json
{
  "commodities": ["Rice", "Wheat", "Maize", "Sugarcane"]
}
```

### Get Price History

```bash
curl -X GET "http://localhost:3000/api/prices/history?commodity=Rice&district=Bangalore"
```

Response:
```json
{
  "priceHistory": {
    "dates": ["2024-01-10", "2024-01-11", "2024-01-12"],
    "prices": [2150, 2180, 2200]
  }
}
```

## 6. Utilities Endpoints

### Get Map Data

```bash
curl -X GET http://localhost:3000/api/map \
  -b cookies.txt
```

Response:
```json
{
  "user_location": "Bangalore",
  "user_coords": [12.9716, 77.5946]
}
```

### Get Weather

```bash
curl -X GET http://localhost:3000/api/weather
```

### Get Motor Status

```bash
curl -X GET http://localhost:3000/api/motor
```

Response:
```json
{
  "motor": {
    "status": "offline",
    "power": 0,
    "flow": 0,
    "pressure": 0
  }
}
```

### Control Motor (IoT)

```bash
curl -X POST http://localhost:3000/api/motor/control \
  -H "Content-Type: application/json" \
  -d '{
    "action": "on",
    "power": 100
  }'
```

Response:
```json
{
  "status": "success",
  "action": "on",
  "power": 100,
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Get Drone Telemetry

```bash
curl -X GET http://localhost:3000/api/drone/telemetry
```

Response:
```json
{
  "telemetry": {
    "status": "offline",
    "battery": 0,
    "altitude": 0,
    "speed": 0,
    "latitude": 0,
    "longitude": 0
  }
}
```

### Update Drone Telemetry

```bash
curl -X POST http://localhost:3000/api/drone/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "drone_id": "agro-drone-001",
    "status": "flying",
    "battery": 85.5,
    "altitude": 45.2,
    "speed": 12.3,
    "latitude": 12.9716,
    "longitude": 77.5946,
    "heading": 180,
    "signal": 95
  }'
```

### Get Drone Logs

```bash
curl -X GET "http://localhost:3000/api/drone/logs?limit=10"
```

### Add Drone Log

```bash
curl -X POST http://localhost:3000/api/drone/logs \
  -H "Content-Type: application/json" \
  -d '{
    "drone_id": "agro-drone-001",
    "event": "Takeoff initiated",
    "level": "info"
  }'
```

## Testing Tips

### Save Cookies from Login

```bash
# Login and save cookies
curl -c cookies.txt -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"pass123"}'

# Use cookies in subsequent requests
curl -b cookies.txt http://localhost:3000/api/bookings
```

### Pretty Print JSON Response

```bash
curl http://localhost:3000/api/machinery | python -m json.tool
# or
curl http://localhost:3000/api/machinery | jq .
```

### Test with Error Handling

```bash
# Test invalid login
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"invalid@example.com","password":"wrongpass"}'

# Response:
# {"error":"Invalid email or password"}
```

### Time Request

```bash
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:3000/health
```

Create `curl-format.txt`:
```
time_namelookup:  %{time_namelookup}\n
time_connect:     %{time_connect}\n
time_appconnect:  %{time_appconnect}\n
time_pretransfer: %{time_pretransfer}\n
time_redirect:    %{time_redirect}\n
time_starttransfer: %{time_starttransfer}\n
----------
time_total:       %{time_total}\n
```

## Using Postman

Import this as Postman Environment:

```json
{
  "id": "agrosmart-env",
  "name": "AgroSmart Development",
  "values": [
    {
      "key": "base_url",
      "value": "http://localhost:3000",
      "enabled": true
    },
    {
      "key": "user_email",
      "value": "john@example.com",
      "enabled": true
    },
    {
      "key": "user_password",
      "value": "SecurePass123",
      "enabled": true
    }
  ]
}
```

Use in requests:
```
{{base_url}}/api/machinery
```

---

**Happy testing! 🚀**
