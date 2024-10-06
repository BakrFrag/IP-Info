import json
import asyncio
import httpx
from jsonschema import ValidationError
from channels.generic.websocket import AsyncWebsocketConsumer
from .utils import validate_ip

class EchoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass
    
    async def get_ip_data(self, ip):
        url = f"https://ipinfo.io/{ip}/json"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()  
            except httpx.HTTPStatusError as e:
                return {"ip": ip, "error": str(e)}


    async def receive(self, text_data):
        try:
            
            text_data_as_json = json.loads(text_data)
            await validate_ip(text_data_as_json)
            ips = text_data_as_json.get("ips")
            for ip in ips:
                asyncio.create_task(self.send_ip_info(ip))
            
        except json.JSONDecodeError as exc:
            await self.send(text_data = json.dumps({
                "status":"error",
                "message": "invalid data"
            }))
        except ValidationError as exc:
            await self.send(text_data = json.dumps({
                "status":"error",
                "message": exc.message
            }))
        
    async def send_ip_info(self, ip):
        """
        send and get ip info
        """
        await self.send(text_data = json.dumps({
            "status": "success",
            "ip": ip,
            "ip_data": await self.get_ip_data(ip)
        }))
            
    
