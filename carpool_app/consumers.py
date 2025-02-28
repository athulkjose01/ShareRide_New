import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Check if user is authenticated
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return

        # Get the other user's ID from the URL
        self.other_user_id = self.scope['url_route']['kwargs']['user_id']
        current_user_id = user.id

        # Generate a unique room name based on sorted user IDs
        user_ids = sorted([current_user_id, int(self.other_user_id)])
        self.room_group_name = f'chat_{user_ids[0]}_{user_ids[1]}'

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        user = self.scope['user']
        receiver_id = self.scope['url_route']['kwargs']['user_id']
        receiver = await database_sync_to_async(User.objects.get)(id=receiver_id)

        # Save the message to the database
        message_object = await self.create_message(user, receiver, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': user.username,
                'receiver': receiver.username,
                'timestamp': message_object.timestamp.isoformat(),
                'message_id': message_object.id
            }
        )

    async def chat_message(self, event):
        print(f"Received event: {event}")  # Log the entire event
        # Extract message data
        message = event['message']
        sender = event['sender']
        receiver = event['receiver']
        timestamp = event['timestamp']
        message_id = event['message_id']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'receiver': receiver,
            'timestamp': timestamp,
            'message_id': message_id
        }))

    @database_sync_to_async
    def create_message(self, sender, receiver, message_text):
        try: 
            message = Message(sender=sender, receiver=receiver, message=message_text)
            message.save()
            return message
        except Exception as e:
            print(f"Error saving message: {e}") # Log any errors
            return None  # Or raise the exception if appropriate

        
        
        