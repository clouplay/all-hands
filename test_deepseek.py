#!/usr/bin/env python3
"""
DeepSeek entegrasyonunu test etmek için basit WebSocket client
"""

import asyncio
import websockets
import json
import uuid

async def test_deepseek_integration():
    """DeepSeek provider ile basit bir test"""
    
    # Session oluştur
    import requests
    response = requests.post("http://localhost:12000/api/v1/sessions")
    session_data = response.json()
    session_id = session_data["session_id"]
    
    print(f"Created session: {session_id}")
    
    # WebSocket bağlantısı
    uri = f"ws://localhost:12000/ws/{session_id}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("WebSocket connected")
            
            # Test mesajı gönder
            test_message = {
                "type": "message",
                "content": "Merhaba! DeepSeek provider ile çalışıyor musun?",
                "agent_type": "code",
                "metadata": {
                    "provider": "deepseek"
                }
            }
            
            await websocket.send(json.dumps(test_message))
            print("Message sent with DeepSeek provider")
            
            # Yanıtları bekle
            responses = []
            try:
                # İlk yanıt (connection_established)
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                responses.append(response_data)
                print(f"First response: {response_data.get('type')}")
                
                # Diğer yanıtları bekle (message_received, typing, typing_stop, message)
                for i in range(4):  # En fazla 4 yanıt bekle
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        response_data = json.loads(response)
                        responses.append(response_data)
                        print(f"Response {i+2}: {response_data.get('type')}")
                        
                        if response_data.get("type") == "message":
                            print(f"Agent response: {response_data.get('message', {}).get('content', 'No content')}")
                            
                    except asyncio.TimeoutError:
                        break
                
                # Sonuçları değerlendir
                message_types = [r.get('type') for r in responses]
                if 'message_received' in message_types:
                    print("✅ Message was received by server")
                if 'typing' in message_types:
                    print("✅ Typing indicator working")
                if 'message' in message_types:
                    print("✅ Agent response received")
                    print("✅ DeepSeek integration test successful!")
                else:
                    print("⚠️  No agent response (expected if no API key configured)")
                    
            except asyncio.TimeoutError:
                print("⚠️  Timeout waiting for initial response")
                
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_deepseek_integration())