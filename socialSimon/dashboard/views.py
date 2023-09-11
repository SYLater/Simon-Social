from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    # You can directly pass the user object to the template using request.user
    context = {
        'student': request.user,  # Assuming the user model has the necessary attributes
    }
    return render(request, 'dashboard/dashboard.html', context)
