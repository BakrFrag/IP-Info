# tasks.py
import httpx
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
import logging

logger = logging.getLogger("ip_logger")

@shared_task(bind=True, max_retries=3, default_retry_delay=10) 
def fetch_ip_info(self, ip):
    """
    Celery task to get IP information from ipinfo.io.
    Retries the task 3 times in case of failure.
    """
    try:
        url = f"https://ipinfo.io/{ip}/json"
        logger.debug(f"Fetching IP info for {ip}")
        response = httpx.get(url)
        response.raise_for_status()
        return {"ip": ip, "data": response.json()}
    
    except httpx.HTTPStatusError as exc:
        logger.error(f"Failed to fetch IP info for {ip}: {str(exc)}")
        raise self.retry(exc=exc, countdown=5)  # Retry with 5 seconds delay
    
    except (httpx.RequestError, httpx.ConnectTimeout) as exc:
        logger.error(f"Connection error for {ip}: {str(exc)}")
        raise self.retry(exc=exc, countdown=5)
    
    except MaxRetriesExceededError:
        logger.error(f"Max retries exceeded for IP {ip}")
        return {"ip": ip, "error": "Max retries exceeded"}
