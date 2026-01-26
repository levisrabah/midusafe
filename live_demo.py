import asyncio
import requests
import time
import random

# Sample disaster scenarios for realistic testing
DISASTER_SCENARIOS = [
    "Massive wildfire spreading rapidly in residential area",
    "Flash flooding detected near main highway",
    "Building collapse reported in downtown district",
    "Chemical spill at industrial facility",
    "Tornado spotted near shopping center",
    "Earthquake tremors felt across the city",
    "Gas leak explosion in apartment complex",
    "Bridge collapse on major interstate",
    "Power substation fire affecting thousands",
    "Dam breach warning issued downstream",
    "Multi-vehicle pileup on highway",
    "Structural fire in high-rise building",
    "Landslide blocking mountain pass",
    "Coastal flooding from storm surge",
    "Airport emergency landing required"
]

def generate_disaster_report():
    """Generate a realistic disaster report"""
    scenario = random.choice(DISASTER_SCENARIOS)
    urgency = random.randint(6, 10)  # High urgency for demo
    return {
        "message": scenario,
        "urgency": urgency
    }

async def send_continuous_alerts():
    """Send continuous alerts to demonstrate live updates"""
    print("🚀 Starting live disaster simulation...")
    print("📡 Sending alerts every 3-7 seconds")
    print("👀 Watch the frontend at http://localhost:3000")
    print("⏹️  Press Ctrl+C to stop\n")
    
    alert_count = 0
    
    try:
        while True:
            # Generate and send alert
            alert_data = generate_disaster_report()
            alert_count += 1
            
            print(f"🚨 Sending Alert #{alert_count}: {alert_data['message'][:50]}...")
            
            try:
                response = requests.post(
                    "http://localhost:8000/report",
                    json=alert_data,
                    timeout=5
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Alert sent successfully!")
                    print(f"   🆔 ID: {result['id'][:8]}...")
                    print(f"   🎯 Confidence: {result.get('confidence', 0):.0%}")
                    print(f"   📍 Location: {result['location']['lat']:.4f}, {result['location']['lng']:.4f}")
                else:
                    print(f"❌ Failed to send alert: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Network error: {e}")
            
            # Random delay between 3-7 seconds
            delay = random.uniform(3, 7)
            print(f"⏳ Next alert in {delay:.1f} seconds...\n")
            await asyncio.sleep(delay)
            
    except KeyboardInterrupt:
        print(f"\n🛑 Stopped after {alert_count} alerts")
        print("📊 Live demo completed")

if __name__ == "__main__":
    asyncio.run(send_continuous_alerts())
