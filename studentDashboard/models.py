# models.py

from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50)

class Class(models.Model):
    class_code = models.CharField(max_length=20)
    class_description = models.CharField(max_length=100)
    domain_component = models.CharField(max_length=100)
    campus = models.CharField(max_length=100)
    teacher_name = models.CharField(max_length=100)

class UserClasses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class_info = models.ForeignKey(Class, on_delete=models.CASCADE)

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message_content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
