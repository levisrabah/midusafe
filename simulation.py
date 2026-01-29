import json
import random
import time
import requests
from datetime import datetime
import urllib3

# Disable SSL warnings for localhost
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    """Send incident report to the backend API with retries"""
    url = "http://127.0.0.1:8000/report"
    
    payload = {
        "message": incident["message"],
        "location": incident["location_name"],
        "lat": incident["lat"],
        "lng": incident["lng"]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    payload_size = len(json.dumps(payload))
    
    print(f"[{timestamp}] 📤 Sending: {incident['location_name']} ({payload_size} bytes)")
    
    # Retry with exponential backoff
    for attempt in range(3):
        try:
            start_time = time.time()
            response = requests.post(
                url, 
                json=payload, 
                headers=headers,
                timeout=(3.05, 30),  # (connect, read) timeout
                verify=False
            )
            elapsed = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                result = response.json()
                print(f"[{timestamp}] ✅ Accepted in {elapsed:.1f}ms - ID: {result.get('id', 'unknown')}")
                return True
            else:
                print(f"[{timestamp}] ❌ HTTP {response.status_code}: {response.text[:100]}")
                
        except requests.exceptions.ConnectTimeout:
            print(f"[{timestamp}] ⏱️ Connection timeout (attempt {attempt + 1}/3)")
        except requests.exceptions.ReadTimeout:
            print(f"[{timestamp}] ⏱️ Read timeout (attempt {attempt + 1}/3)")
        except requests.exceptions.RequestException as e:
            print(f"[{timestamp}] ❌ Request error: {str(e)[:100]}")
        
        if attempt < 2:
            backoff = 2 ** attempt
            print(f"[{timestamp}] ⏳ Retrying in {backoff}s...")
            time.sleep(backoff)
    
    print(f"[{timestamp}] 💀 Failed after 3 attempts")
    return False

def main():
    """Main simulation loop"""
    print("🚀 Starting MIDUSAFE Simulation Engine...")
    print("📍 Loading East African climate disaster scenarios...")
    
    # Test health endpoint first
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend health check passed")
        else:
            print(f"❌ Backend health failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot reach backend: {e}")
        return
    
    incidents = load_mock_incidents()
    
    if not incidents:
        print("❌ No incidents loaded. Exiting.")
        return
    
    print(f"✅ Loaded {len(incidents)} incident scenarios")
    print("🔄 Starting simulation loop (sending incident every 5-10 seconds)...")
    print("📡 Target: http://127.0.0.1:8000/report")
    print("-" * 60)
    
    incident_index = 0
    success_count = 0
    
    try:
        while True:
            # Get current incident (cycle through list)
            incident = incidents[incident_index]
            
            # Send the incident report
            if send_incident_report(incident):
                success_count += 1
            
            # Move to next incident (cycle back to start if needed)
            incident_index = (incident_index + 1) % len(incidents)
            
            # Wait 10-15 seconds before next incident (reduced frequency)
            time.sleep(random.uniform(10, 15))
            
    except KeyboardInterrupt:
        print(f"\n🛑 Simulation stopped by user - {success_count} reports sent successfully")
    except Exception as e:
        print(f"❌ Simulation error: {e}")

if __name__ == "__main__":
    main()
