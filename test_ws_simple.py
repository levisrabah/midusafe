import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/alerts"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established!")
            print("👂 Listening for alerts...")
            
            # Listen for messages
            message_count = 0
            while message_count < 5:  # Listen for 5 messages
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(message)
                    message_count += 1
                    
                    print(f"\n📨 Alert #{message_count} received:")
                    print(f"   🆔 ID: {data.get('id', 'N/A')}")
                    print(f"   🚨 Type: {data.get('disaster_type', 'Unknown')}")
                    print(f"   ⚡ Urgency: {data.get('urgency', 0)}/10")
                    print(f"   🎯 Confidence: {data.get('confidence', 0):.0%}")
                    print(f"   📍 Location: {data.get('location', {})}")
                    print(f"   📝 Summary: {data.get('summary', 'No summary')}")
                    print(f"   ⏰ Timestamp: {data.get('timestamp', 'No timestamp')}")
                    print("-" * 60)
                    
                except asyncio.TimeoutError:
                    print("⏳ Waiting for alerts... (sending test disaster)")
                    # Send a test disaster to trigger WebSocket
                    import requests
                    response = requests.post(
                        "http://localhost:8000/report",
                        json={"message": f"Test wildfire alert #{message_count + 1} with high urgency"}
                    )
                    if response.status_code == 200:
                        print("🚨 Test disaster sent!")
                    else:
                        print(f"❌ Failed to send test disaster: {response.status_code}")
                        
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return False
    
    print(f"\n✅ Successfully received {message_count} alerts via WebSocket!")
    return True

if __name__ == "__main__":
    asyncio.run(test_websocket())
