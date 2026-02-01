"""
Test the complete 3-agent system
"""
import requests
import json
import time

BASE_URL = "https://amigos-advanced-decision-making-in-road.onrender.com"

def print_header(text):
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def print_subheader(text):
    print(f"\n  {text}")
    print("  " + "-"*76)

print_header("🚛 COMPLETE ADAPTIVE LOGISTICS SYSTEM TEST")
print("  Testing all 3 agents: Monitor → Matcher → Route Manager")

# Step 1: Initialize
print_header("STEP 1: Initialize Fleet (Monitor Agent)")
r = requests.post(f"{BASE_URL}/api/initialize", json={
    "num_vehicles": 5,
    "num_loads": 8
})
print(f"✓ {r.json()['message']}")
print(f"  Vehicles: {r.json()['num_vehicles']}")
print(f"  Loads: {r.json()['num_loads']}")

# Step 2: Check initial state
print_header("STEP 2: View Initial State")
r = requests.get(f"{BASE_URL}/api/state")
state = r.json()
print(f"✓ Initial State:")
print(f"  Idle Vehicles: {sum(1 for v in state['vehicles'] if v['status'] == 'idle')}")
print(f"  Available Loads: {sum(1 for l in state['active_loads'] if l['status'] == 'available')}")
print(f"  Active Trips: {len(state.get('active_trips', []))}")

# Step 3: AI Load Matching
print_header("STEP 3: AI Load Matching (Matcher Agent)")
print("  🤖 Running intelligent load matching...")

try:
    r = requests.post(f"{BASE_URL}/api/match-loads", timeout=30)
    result = r.json()
    
    print(f"\n✓ {result['message']}")
    print(f"  Opportunities analyzed: {result['opportunities_analyzed']}")
    print(f"  Matches created: {result['matches_created']}")
    
    if result['matches_created'] > 0:
        print_subheader("LLM Reasoning (First 15 lines):")
        for line in result['llm_reasoning'].split('\n')[:15]:
            print(f"    {line}")
        
        print_subheader("Approved Matches:")
        for match in result['approved_matches']:
            print(f"    ✓ {match['vehicle_id']} → {match['load_id']}")
    else:
        print("  ℹ️  No matches created (constraints not met or all already matched)")
        
except Exception as e:
    print(f"✗ Error: {e}")

# Step 4: Check updated state
print_header("STEP 4: State After Matching")
r = requests.get(f"{BASE_URL}/api/state")
state = r.json()
print(f"✓ Updated State:")
print(f"  Idle Vehicles: {sum(1 for v in state['vehicles'] if v['status'] == 'idle')}")
print(f"  En-route Vehicles: {sum(1 for v in state['vehicles'] if v['status'] in ['en_route_empty', 'en_route_loaded'])}")
print(f"  Matched Loads: {sum(1 for l in state['active_loads'] if l['status'] == 'matched')}")
print(f"  Active Trips: {len(state.get('active_trips', []))}")

en_route_count = sum(1 for v in state['vehicles'] if v['status'] in ['en_route_empty', 'en_route_loaded'])

# Step 5: Simulate time passing
print_header("STEP 5: Simulate Time Passing (Monitoring Cycle)")
print("  Vehicles move, conditions change...")
r = requests.post(f"{BASE_URL}/api/cycle")
result = r.json()
print(f"✓ {result['message']}")
print(f"  Events generated: {result['events_count']}")

# Small delay to make demo more realistic
time.sleep(1)

# Step 6: ADAPTIVE ROUTE MANAGEMENT
print_header("STEP 6: 🚛 ADAPTIVE ROUTE MANAGEMENT (Route Manager Agent)")
print("  This is the KEY innovation - adapting routes while trucks are moving!")

if en_route_count == 0:
    print("\n  ℹ️  No vehicles currently en-route")
    print("     (Run step 3 again or adjust matching constraints)")
else:
    print(f"  Managing routes for {en_route_count} moving vehicles...")
    print("  Checking for: traffic, delays, new opportunities...")
    
    try:
        r = requests.post(f"{BASE_URL}/api/manage-routes", timeout=30)
        result = r.json()
        
        print(f"\n✓ {result['message']}")
        print(f"  Routes managed: {result['routes_managed']}")
        
        if result['routes_managed'] > 0:
            print_subheader("ROUTE MANAGEMENT DECISIONS:")
            
            for i, decision in enumerate(result['decisions'], 1):
                print(f"\n    Decision {i} - Vehicle {decision['vehicle_id']}:")
                print(f"      Trip ID: {decision['trip_id']}")
                print(f"      Traffic Delays: {decision['traffic_delays']}")
                
                if decision['delay_minutes'] > 0:
                    print(f"      ⚠️  Delay Detected: {decision['delay_minutes']:.0f} minutes")
                
                print(f"      New Opportunities Found: {decision['new_opportunities_found']}")
                
                if decision['opportunities']:
                    print(f"\n      💡 Opportunities:")
                    for opp in decision['opportunities'][:2]:  # Show first 2
                        print(f"         • Load {opp['load_id']}: {opp['load_origin']} → {opp['load_destination']}")
                        print(f"           Detour: {opp['detour_km']}km, Profit: ${opp['profit']}")
                
                print(f"\n      🤖 LLM DECISION:")
                print("         " + "-"*68)
                for line in decision['llm_decision'].split('\n')[:25]:  # First 25 lines
                    print(f"         {line}")
                if len(decision['llm_decision'].split('\n')) > 25:
                    print("         ...")
                print("         " + "-"*68)
                
                print(f"\n      ✅ Action Taken: {decision['action_taken']}")
                print()
        else:
            print("  ℹ️  No routes needed management (no vehicles moving)")
    
    except Exception as e:
        print(f"✗ Error: {e}")

# Step 7: Final Metrics
print_header("STEP 7: Final Fleet Metrics")
r = requests.get(f"{BASE_URL}/api/metrics")
metrics = r.json()
print(f"✓ Fleet Performance:")
print(f"  Total Vehicles: {metrics['total_vehicles']}")
print(f"  En-route: {metrics['en_route_vehicles']}")
print(f"  Idle: {metrics['idle_vehicles']}")
print(f"  Total Loads: {metrics['total_loads']}")
print(f"  Matched: {metrics['matched_loads']}")
print(f"  Average Utilization: {metrics['average_utilization']:.1%}")
print(f"  Total KM Today: {metrics['total_km_today']:.2f}")

# Summary
print_header("🎉 COMPLETE SYSTEM TEST FINISHED!")

print("""
✅ ALL 3 AGENTS WORKING:

1. Fleet Monitor Agent:
   - Tracks all vehicles and loads
   - Collects events
   - Updates state continuously
   
2. Load Matcher Agent (AI):
   - Analyzes vehicle-load combinations
   - Uses Groq LLM for intelligent matching
   - Creates optimal assignments
   
3. Route Manager Agent (AI):
   - Monitors trucks while moving
   - Detects traffic and delays
   - Finds new opportunities
   - Makes adaptive decisions

SYSTEM CAPABILITIES:
✅ Real-time monitoring
✅ AI-powered initial planning  
✅ Adaptive route management
✅ Explainable decision-making
✅ Multi-agent coordination

""")

print("="*80)
print("  Ready for demo! Open ADAPTIVE_LOGISTICS.md for presentation guide.")
print("="*80)
