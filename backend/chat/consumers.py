from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from chat import services


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.group_name = f"chat_{self.room_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await sync_to_async(services.ensure_chat_room)(self.room_id)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        msg_type = content.get("type")
        if msg_type == "ping":
            await self.send_json({"type": "pong"})
            return
        if msg_type == "delivered":
            message_id = content.get("message_id")
            user_id = content.get("user_id")
            if message_id and user_id:
                await sync_to_async(services.mark_delivered)(message_id, user_id)
            return
        if msg_type != "message":
            return

        sender_id = content.get("sender_id")
        sender_role = content.get("sender_role")
        receiver_id = content.get("receiver_id")
        receiver_role = content.get("receiver_role")
        text = content.get("message")
        client_message_id = content.get("client_message_id")

        if not sender_id or not sender_role or not text:
            await self.send_json({"type": "error", "detail": "Invalid message"})
            return

        message_doc = await sync_to_async(services.store_message)(
            self.room_id,
            sender_id,
            sender_role,
            receiver_id,
            receiver_role,
            text,
            client_message_id,
        )

        payload = {
            "message": {
                "id": str(message_doc.get("_id")),
                "room_id": self.room_id,
                "sender_id": sender_id,
                "sender_role": sender_role,
                "receiver_id": receiver_id,
                "receiver_role": receiver_role,
                "text": message_doc.get("text"),
                "created_at": message_doc.get("created_at").isoformat(),
                "client_message_id": client_message_id,
            }
        }
        await self.channel_layer.group_send(
            self.group_name,
            {"type": "chat_message", "payload": payload},
        )
        await self.send_json({"type": "ack", "message_id": str(message_doc.get("_id"))})

    async def chat_message(self, event):
        await self.send_json({"type": "message", "data": event.get("payload")})
