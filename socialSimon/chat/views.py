from accounts.models import Class, User, UserClassesRelationship
from chat.models import DirectMessage, DirectMessageRoom, Message
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.shortcuts import render, redirect


def index(request):
    # Fetch all classes related to the current user
    user_classes = request.user.user_classes.all() 

    # Prepare the context with the user's classes
    context = {
        "user_classes": user_classes,
    }

    # Render the template with the context
    return render(request, "chat/index.html",context)


def room(request, room_name):
    return render(request, 'chat/chat_room.html', {'room_name': room_name})