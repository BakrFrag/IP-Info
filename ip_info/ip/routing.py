from django.urls import re_path
from ip.consumers import IPConsumer

websocket_urlpatterns = [
    re_path(r'ws/ip/$', IPConsumer.as_asgi()),
]