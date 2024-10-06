from celery import shared_task
import httpx
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
import logging

logger = logging.getLogger("ip_logger")

@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def fetch_ip_info(self, ip, channel_name):
    """
    Celery task to get IP information from ipinfo.io.
    Retries the task 3 times in case of failure.
    after task execuation finish them, task sends result back to client 
    """
    try:
        logger.debug(f"receive request to fetch ip {ip} data for channel name {channel_name}")
        logger.debug(f"Task {self.request.id} is in attempt {self.request.retries + 1}")

        
        url = f"https://ipinfo.io/{ip}/json"
        logger.debug(f"Fetching IP info for {ip}")
        response = httpx.get(url)
        response.raise_for_status()  
        ip_data = {"ip": ip, "data": response.json(), "task_id": self.request.id}
        status = "success"
        logger.info(f"Successfully fetched data for IP: {ip}")

    except httpx.HTTPStatusError as exc:
        logger.error(f"Task {self.request.id} failed on attempt {self.request.retries + 1} for IP {ip}: {exc}")
        ip_data = {"ip": ip, "error": str(exc), "task_id": self.request.id}
        status = "error"
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=5)

    except (httpx.RequestError, httpx.ConnectTimeout, httpx.HTTPError) as exc:
        logger.error(f"Task {self.request.id} connection error on attempt {self.request.retries + 1} for IP {ip}: {exc}")
        ip_data = {"ip": ip, "error": str(exc), "task_id": self.request.id}
        status = "error"
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=5)

    except Exception as exc:
        logger.error(f"Task {self.request.id} unexpected error for IP {ip}: {exc}")
        ip_data = {"ip": ip, "error": str(exc), "task_id": self.request.id}
        status = "error"

    logger.info(f"start process for sending ip data {ip_data} to channel name {channel_name}")
    channel_layer = get_channel_layer()
    logger.debug(f"channel layer {channel_layer}")
    async_to_sync(channel_layer.send)(channel_name, {
        "type": "send_ip_info", 
        "message": json.dumps({"status": status, **ip_data})
    })

    return ip_data  