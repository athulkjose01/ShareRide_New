"""
ASGI config for shareride project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""



# shareride/asgi.py (Replace mysite with your project name)
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import carpool_app.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shareride.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            carpool_app.routing.websocket_urlpatterns
        )
    ),
})