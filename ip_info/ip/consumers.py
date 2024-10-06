import json
import logging
import asyncio
from asgiref.sync import async_to_sync
from typing import Dict 
import httpx
from jsonschema import ValidationError
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from celery.result import AsyncResult
from ip.utils import validate_ip
from ip.tasks import fetch_ip_info


logger = logging.getLogger('ip_logger')

class IPConsumer(AsyncWebsocketConsumer):
    """
    ip consumer communicate with clients and processing their request
    """

    async def connect(self):
        """
        accept connection from user
        """
        logger.info(f"WebSocket connected from {self.scope['client']} with channel name {self.channel_name} and layer {self.channel_layer}")
        await self.accept()

    async def disconnect(self):
        logger.debug(f"web socket disconnect from {self.scope['client']}")
        pass

    async def send_ip_info(self, event):
        """
        Send the IP info back to the WebSocket client.
        """
        message = event['message']
        logger.info(f"Sending result back to client: {message}")
        await self.send(text_data=message)

    async def receive(self, text_data):
        try:
            logger.debug(f"receive request to get info about list of ips")
            text_data_as_json = json.loads(text_data)
            logger.debug(f"data converted to json as {text_data_as_json}")
            await validate_ip(text_data_as_json)
            logger.info(f"data validation success include true schema with valid public ips")
            ips = text_data_as_json.get("ips")
            for ip in ips:
                # result = fetch_ip_info.delay(ip)
                # task_id = result.id
                # asyncio.create_task(self.check_and_send_result(task_id))
                
                
                fetch_ip_info.apply_async(args=[ip, self.channel_name])
                
        except json.JSONDecodeError as exc:
            logger.error(f"parsed data can't converted to json")
            await self.send(text_data = json.dumps({
                "status":"error",
                "message": "invalid data"
            }))
        except ValidationError as exc:
            logger.error(f"parsed data not parsed as {exc.message} or may include not public ips")
            await self.send(text_data = json.dumps({
                "status":"error",
                "message": exc.message,
            }))

    async def send_ip_info(self, event):
        """
        Handle messages sent by the Celery task (via Channels layer).
        Send the result back to the WebSocket client.
        """
        print("event:",event)
        print(type(event))
        message = event['message']
        logger.info(f"Sending result back to WebSocket client: {message}")
        await self.send(text_data=message)
                
                
        
            
            
    async def check_and_send_result(self, task_id):
        while True:
            result = AsyncResult(task_id)
            if result.status == 'SUCCESS':
                await self.send(text_data=json.dumps({
                    'status': 'success',
                    'data': result.result
                }))
                break
            elif result.status == 'FAILURE':
                await self.send(text_data=json.dumps({
                    'status': 'error',
                    'message': 'Task failed',
                    'details': str(result.result)
                    
                }))
                break
            await asyncio.sleep(1)
                
        
        
    # async def send_ip_info(self, ip):
    #     """
    #     send and get ip info
    #     """
    #     collected_data: Dict[str, str] = await self.get_ip_data(ip)
    #     status: str = "failure" if collected_data.get("error") else "success"
    #     logger.debug(f"data collected for ip as {collected_data} with status {status}")
    #     await self.send(text_data = json.dumps({
    #         "status": status, ** collected_data
    #     }))
            
    
