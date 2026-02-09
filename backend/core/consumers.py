from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from core import redis_queue


class CaptainConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.captain_id = self.scope["url_route"]["kwargs"]["captain_id"]
        self.group_name = f"captain_{self.captain_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await sync_to_async(redis_queue.set_ws_presence)("captain", self.captain_id, True)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await sync_to_async(redis_queue.set_ws_presence)("captain", self.captain_id, False)

    async def receive_json(self, content, **kwargs):
        if content.get("type") == "ping":
            await self.send_json({"type": "pong"})

    async def job_offer(self, event):
        await self.send_json({"type": "job_offer", "data": event.get("payload")})

    async def job_assigned(self, event):
        await self.send_json({"type": "job_assigned", "data": event.get("payload")})

    async def job_status(self, event):
        await self.send_json({"type": "job_status", "data": event.get("payload")})


class UserConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.group_name = f"user_{self.user_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await sync_to_async(redis_queue.set_ws_presence)("user", self.user_id, True)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await sync_to_async(redis_queue.set_ws_presence)("user", self.user_id, False)

    async def receive_json(self, content, **kwargs):
        if content.get("type") == "ping":
            await self.send_json({"type": "pong"})

    async def job_assigned(self, event):
        await self.send_json({"type": "job_assigned", "data": event.get("payload")})

    async def location_update(self, event):
        await self.send_json({"type": "location_update", "data": event.get("payload")})

    async def job_status(self, event):
        await self.send_json({"type": "job_status", "data": event.get("payload")})


class OrderTrackingConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope["url_route"]["kwargs"]["order_id"]
        self.group_name = f"order_{self.order_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if content.get("type") == "ping":
            await self.send_json({"type": "pong"})

    async def location_update(self, event):
        await self.send_json({"type": "location_update", "data": event.get("payload")})
