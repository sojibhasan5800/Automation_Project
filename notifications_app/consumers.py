import json,html
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'notification_%s' % self.room_name
        print(self.room_group_name)
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    # async def receive(self, text_data):
    #     text_data_json = json.loads(text_data)
    #     message = text_data_json['message']

    #     # Send message to room group
    #     await self.channel_layer.group_send(
    #         self.room_group_name,
    #         {
    #             'type': 'chat_message',
    #             'message': message
    #         }
    #     )

    # Receive message from room group
    async def send_notification(self, event):
        print("WebSocket received message:", event) 

        raw_message = event.get("message", None)

        # if message none deafule value set
        if raw_message is None:
            message = {"text": "No message available", "type": "info"}
        else:
            try:
                message = json.loads(raw_message)
            except (json.JSONDecodeError, TypeError):
                message = {"text": str(raw_message), "type": "info"}

        # key not find then default value use
        text = html.escape(message.get("text", "No message available"))
        type_ = message.get("type", "info")

        # Frontend sender
        await self.send(text_data=json.dumps({
            "text": text,
            "type": type_,
        }))

