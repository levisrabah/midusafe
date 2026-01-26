import json
import random
import time
import requests
from datetime import datetime

def load_mock_incidents():
    """Load mock incidents from JSON file"""
    try:
        with open('data/mock-incidents.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: data/mock-incidents.json not found")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid JSON in data/mock-incidents.json")
        return []

def send_incident_report(incident):
    """Send incident report to the backend API"""
    url = "http://localhost:8000/report"
    
    payload = {
        "message": incident["message"],
        "location": incident["location_name"],
        "lat": incident["lat"],
        "lng": incident["lng"]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] ✅ Sent: {incident['location_name']} - {incident['message'][:50]}...")
        else:
            print(f"❌ Failed to send report: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")

def main():
    """Main simulation loop"""
    print("🚀 Starting MIDUSAFE Simulation Engine...")
    print("📍 Loading East African climate disaster scenarios...")
    
    incidents = load_mock_incidents()
    
    if not incidents:
        print("❌ No incidents loaded. Exiting.")
        return
    
    print(f"✅ Loaded {len(incidents)} incident scenarios")
    print("🔄 Starting simulation loop (sending incident every 5 seconds)...")
    print("📡 Target: http://localhost:8000/report")
    print("-" * 60)
    
    incident_index = 0
    
    try:
        while True:
            # Get current incident (cycle through list)
            incident = incidents[incident_index]
            
            # Send the incident report
            send_incident_report(incident)
            
            # Move to next incident (cycle back to start if needed)
            incident_index = (incident_index + 1) % len(incidents)
            
            # Wait 5 seconds before next incident
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n🛑 Simulation stopped by user")
    except Exception as e:
        print(f"❌ Simulation error: {e}")

if __name__ == "__main__":
    main()
