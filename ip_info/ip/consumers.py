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
        logger.info(f"WebSocket connected from {self.scope['client']}")
        await self.accept()

    async def disconnect(self):
        logger.debug(f"web socket disconnect from {self.scope['client']}")
        pass
    
    # async def get_ip_data(self, ip: str) -> Dict[str, str]:
    #     """
    #     communicate with ip inf and get ip data
    #     Parameters:
    #         ip: str 
    #             ip to collect data about it
    #     Raises:
    #         httpx: httperr exception when connection error happens
        
    #     Returns:
    #         ip info: Dict[str, str]
    #             collect info about parsed ip 
    #     """
    #     try:
    #         logger.debug(f"receive request to get info from ip {ip}")
    #         url = f"https://ipinfo.io/{ip}/json"
    #         async with httpx.AsyncClient() as client:
    #                 response = await client.get(url)
    #                 response.raise_for_status()
    #                 ip_data = response.json()
    #                 logger.info(f"info collected for ip {ip} with data as {ip_data}")
    #                 return {"ip": ip, "data": ip_data}
                
    #     except httpx.HTTPStatusError as exc:

    #         status_code = exc.response.status_code
    #         exc_error = exc.response.json().get("error")
    #         logger.error(f"collect info for ip {ip} failed with status code {status_code} with error {exc_error}")
    #         return {"ip": ip, "error": exc_error}
        
    #     except (httpx.ConnectError, httpx.TimeoutError) as exc:
    #         logger.error(f"connection error while collect data for ip {ip} with {str(exc)}")
    #         return {"ip": ip, "error": str(exc)}
        
    #     except httpx.HTTPError as exc:
    #         logger.error(f"error collect ip {ip} data as {str(exc)}")
    #         return {"ip": ip, "error": str(exc)}

    @staticmethod
    def task_callback(result, channel_name):
        """
        Callback method called when the Celery task is finished.
        Sends the result back to the WebSocket client via the Channels layer.
        """
        channel_layer = get_channel_layer()
        result_data = result.get()
        async_to_sync(channel_layer.send)(channel_name, {
            "type": "send_ip_info",
            "message": json.dumps(result_data)
        })

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
            # tasks = [self.send_ip_info(ip) for ip in ips]
            # logger.info(f"start fire background tasks for ips {ips}")
            # asyncio.gather(*tasks)
            for ip in ips:
                result = fetch_ip_info.delay(ip)
                task_id = result.id
                asyncio.create_task(self.check_and_send_result(task_id))
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
    async def check_and_send_result(self, task_id):
        while True:
            result = AsyncResult(task_id)
            if result.status == 'SUCCESS':
                await self.send(text_data=json.dumps({
                    'status': 'success',
                    'ip_data': result.result
                }))
                break
            elif result.status == 'FAILURE':
                await self.send(text_data=json.dumps({
                    'status': 'error',
                    'message': 'Task failed'
                }))
                break
            await asyncio.sleep(1)
                
        
        
    async def send_ip_info(self, ip):
        """
        send and get ip info
        """
        collected_data: Dict[str, str] = await self.get_ip_data(ip)
        status: str = "failure" if collected_data.get("error") else "success"
        logger.debug(f"data collected for ip as {collected_data} with status {status}")
        await self.send(text_data = json.dumps({
            "status": status, ** collected_data
        }))
            
    
