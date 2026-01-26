import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/alerts"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established!")
            
            # Listen for messages
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    print(f"📨 Received alert:")
                    print(f"   ID: {data.get('id')}")
                    print(f"   Type: {data.get('disaster_type')}")
                    print(f"   Urgency: {data.get('urgency')}/10")
                    print(f"   Location: {data.get('location')}")
                    print(f"   Summary: {data.get('summary')}")
                    print("-" * 50)
                except asyncio.TimeoutError:
                    print("⏳ Waiting for alerts...")
                    # Send a test disaster to trigger WebSocket
                    import requests
                    response = requests.post(
                        "http://localhost:8000/report",
                        json={"message": "Test wildfire alert with high urgency"}
                    )
                    if response.status_code == 200:
                        print("🚨 Test disaster sent!")
                        
    except Exception as e:
        print(f"❌ WebSocket error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
