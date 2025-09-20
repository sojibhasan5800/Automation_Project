from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notification/(?P<room_name>\w+)/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'tictacs/ws/game/(?P<room_code>\w+)/$', consumers.GameConsumer.as_asgi()),
]
