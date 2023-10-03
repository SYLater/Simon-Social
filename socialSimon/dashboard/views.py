import re
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import requests
import json
from datetime import datetime

from accounts.views import extract_timetable_data,  Class
from tasks.models import Task

common_headers = {
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Host': 'intranet.padua.vic.edu.au',
    'Origin': 'https://intranet.padua.vic.edu.au',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
}

def get_user_classes(user):
    """Retrieve classes for a given user."""
    # Query the UserClassesRelationship model to get related classes
    related_classes = user.user_classes.all()
    
    # Extract the actual Class instances from the relationships
    classes = [relation.class_id for relation in related_classes]
    
    return classes

from datetime import datetime
import json

def generate_timetable_data(current_user):

    # Convert cookies string to dictionary
    cookies = json.loads(current_user.cookies)

    # Fetch Master timetable data
    timetable_data = extract_timetable_data(cookies)

    all_periods = ["Homeroom", "Period 1", "Period 2", "Period 3", "Period 4", "Period 5"]

    # Get user's classes
    user_classes = get_user_classes(current_user)

    # Get current date
    current_date = datetime.now()

    # Format date as "Day Month/Day"
    formatted_date_alternative = f"{current_date.strftime('%A')} {current_date.day}/{current_date.month}"

    # List to store each class for each period
    period_data = []

    # Iterate over each period
    for period in all_periods:
        class_for_period = "No class"
        room=""

        # Iterate over timetable data
        for timetable in timetable_data:
            if 'Date' in timetable:
                if formatted_date_alternative in timetable['Date']:
                    # Iterate over period data
                    for key, value in timetable.items():
                        if key == period:
                            # Iterate over user's classes
                            for user_class in user_classes:
                                class_code = user_class.class_code
                                # Iterate over class data
                                for data in value:
                                    if class_code in data:
                                        domain = Class.objects.get(class_code=class_code)
                                        class_for_period = domain.class_description
                                        room = data[-6:]
                                        break
                                if class_for_period != "No class":
                                    break

        # Add period data to list
        period_data.append({'period': period, 'class_code': class_for_period, 'room': room})
    return period_data


def dashboard(request):
    period_data = generate_timetable_data(request.user) 

    tasks = Task.objects.filter(user=request.user)

    # Prepare the context data for rendering the dashboard page
    context = {
        'student': request.user,
        'period_data': period_data,
        'tasks': tasks   # Add this line
    }

    return render(request, 'dashboard/dashboard.html', context)


def timetable(request):
    # Generate the timetable data for the user
    period_data = generate_timetable_data(request.user)

    # Create the context dictionary with the user and timetable data
    context = {
        'student': request.user,
        'period_data': period_data
    }

    # Render the timetable page using the context
    return render(request, 'dashboard/timetable.html', context)

