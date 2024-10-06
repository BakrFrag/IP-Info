from django.urls import re_path
from ip import consumers

websocket_urlpatterns = [
    re_path(r'ws/echo/$', consumers.IPConsumer.as_asgi()),
]