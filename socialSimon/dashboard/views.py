import re
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import requests
import json
from datetime import datetime

from accounts.views import extract_timetable_data

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

def generate_timetable_data(current_user):
    cookies = json.loads(current_user.cookies)
    print('hi')
    # Fetch Master timetable data
    timetable_data = extract_timetable_data(cookies)

    all_periods = ["Homeroom", "Period 1", "Period 2", "Period 3", "Period 4", "Period 5"]
    user_classes = get_user_classes(current_user)
    current_date = datetime.now()
    formatted_date_alternative = f"{current_date.strftime('%A')} {current_date.day}/{current_date.month}"

    # List to store each period's data
    period_data = []

    for period in all_periods:
        class_for_period = "No class"
        for timetable in timetable_data:
            if 'Date' in timetable:
                if formatted_date_alternative in timetable['Date']:
                    for key, value in timetable.items():
                        if key == period:
                            for user_class in user_classes:
                                class_code = user_class.class_code
                                for data in value:
                                    if class_code in data:
                                        class_for_period = class_code
                                        break
                                if class_for_period != "No class":
                                    break
        period_data.append({'period': period, 'class_code': class_for_period})

    return period_data

def dashboard(request):
    period_data = generate_timetable_data(request.user) 
    context = {
        'student': request.user,
        'period_data': period_data
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

