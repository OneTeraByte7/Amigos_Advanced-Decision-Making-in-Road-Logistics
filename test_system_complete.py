import sys
import requests
import json
import time

print("="*80)
print("  🚀 ADAPTIVE LOGISTICS SYSTEM - COMPLETE TEST")
print("="*80)
print()

API_BASE = "http://localhost:8000"

def test_api_connection():
    """Test if API is running"""
    print("1. Testing API Connection...")
    try:
        response = requests.get(f"{API_BASE}/docs", timeout=5)
        if response.status_code == 200:
            print("   ✅ API is running at", API_BASE)
            return True
        else:
            print("   ❌ API returned status code:", response.status_code)
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to API. Is it running?")
        print("   💡 Start it with: python api.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_initialize():
    """Initialize the system"""
    print("\n2. Initializing Fleet...")
    try:
        response = requests.post(
            f"{API_BASE}/api/initialize",
            json={"num_vehicles": 5, "num_loads": 8},
            timeout=10
        )
        data = response.json()
        print(f"   ✅ Initialized: {data['num_vehicles']} vehicles, {data['num_loads']} loads")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_get_state():
    """Get current state"""
    print("\n3. Getting Fleet State...")
    try:
        response = requests.get(f"{API_BASE}/api/state", timeout=5)
        data = response.json()
        print(f"   ✅ Vehicles: {len(data['vehicles'])}")
        print(f"   ✅ Loads: {len(data['active_loads'])}")
        print(f"   ✅ Active Trips: {len(data['active_trips'])}")
        return data
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_ai_matching():
    """Run AI load matching"""
    print("\n4. Running AI Load Matching...")
    print("   ⏳ This may take 5-10 seconds...")
    try:
        response = requests.post(f"{API_BASE}/api/match-loads", timeout=30)
        data = response.json()
        
        print(f"   ✅ Opportunities Analyzed: {data['opportunities_analyzed']}")
        print(f"   ✅ Matches Created: {data['matches_created']}")
        
        # Check if LLM is working
        reasoning = data.get('llm_reasoning', '')
        if 'LLM Error' in reasoning:
            print(f"\n   ⚠️  LLM Issue: {reasoning[:100]}...")
            print("   💡 Check your GROQ_API_KEY in .env")
            return False
        else:
            print(f"\n   🤖 LLM Reasoning:")
            print("   " + "-"*76)
            # Print first 300 chars of reasoning
            print("   " + reasoning[:300].replace('\n', '\n   '))
            if len(reasoning) > 300:
                print("   ...")
            print("   " + "-"*76)
            return True
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out. LLM may be slow.")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_metrics():
    """Get metrics"""
    print("\n5. Getting Fleet Metrics...")
    try:
        response = requests.get(f"{API_BASE}/api/metrics", timeout=5)
        data = response.json()
        print(f"   ✅ Total Vehicles: {data['total_vehicles']}")
        print(f"   ✅ En-route: {data['en_route_vehicles']}")
        print(f"   ✅ Active Trips: {data['active_trips']}")
        print(f"   ✅ Avg Utilization: {data['average_utilization']:.1%}")
        return data
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_monitoring_cycle():
    """Run monitoring cycles"""
    print("\n6. Running Monitoring Cycles (simulating time)...")
    try:
        for i in range(3):
            response = requests.post(f"{API_BASE}/api/cycle", timeout=5)
            data = response.json()
            print(f"   ✅ Cycle {i+1}: {data['vehicles_count']} vehicles, {data['events_count']} events")
            time.sleep(1)
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_route_management():
    """Test adaptive route management"""
    print("\n7. Testing Adaptive Route Management...")
    print("   ⏳ Running AI route manager...")
    try:
        response = requests.post(f"{API_BASE}/api/manage-routes", timeout=30)
        data = response.json()
        
        print(f"   ✅ Routes Managed: {data['routes_managed']}")
        
        decisions = data.get('decisions', [])
        if decisions:
            print(f"\n   🤖 AI Decisions Made: {len(decisions)}")
            for i, decision in enumerate(decisions[:2], 1):  # Show first 2
                print(f"\n   Decision {i}:")
                print(f"   Vehicle: {decision.get('vehicle_id', 'N/A')}")
                print(f"   Action: {decision.get('decision', 'N/A')}")
                reasoning = decision.get('reasoning', '')
                if reasoning:
                    print(f"   Reasoning: {reasoning[:150]}...")
        else:
            print("   ℹ️  No active routes to manage yet")
            print("   💡 Normal - trucks need to be en-route first")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_vehicles_endpoint():
    """Test vehicles endpoint"""
    print("\n8. Testing Vehicles Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/vehicles", timeout=5)
        vehicles = response.json()
        print(f"   ✅ Retrieved {len(vehicles)} vehicles")
        if vehicles:
            v = vehicles[0]
            print(f"   Example: {v['vehicle_id']} - Status: {v['status']}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_loads_endpoint():
    """Test loads endpoint"""
    print("\n9. Testing Loads Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/loads", timeout=5)
        loads = response.json()
        print(f"   ✅ Retrieved {len(loads)} loads")
        if loads:
            l = loads[0]
            print(f"   Example: {l['load_id']} - Status: {l['status']}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_events_endpoint():
    """Test events endpoint"""
    print("\n10. Testing Events Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/events?limit=10", timeout=5)
        events = response.json()
        print(f"   ✅ Retrieved {len(events)} recent events")
        if events:
            e = events[0]
            print(f"   Latest: {e['event_type']} - {e.get('description', 'N/A')[:50]}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    results = {}
    
    # Test 1: Connection
    results['api_connection'] = test_api_connection()
    if not results['api_connection']:
        print("\n" + "="*80)
        print("❌ FAILED: API is not running")
        print("="*80)
        sys.exit(1)
    
    # Test 2: Initialize
    results['initialize'] = test_initialize()
    time.sleep(1)
    
    # Test 3: Get State
    state = test_get_state()
    results['get_state'] = state is not None
    time.sleep(1)
    
    # Test 4: AI Matching
    results['ai_matching'] = test_ai_matching()
    time.sleep(2)
    
    # Test 5: Metrics
    metrics = test_metrics()
    results['metrics'] = metrics is not None
    time.sleep(1)
    
    # Test 6: Monitoring
    results['monitoring'] = test_monitoring_cycle()
    time.sleep(1)
    
    # Test 7: Route Management
    results['route_management'] = test_route_management()
    time.sleep(1)
    
    # Test 8-10: Additional endpoints
    results['vehicles'] = test_vehicles_endpoint()
    results['loads'] = test_loads_endpoint()
    results['events'] = test_events_endpoint()
    
    # Summary
    print("\n" + "="*80)
    print("  📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name.replace('_', ' ').title()}")
    
    print("\n" + "="*80)
    if passed == total:
        print(f"  🎉 ALL TESTS PASSED ({passed}/{total})")
        print("="*80)
        print("\n  ✅ System is fully operational!")
        print("  ✅ AI agents are working!")
        print("  ✅ All endpoints responding!")
        print("\n  🚀 Ready for demo!")
        print("\n  Next steps:")
        print("  1. Open Thunder Client and test endpoints")
        print("  2. Start frontend: cd frontend && npm run dev")
        print("  3. Open http://localhost:3000")
        print()
        return 0
    else:
        print(f"  ⚠️  {passed}/{total} TESTS PASSED")
        print("="*80)
        print("\n  Some tests failed. Check the errors above.")
        print()
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏸️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
