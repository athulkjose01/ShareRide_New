# shareride/routing.py  (Replace mysite with your project name)
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import carpool_app.routing  # Import your app's routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            carpool_app.routing.websocket_urlpatterns
        )
    ),
})