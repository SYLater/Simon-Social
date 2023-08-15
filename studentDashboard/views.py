from django.shortcuts import render

# Create your views here.
def dashboard(request):
    return render(request, "dashboard/dashboard.html") # render html

def social(request):
    return render(request, "dashboard/social.html") # render html