from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

# Create your views here.



def login(request):
   
    return render(request, "login/login.html") #dir to html


