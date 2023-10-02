from accounts.models import Class, User, UserClassesRelationship
from chat.models import DirectMessage, DirectMessageRoom, Message
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render


@login_required
def chat_room(request, room_name):
    # Ensure that the user is part of the class (room) they are trying to access
    user_classes = UserClassesRelationship.objects.filter(user=request.user)
    class_names = [user_class.class_id.class_code for user_class in user_classes]

    if room_name not in class_names:
        return redirect('some_view_name')  # redirect to a suitable view if the user is not part of the class

    # Fetch the last 10 messages for the room
    messages = Message.last_10_messages(room_name)

    context = {
        'room_name': room_name,
        'messages': messages,
    }

    return render(request, 'chat/chat_room.html', context)
