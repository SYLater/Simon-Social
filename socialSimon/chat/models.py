from django.db import models
from accounts.models import User, Class

class Message(models.Model):
    author = models.ForeignKey(User, related_name='author_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    chat_room = models.ForeignKey(Class, related_name='class_messages', on_delete=models.CASCADE)

    def __str__(self):
        return self.author.user_userName

    def last_10_messages(class_id):
        # This function retrieves the last 10 messages for a chat room.
        return Message.objects.filter(chat_room=class_id).order_by('-timestamp').all()[:10]


class DirectMessageRoom(models.Model):
    participant1 = models.ForeignKey(User, related_name='user_participant1', on_delete=models.CASCADE)
    participant2 = models.ForeignKey(User, related_name='user_participant2', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.participant1.user_userName} - {self.participant2.user_userName}"

class DirectMessage(models.Model):
    room = models.ForeignKey(DirectMessageRoom, related_name='dm_room', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='dm_author', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.user_userName

    def last_10_messages(room_id):
        return DirectMessage.objects.filter(room=room_id).order_by('-timestamp').all()[:10]
