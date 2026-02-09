from django.urls import re_path
from core import consumers

websocket_urlpatterns = [
    re_path(r"ws/captain/(?P<captain_id>[^/]+)/$", consumers.CaptainConsumer.as_asgi()),
    re_path(r"ws/user/(?P<user_id>[^/]+)/$", consumers.UserConsumer.as_asgi()),
    re_path(r"ws/order/(?P<order_id>[^/]+)/$", consumers.OrderTrackingConsumer.as_asgi()),
]
