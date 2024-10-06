import json
import logging
import asyncio
from typing import Dict 
import httpx
from jsonschema import ValidationError
from channels.generic.websocket import AsyncWebsocketConsumer
from .utils import validate_ip

logger = logging.getLogger('ip_logger')

class IPConsumer(AsyncWebsocketConsumer):
    """
    ip consumer communicate with clients and processing their request
    """

    async def connect(self):
        """
        accept connection from user
        """
        logger.debug(f"receive request to connect")
        await self.accept()

    async def disconnect(self, close_code):
        logger.debug(f"receive request to disconnect with code {close_code}")
        pass
    
    async def get_ip_data(self, ip: str) -> Dict[str, str]:
        """
        communicate with ip inf and get ip data
        Parameters:
            ip: str 
                ip to collect data about it
        Raises:
            httpx:httperr exception when connection error happens
        
        Returns:
            ip info: Dict[str, str]
                collect info about parsed ip 
        """
        try:
            logger.debug(f"receive request to get info from ip {ip}")
            url = f"https://ipinfo.io/{ip}/json"
            async with httpx.AsyncClient() as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    ip_data = response.json()
                    logger.info(f"info collected for ip {ip} with data as {ip_data}")
                    return {"ip": ip, "data": ip_data}
                
        except httpx.HTTPStatusError as exc:

            status_code = exc.response.status_code
            exc_error = exc.response.json().get("error")
            logger.error(f"collect info for ip {ip} failed with status code {status_code} with error {exc_error}")
            return {"ip": ip, "error": exc_error}
        
        except (httpx.ConnectError, httpx.TimeoutError) as exc:
            logger.error(f"connection error while collect data for ip {ip} with {str(exc)}")
            return {"ip": ip, "error": str(exc)}
        
        except httpx.HTTPError as exc:
            logger.error(f"error collect ip {ip} data as {str(exc)}")
            return {"ip": ip, "error": str(exc)}


    async def receive(self, text_data):
        try:
            logger.debug(f"receive request to get info about list of ips")
            text_data_as_json = json.loads(text_data)
            logger.debug(f"data converted to json as {text_data_as_json}")
            await validate_ip(text_data_as_json)
            logger.info(f"data validation success include true schema with valid public ips")
            ips = text_data_as_json.get("ips")
            for ip in ips:
                logger.info(f"start fire background task for {ip}")
                asyncio.create_task(self.send_ip_info(ip))
            
        except json.JSONDecodeError as exc:
            logger.error(f"parsed data can't converted to json")
            await self.send(text_data = json.dumps({
                "status":"error",
                "message": "invalid data"
            }))
        except ValidationError as exc:
            logger.error(f"parsed data not match json schema or include wrong ips or include private ips")
            await self.send(text_data = json.dumps({
                "status":"error",
                "message": exc.message
            }))
        
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
            
    
