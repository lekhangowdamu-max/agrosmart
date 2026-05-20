#!/usr/bin/env python
"""
Comprehensive Flask App Test Suite
Tests all major features of the AgroSmart application
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

def test_route(method, endpoint, expected_status=200, data=None, name=""):
    """Test a single route"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            resp = session.get(url, timeout=5)
        elif method == "POST":
            resp = session.post(url, data=data, timeout=5)
        
        status = "✓" if resp.status_code == expected_status else "✗"
        print(f"{status} {name:40} | {method} {endpoint:30} | Status: {resp.status_code}")
        return resp.status_code == expected_status
    except Exception as e:
        print(f"✗ {name:40} | {method} {endpoint:30} | Error: {str(e)}")
        return False

def main():
    print("\n" + "="*100)
    print("AgroSmart Flask Application Test Suite")
    print("="*100 + "\n")
    
    # Test 1: Home and Public Pages
    print("TEST 1: Home and Public Pages")
    print("-" * 100)
    test_route("GET", "/", name="Home Page")
    test_route("GET", "/dashboard", name="Dashboard (Public)")
    test_route("GET", "/machinery", name="Machinery Page")
    test_route("GET", "/prices", name="Prices Page")
    test_route("GET", "/cctv", name="CCTV Page")
    test_route("GET", "/weather", name="Weather Page")
    test_route("GET", "/map", name="Map Page")
    test_route("GET", "/motor", name="Motor Control Page")
    test_route("GET", "/drone", name="Drone Page")
    
    # Test 2: Authentication Pages
    print("\n\nTEST 2: Authentication Pages")
    print("-" * 100)
    test_route("GET", "/login", name="Login Page")
    test_route("GET", "/register", name="Register Page")
    
    # Test 3: Static Files
    print("\n\nTEST 3: Static Files (Machinery Images)")
    print("-" * 100)
    test_route("GET", "/static/tractor.jpg", name="Tractor Image")
    test_route("GET", "/static/harvester.jpg", name="Harvester Image")
    test_route("GET", "/static/plough.jpg", name="Plough Image")
    test_route("GET", "/static/seeder.jpg", name="Seeder Image")
    test_route("GET", "/static/sprayer.jpg", name="Sprayer Image")
    test_route("GET", "/static/style.css", name="Style Sheet")
    
    # Test 4: API Endpoints (without authentication)
    print("\n\nTEST 4: API Endpoints (Public)")
    print("-" * 100)
    test_route("GET", "/api/machinery", name="Get All Machinery")
    test_route("GET", "/api/prices", name="Get Prices")
    test_route("GET", "/api/prices/states", name="Get States")
    
    # Test 5: Protected Pages (should redirect to login or show error)
    print("\n\nTEST 5: Protected Pages (not authenticated)")
    print("-" * 100)
    test_route("GET", "/bookings", expected_status=302, name="Bookings (redirect to login)")
    test_route("GET", "/profile", expected_status=302, name="Profile (redirect to login)")
    test_route("GET", "/admin", expected_status=302, name="Admin Panel (redirect to login)")
    
    # Test 6: Database Connectivity
    print("\n\nTEST 6: Database Connectivity Check")
    print("-" * 100)
    try:
        from models import db, User, Machinery, Booking
        users = User.query.all()
        machines = Machinery.query.all()
        print(f"✓ Database Connected           | Found {len(users)} users, {len(machines)} machines")
    except Exception as e:
        print(f"✗ Database Connection Failed   | Error: {str(e)}")
    
    print("\n" + "="*100)
    print("Test Suite Complete!")
    print("="*100 + "\n")

if __name__ == "__main__":
    main()
