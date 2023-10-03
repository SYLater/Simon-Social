# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message, Class  # Importing the Message model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        
        # Check if the user is authenticated and has access to the room.
        if self.scope["user"].is_authenticated and await self.has_access_to_room(self.room_name):
            await self.channel_layer.group_add(
                self.room_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close(code=4000)  # Close the WebSocket connection with a 4000 code (Policy Violation).

    async def disconnect(self, close_code):
        # Leave the room channel
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        
        user_id = self.scope['user'].user_id
        author = await self.get_user(user_id)
        chat_room = await self.get_class(self.room_name)
        
        message = await self.create_message(
            author=author, 
            content=message_content,
            chat_room=chat_room
        )
        
        # Send message to WebSocket group
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'author': author.username,  
                'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            }
        )
    
    # Handler for the "chat_message" type message.
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'author': event['author'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(user_id=user_id)
    
    @database_sync_to_async
    def get_chat_room(self, room_name):
        return Class.objects.get(name=room_name)
    
    @database_sync_to_async
    def save_message(self, author, content, chat_room):
        return Message.objects.create(author=author, content=content, chat_room=chat_room)

    @database_sync_to_async
    def create_message(self, author, content, chat_room):
        return Message.objects.create(
            author=author,
            content=content,
            chat_room=chat_room
        )

    @database_sync_to_async
    def has_access_to_room(self, room_name):
        # Implement your logic to check if a user has access to a room.
        # This might involve checking if the user is a member of the class/room, etc.
        # Return True if access is allowed, otherwise False.
        return True  # Example: Allow access to all authenticated users.
