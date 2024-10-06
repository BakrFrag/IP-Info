import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import ip.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ip_info.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            ip.routing.websocket_urlpatterns
        )
    ),
})