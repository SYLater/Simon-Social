import json
import re  # for regular expression

import requests
from bs4 import BeautifulSoup
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import redirect, render
from helium import click, start_chrome, write
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .forms import UserLoginForm
from .models import StudentProfile, User, Class, UserClassesRelationship

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


def fetch_timetable(cookies):
    timetable_url = 'https://intranet.padua.vic.edu.au/WebModules/Timetables/MasterTimetable.aspx'
    timetable_headers = {
        **common_headers,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Cache-Control': 'max-age=0',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://intranet.padua.vic.edu.au/WebModules/Timetables/MasterTimetable.aspx',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1'
    }
    
    # Add the content length if you know the exact size of your payload
    # timetable_headers['Content-Length'] = '3628'
    
    payload = {
    "__EVENTTARGET": "",
    "__EVENTARGUMENT": "",
    "__VIEWSTATE": "aQPDBcXdzdoJr/peMzuzH88Jio2y5ZEEPtIxObppfOrPhFdt0OMVpH6UJ1XUeBh1vxmbejdqmlNuC+cDKLmMdgBQah1yi4FH/PpnkBMn6TebyVppjJfIky1a1JOZxc8BN7kHLlkgj/HFPoTIv/qB/pYyZEWEGfCJ389GClryx2kSYpdvdnvKusVwH6ysj9ibIbzYE4YibV0c5RcFI1brM6ohFb5KOZb7yuPliwWRJyaASPfDAGX9IFf8lBFw+uHBZ7cC9EbZjXFR9E1uk7aMInQk9cJZEm1OCJ4TRV7RstZ89n2ap2IABi3vB7PjAYYGBN/838tKWXtkIYdgY56xlc5ax6mt4UfrTV/klzyxsJulPkQ5rdoeVNUndtI8H6tVks4ynYs4T9bt6L6ktPny9r/Xlqk0ZNIP36meZ8rJAgTOBhchbDUWYYBsDNnPYhdt8YvcDuRT+A0rhn2gQkTNyGLrx2Qx9rFOt7UVdpFZo/cv19PW0/+R6QKtSKUv4GYQQGKVR/2OB91Lx2A10EK7a4drXyarAN9se7k0C52YfbxGRb7TDb0RkJ7y/gftHHrlDnAGp9qEu2i37Yw6dOvX9SyovapQ913Ygnt15BzCY1rLMlVjBvlVIDVVxkRYPdxNrE5dvInBQ5H7ZLLFsTSyH8QwEA1tGBHWhe6xACIWOvBpfH32S6seBxiBiyyeMeIjPfXPWa9FZKnDCCpuErxaGVK0DyvASzNB45NTlEdAZoOWWfVIL+70iictYY9p+I/IlGnHT4sR/i51sW2l8QtCW3rvXTuCxR/eHrAug6yPHtsQf03iPv8kpuMtVCOmu7y8+qRXdPiEPTltjyLKNqkIuJXGneZoItOfH54c3NtDoUnEJF+YnRJsF2EfJJXD6Ky2SjFqpx5y8VhnYUHmzwZIv8SOzIX/mOnUjDm5M/kLcnQsNYvrtADHeqE4tEeCS9v4RIzFSgHK54BnbWoGxBAJHPaONI30FaE0BzzTwhz0wlu4169XhVzmz/RtuPEKg8OkeP9Z9NWGdwsTu8lzKtxLvJj+ca0/eLonzLfcp364PS+RmZfkh9CM8EpBO7KeTVXJcOvpOgQlN7gjgehd391hSL+JcfohMeuqFGR/4iAA6qyQyhlQ2c0cjZ/Wb12YDoGM9bOyVsqB6gt89HJcogyRzTew8LzUPIW8YJhWLVBZOoUmf1VcKGBQKgewvlN/dSvWFLyJvx7qYqp/t08mzErQ/HQTUlBtvKbaJluXheNZAC/lgqWxhexspCs7Bw424qOlXNYxugdJNUxKpsdlMjluFc+YVEXorfKlbh3Az99PcUGHShIHlFNUOKkARhvEYEVaR7NUbwQ1dC+RZzpTOdvurfcyh/tA13uEOaf2urrdyGga6BmnZfQwEOxtocJt/A04yWMm4s76uvdLCqt32zreIJy2WgsvOBEEZBwpzZyqHKodxcpE+dZTu2dcZWBhh7QQKCL07Z3T1x+nx2ogu2fm1Wk+vvEWAk1/yfm+ssiGmA/e8zCHHqebGwTT2fI3BQrRxFvE+ZVSnrxHpJrERhhPYEDWyVxmtiAyDXOwmseutEiRBnft",
    "__VIEWSTATEGENERATOR": "36B1BA4C",
    "__VIEWSTATEENCRYPTED": "",
    "__EVENTVALIDATION": "C4F+h7ekCnQ+rUeiBiRGWU7vyiuNPgEClaULQRBFszYzxZzwN5iLtu34If9d3zSKTSTvMrbxjhukJpmfF5mp4ATSudZw7p4+P5UpWjGXKMwsYRAFjSISqDLH1aL0s9UANuYOpSdkHTFtTrfU3FxqQkMPp8i8Lls7lnjVLxUXYfJucoC4QojqR13ZXWI7x3yBuosw+iZHmYq7Y8EByVjfr8/Vn+ua1/GaxIcRm+EsTnUSny4InR0t6vKPggTgVvh08eCfnp7SPGrHzzhf3Y6Bs5bmJDFRMJUQqy5/CExGX5fR6y+zdRksKA1RBL38IiqekCa0wg==",
    "ContentPlaceHolder1_ContentPlaceHolder1_TimetableDate_clientState": " %7C0%7C012023-10-2-0-0-0-0%7C%7C%5B%5B%5B%5B%5D%5D%2C%5B%5D%2C%5B%5D%5D%2C%5B%7B%7D%2C%5B%5D%5D%2C%22012023-10-2-0-0-0-0%22%5D",
    "ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder1$Cycles": "1",
    "ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder1$TimetableGroup": "PADUA",
    "ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder1$GenerateTimetable.x": "112",
    "ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder1$GenerateTimetable.y": "16",
    "_ig_def_dp_cal_clientState": "%5B%5Bnull%2C%5B%5D%2Cnull%5D%2C%5B%7B%7D%2C%5B%5D%5D%2C%2201%2C2023%2C10%22%5D",
    "ctl00$ctl00$_IG_CSS_LINKS_": "/apple-icon-57x57.png?m=201809041635|/apple-icon-60x60.png?m=201809041635|/apple-icon-72x72.png?m=201809041635|/apple-icon-76x76.png?m=201809041635|/apple-icon-114x114.png?m=201809041635|/apple-icon-120x120.png?m=201809041635|/apple-icon-144x144.png?m=201809041635|/apple-icon-152x152.png?m=201809041635|/apple-icon-180x180.png?m=201809041635|/android-icon-512x512.png?m=201809041635|/android-icon-192x192.png?m=201809041635|/favicon-32x32.png?m=201809041635|/favicon-96x96.png?m=201809041635|/favicon-16x16.png?m=201809041635|/manifest.json|/CSS/ServerStyles.ashx|../../ig_res/SIMONGeneric/ig_monthcalendar.css|../../ig_res/SIMONGeneric/ig_texteditor.css|../../ig_res/SIMONGeneric/ig_shared.css"
}
    response = requests.post(timetable_url, headers=timetable_headers, cookies=cookies, data=payload)
    return response.text


def read_data_from_json(input_file):
    """Read data from the provided JSON file."""
    with open(input_file, 'r') as file:
        data = json.load(file)
    return data

def extract_timetable_data(cookies):
    """Extract timetable data from the provided HTML file."""
    
    content = read_data_from_json("tabel_output.json")

    soup = BeautifulSoup(content, 'html.parser')

    def extract_classes(text):
        # Pattern to capture prefixes and class codes based on the provided examples
        pattern = r'([0-9A-Z]+)(\d{1,2}[A-Z]+\d{1,2}[A-Z]+(?:\([A-Z]+\d{3}\)))'
        matches = re.findall(pattern, text)
        
        # Return a list of matches with the specified prefix and class code combined
        return [prefix + class_code for prefix, class_code in matches] if matches else text

    # Extract data from the tables with the class "clsGeneralAccessTimetableGeneration"
    extracted_data = []
    for table in soup.find_all('table', class_='clsGeneralAccessTimetableGeneration'):
        rows = table.find_all('tr')
        headers = [header.get_text(strip=True) for header in rows[0].find_all('td')]
        
        for row in rows[1:]:
            row_data = [cell.get_text(strip=True) for cell in row.find_all('td')]
            row_data = [item.strip() for item in ','.join(row_data).split(',')]
            extracted_data.append(dict(zip(headers, row_data)))

    # Clean extracted data
    cleaned_extracted_data = [
        {key: extract_classes(value) for key, value in data_dict.items()}
        for data_dict in extracted_data
    ]

    for entry in cleaned_extracted_data:
        if "" in entry:
            entry["Date"] = entry.pop("")

    with open('extracted_data.json', 'w') as file:
        json.dump(extracted_data, file)
    with open('cleaned_extracted_data.json', 'w') as file:
        json.dump(cleaned_extracted_data, file)

    return cleaned_extracted_data

# NOTE: The function is now updated. However, I cannot run this function directly since it relies on a function 
# `read_data_from_json` and other external dependencies that are not provided.


def fetch_all_classes(request):
    #define user & cookies
    current_user = request.user
    cookies = json.loads(current_user.cookies)
    timetable_data = extract_timetable_data(cookies)

    all_classes = []
    for timetable in timetable_data:
        if 'Class Code' in timetable:
            all_classes.append(timetable)
    return all_classes
                

def fetch_user_classes(current_user, cookies):
    studentID = StudentProfile.objects.get(user=current_user).StudentID	# StudentID for the request 
    cookies = json.loads(cookies) # Cookies for the request

    user_info_url = 'https://intranet.padua.vic.edu.au/Default.asmx/UserInformation'
    user_info_headers = {
        **common_headers,
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Referer': f'https://intranet.padua.vic.edu.au/profiles/students/{studentID}/aspx/GeneralInformation/StudentProfileTimetable.aspx/',
    }
    payload = json.dumps({})
    response = requests.post(user_info_url, headers=user_info_headers, cookies=cookies, data=payload)
    
   
    
    data1 = response.json()
    # Assuming the JSON data is stored in a variable named 'data'

    learning_areas_classes = []
    for item in data1['d']["menuItems"]["O"]:
        if item[0].startswith('LEARNINGAREASCLS'):
            learning_areas_classes.append(item)

    # Now, the 'learning_areas_classes' list contains all the items with keys starting with "LEARNINGAREASCLS"
    # You can access and manipulate this data as needed.

    classes = []
    # For example, to print the information about these classes:
    for class_item in learning_areas_classes:
        classes.append(class_item[5])

    return classes

def login(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        
        if form.is_valid():
            user_email = form.cleaned_data['user_email']
            password = form.cleaned_data['password']
            if "@" in user_email:
                         username = user_email.split("@")[0]
            # Check if user exists in Django database
            user = authenticate(user_email=user_email, password=password)
            if user:
                auth_login(request, user)
                return redirect("/dashboard")

            # Check with external system if local authentication fails
            success, data = simonAuthChk(username=username, password=password)

            if success:
                user_instance, created = User.objects.get_or_create(user_email=user_email, user_userName=username)
                
                if created:
                    if "@" in user_email:
                        user_instance.user_userName = user_email.split("@")[0]
                    user_instance.set_password(password)  # Use Django's built-in password hashing

                    # Update User instance with fetched data
                    user_instance.user_firstName = data['profile_details']['d']['FullName'].split(" ", 1)[0]
                    user_instance.user_lastName = data['profile_details']['d']['FullName'].split(" ", 1)[1]
                    user_instance.cookies = json.dumps(data['cookies'])
                    user_instance.save()

                # Create and save the associated StudentProfile
                StudentProfile.objects.create(
                    user=user_instance,
                    studentGUID=data['profile_details']['d']['UserGUID'],
                    communityID=data['profile_details']['d']['CommunityID'],
                    communityUID=data['profile_details']['d']['UID'],
                    YearLevelCode=data['profile_details']['d']['YearLevelCode'],
                    HouseDescription=data['profile_details']['d']['HouseDescription'],
                    HomeroomCode=data['profile_details']['d']['HomeroomCode'],
                    HomeroomDescription=data['profile_details']['d']['HomeroomDescription'],
                    HomeroomTeachers=','.join(data['profile_details']['d']['HomeroomTeachers']),  # Assuming it's a list
                    StudentID=data['profile_details']['d']['StudentID'],
                    StudentPersonalRefId=data['profile_details']['d'].get('StudentPersonalRefId', None),  # Using get in case the key doesn't exist
                    NoteCount=data['profile_details']['d']['NoteCount'],
                    NoteImportantCount=data['profile_details']['d']['NoteImportantCount'],
                    ImportantMedicalWarning=data['profile_details']['d']['ImportantMedicalWarning']
                )
                user = authenticate(username=user_email, password=password)
                auth_login(request, user)
                return redirect("/dashboard")
            else:
                messages.error(request, "Incorrect credentials or you don't have a Simon account.")
        else:
            messages.error(request, "Invalid form submission.")
            form = UserLoginForm()
    else:
        form = UserLoginForm()
    return render(request, "accounts/login.html", {'form': form})

def update_all_classes(request):
    Class.objects.all().delete()
    all_classes = fetch_all_classes(request)
    for class_item in all_classes:
        match = re.search(r'\((\w+)\)', class_item["Teacher Name"])
        if match:
            teacher_code = match.group(1)
        else:
            teacher_code = None
        new_class = Class(
            class_code=class_item["Class Code"],
            class_description=class_item["Class Description"],
            class_domain=class_item["Domain Component"],
            class_campus=class_item["Campus"],
            class_teacher=class_item["Teacher Name"],
            class_teacher_code=teacher_code
            )
        new_class.save()

def add_student_to_class(student, class_code):
    try:
        target_class = Class.objects.get(class_code=class_code)
    except ObjectDoesNotExist:
        print(f"Class with code {class_code} not found.")
        return

    # Create a new relationship between the student and the class
    relationship = UserClassesRelationship(user=student, class_id=target_class)
    relationship.save()

def get_user_classes(user):
    """Retrieve classes for a given user."""
    # Query the UserClassesRelationship model to get related classes
    related_classes = user.user_classes.all()
    
    # Extract the actual Class instances from the relationships
    classes = [relation.class_id for relation in related_classes]
    
    return classes

def profile(request):
    button_clicked = request.POST.get('whichButton')
    current_user = request.user
    if button_clicked == 'sync':
        class_codes = []
        student_classes = fetch_user_classes(request.user, request.user.cookies)
        pattern = r'\((\d[A-Z\d]+)\)'  # Matches a number followed by uppercase letters and numbers inside parentheses
        for classes in student_classes:
            match = re.search(pattern, classes)
            if match:
                class_codes.append(match.group(1))
        for class_code in class_codes:
            add_student_to_class(request.user, class_code)

        print("Button 1")
        
    elif button_clicked == 'button2':
        
        print("Button 2")
    user_classes = get_user_classes(current_user)
    context = {
        'student': request.user,  # Assuming the user model has the necessary attributes
        "user_classes": user_classes
    }
    return render(request, "accounts/profile.html", context)


def display_image(request):
    current_user = request.user
    cookiesvalues = current_user.cookies
    cookies = json.loads(cookiesvalues)
    # Specify the URL to fetch the image from
    StudentID = StudentProfile.objects.get(user=current_user).StudentID
    print(StudentID)
    url = f"https://intranet.padua.vic.edu.au/WebHandlers/DisplayUserPhoto.ashx?StudentID={StudentID}"

    # Define the headers based on the provided information
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": "\"Chromium\";v=\"116\", \"Not)A;Brand\";v=\"24\", \"Google Chrome\";v=\"116\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    }

    # Make the GET request
    response = requests.get(url, headers=headers, cookies=cookies)

    # Check if the request was successful
    if response.status_code == 200:
        # Return the image content as a response
        return HttpResponse(response.content, content_type='image/jpeg')
    else:
        return HttpResponse("Failed to fetch the image", status=400)

import requests


def simonAuthChk(username, password):
    # helium 3.2.5

    chromedriver_path = 'accounts/chromedriver.exe'  # Update this path

    url = 'https://intranet.padua.vic.edu.au/Login/Default.aspx?ReturnUrl=%2F'

    service = Service(executable_path=chromedriver_path)
    driver = start_chrome(url, headless=False)

    # Fill in login details
    write(username, into='Username')
    write(password, into='Password')

    # Click the login button
    click(('Sign in'))

    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[2]/div[1]/nav/div[1]/div[1]/div[2]/div/a[1]')))

        # Locate the element containing the four-digit number
        element = driver.find_element_by_xpath(
            '/html/body/div[2]/div[1]/nav/div[1]/div[1]/div[2]/div/a[1]')
        href = element.get_attribute('href')

        # Use regex to extract the number (one or more digits)
        match = re.search(r'/(\d+)/aspx', href)
        if match:
            studentID = match.group(1)
            print(f"Number: {studentID}")

        # Extract cookies
        print("Extracting cookies")
        cookies = driver.get_cookies()

        # Cookies: Extract from your browser and insert here
        cookies = {
            'AzureAppProxyAnalyticCookie_1971d3c1-f744-420e-a7b0-2bd2e07a23b5_https_1.3': cookies[1]["value"],
            'ASP.NET_SessionId': cookies[2]["value"],
            'adAuthCookie': cookies[0]["value"],
        }


        all_data = {}

        # Fetch profile details
        def fetch_profile_details(studentID):
            profile_details_url = 'https://intranet.padua.vic.edu.au/WebModules/Profiles/Student/StudentProfiles.asmx/StudentProfileDetails'
            profile_headers = {
                **common_headers,
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json',
                'Referer': f'https://intranet.padua.vic.edu.au/profiles/students/{studentID}/aspx/GeneralInformation/StudentProfilePersonalDetails.aspx/',
            }
            payload = json.dumps({"studentId": studentID})
            response = requests.post(
                profile_details_url, headers=profile_headers, cookies=cookies, data=payload)
            return response.json()

        all_data['profile_details'] = fetch_profile_details(studentID)
        all_data['cookies'] = cookies

        print('worked')
        driver.close()
        return True, all_data
    except Exception as e:
        print("Timeout")
        print(f"An error occurred: {e}")
        driver.close()
        return False, None  # Make sure to return a tuple


def simonScrap(username, password):
    # helium 3.2.5

    chromedriver_path = 'accounts/chromedriver.exe'  # Update this path

    url = 'https://intranet.padua.vic.edu.au/Login/Default.aspx?ReturnUrl=%2F'

    service = Service(executable_path=chromedriver_path)
    driver = start_chrome(url, headless=False)

    # Fill in login details
    write(username, into='Username')
    write(password, into='Password')

    # Click the login button
    click(('Sign in'))
    all_data = {}

    def fetch_profile_details(studentID):
        profile_details_url = 'https://intranet.padua.vic.edu.au/WebModules/Profiles/Student/StudentProfiles.asmx/StudentProfileDetails'
        profile_headers = {
            **common_headers,
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Referer': f'https://intranet.padua.vic.edu.au/profiles/students/{studentID}/aspx/GeneralInformation/StudentProfilePersonalDetails.aspx/',
        }
        payload = json.dumps({"studentId": studentID})
        response = requests.post(
            profile_details_url, headers=profile_headers, cookies=cookies, data=payload)
        return response.json()

    def fetch_dashboard_data(studentGUID):
        dashboard_url = 'https://intranet.padua.vic.edu.au/WebModules/Profiles/Student/GeneralInformation/StudentDashboard.aspx/GetDashboardData'
        dashboard_headers = {
            **common_headers,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://intranet.padua.vic.edu.au/WebModules/Profiles/Student/GeneralInformation/StudentDashboard.aspx?UserGUID={studentGUID}',
        }
        payload = json.dumps({"guidString": studentGUID, "semester": 33})
        response = requests.post(
            dashboard_url, headers=dashboard_headers, cookies=cookies, data=payload)
        return response.json()

    def fetch_timetable_data(studentGUID):
        timetable_url = 'https://intranet.padua.vic.edu.au/Default.asmx/GetUserInfo?1693648835712'
        timetable_headers = {
            **common_headers,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/json; charset=utf-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://intranet.padua.vic.edu.au/WebModules/Profiles/Student/GeneralInformation/StudentProfileTimetable.aspx?UserGUID={studentGUID}',
        }
        response = requests.post(
            timetable_url, headers=timetable_headers, cookies=cookies)
        return response.json()

    def fetch_user_info(studentID, studentGUID):
        user_info_url = 'https://intranet.padua.vic.edu.au/Default.asmx/UserInformation'
        user_info_headers = {
            **common_headers,
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Referer': f'https://intranet.padua.vic.edu.au/profiles/students/{studentID}/aspx/GeneralInformation/StudentProfileTimetable.aspx/',
        }
        payload = json.dumps({})
        response = requests.post(
            user_info_url, headers=user_info_headers, cookies=cookies, data=payload)
        return response.json()

    def fetch_alerts(studentGUID):
        alerts_url = 'https://intranet.padua.vic.edu.au/Default.asmx/GetAlerts'
        alerts_headers = {
            **common_headers,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/json; charset=utf-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://intranet.padua.vic.edu.au/WebModules/Profiles/Student/GeneralInformation/StudentProfileTimetable.aspx?UserGUID={studentGUID}',
        }
        response = requests.post(
            alerts_url, headers=alerts_headers, cookies=cookies)
        return response.json()

    def fetch_messages(studentGUID):
        get_messages_url = 'https://intranet.padua.vic.edu.au/Default.asmx/GetMessages'
        get_messages_headers = {
            **common_headers,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/json; charset=utf-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://intranet.padua.vic.edu.au/WebModules/Profiles/Student/GeneralInformation/StudentProfileTimetable.aspx?UserGUID={studentGUID}',
        }
        payload = json.dumps({})
        response = requests.post(
            get_messages_url, headers=get_messages_headers, cookies=cookies, data=payload)
        return response.json()

    def fetch_medical_status(communityID, studentGUID):
        medical_status_url = 'https://intranet.padua.vic.edu.au/Webmodules/medical/Medical.asmx/GETmedicalStudentStatus'
        medical_status_headers = {
            **common_headers,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://intranet.padua.vic.edu.au/WebModules/Profiles/Student/MedicalInformation/MedicalStatus.aspx?UserGUID={studentGUID}',
        }
        payload = json.dumps({"communityID": communityID})
        response = requests.post(
            medical_status_url, headers=medical_status_headers, cookies=cookies, data=payload)
        return response.json()

    def fetch_behavioural_history(communityUID, YearLevelCode, studentGUID):
        behavioural_history_url = 'https://intranet.padua.vic.edu.au/WebServices/BehaviouralTracking.asmx/GetStudentProfileBehaviouralHistory?1693652261176'
        behavioural_history_headers = {
            **common_headers,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://intranet.padua.vic.edu.au/WebModules/Profiles/Student/SocialBehaviour/StudentProfileBehaviouralHistory.aspx?UserGUID={studentGUID}',
        }
        payload = json.dumps({
            "selectedAcademicYearID": 21,
            "communityUID": communityUID,
            "yearLevelCode": YearLevelCode
        })
        response = requests.post(
            behavioural_history_url, headers=behavioural_history_headers, cookies=cookies, data=payload)
        return response.json()

    def fetch_commendations(studentGUID):
        commendations_url = 'https://intranet.padua.vic.edu.au/WebServices/BehaviouralTracking.asmx/GetWorkDeskCommendationsPaged'
        commendations_headers = {
            **common_headers,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://intranet.padua.vic.edu.au/WebModules/Profiles/Student/SocialBehaviour/StudentProfileBehaviouralHistory.aspx?UserGUID={studentGUID}',
        }
        commendations_payload = json.dumps({
            "sort": [{"field": "CommendationDate", "dir": "desc"}],
            "filter": None,
            "userGUID": studentGUID,
            "startDate": "2022-01-16T13:00:00.000Z",
            "endDate": "2022-12-06T13:00:00.000Z",
            "showMyRecordsOnly": False,
            "take": 50,
            "skip": 0,
            "page": 1,
            "pageSize": 50
        })
        response = requests.post(
            commendations_url, headers=commendations_headers, cookies=cookies, data=commendations_payload)
        return response.json()

    def fetch_enrollment_info(studentID, studentGUID):
        enrollment_info_url = f'https://intranet.padua.vic.edu.au/WebModules/Profiles/Student/EnrolmentInformation/StudentProfileStudentStatus.aspx?UserGUID={studentGUID}'
        enrollment_info_headers = {
            **common_headers,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Sec-Fetch-Dest': 'iframe',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Referer': f'https://intranet.padua.vic.edu.au/profiles/students/{studentID}/aspx/EnrolmentInformation/StudentProfileStudentStatus.aspx/',
        }
        response = requests.get(
            enrollment_info_url, headers=enrollment_info_headers, cookies=cookies)
        response_text = response.text
        soup = BeautifulSoup(response_text, 'html.parser')
        enrollment_info = {
            'gov_student_number': soup.find('input', {'id': 'FormPlaceHolder_FormContent_DefaultContainer_DefaultContainer_PageContent_GovernmentStudentNumberEdit'})['value'],
            'barcode': soup.find('input', {'id': 'FormPlaceHolder_FormContent_DefaultContainer_DefaultContainer_PageContent_BarcodeEdit'})['value'],
            'year_level': soup.find('select', {'id': 'FormPlaceHolder_FormContent_DefaultContainer_DefaultContainer_PageContent_YearLevelEdit'}).find('option', selected=True).text,
            'homeroom': soup.find('select', {'id': 'FormPlaceHolder_FormContent_DefaultContainer_DefaultContainer_PageContent_HomeroomEdit'}).find('option', selected=True).text,
            'house': soup.find('select', {'id': 'FormPlaceHolder_FormContent_DefaultContainer_DefaultContainer_PageContent_HouseEdit'}).find('option', selected=True).text,
            'campus': soup.find('select', {'id': 'FormPlaceHolder_FormContent_DefaultContainer_DefaultContainer_PageContent_CampusEdit'}).find('option', selected=True).text,
            'status': soup.find('select', {'id': 'FormPlaceHolder_FormContent_DefaultContainer_DefaultContainer_PageContent_StatusEdit'}).find('option', selected=True).text
        }
        return enrollment_info
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/noscript')))

        wait.until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[2]/div[1]/nav/div[1]/div[1]/div[2]/div/a[1]')))
        # Locate the element containing the four-digit number
        element = driver.find_element_by_xpath(
            '/html/body/div[2]/div[1]/nav/div[1]/div[1]/div[2]/div/a[1]')
        href = element.get_attribute('href')

        # Use regex to extract the number (one or more digits)
        match = re.search(r'/(\d+)/aspx', href)
        if match:
            studentID = match.group(1)
            print(f"Number: {studentID}")

        # Extract cookies
        cookies = driver.get_cookies()

        # close the driver as we don't need it anymore
        driver.close()

        # Cookies: Extract from your browser and insert here
        cookies = {
            'AzureAppProxyAnalyticCookie_1971d3c1-f744-420e-a7b0-2bd2e07a23b5_https_1.3': cookies[1]["value"],
            'ASP.NET_SessionId': cookies[2]["value"],
            'adAuthCookie': cookies[0]["value"],
        }



        all_data['profile_details'] = fetch_profile_details(studentID)
        all_data['dashboard'] = fetch_dashboard_data(
            all_data['profile_details']['d']["UserGUID"])
        all_data['timetable'] = fetch_timetable_data(
            all_data['profile_details']['d']["UserGUID"])
        all_data['user_info'] = fetch_user_info(
            studentID, all_data['profile_details']['d']["UserGUID"])
        all_data['alerts'] = fetch_alerts(
            all_data['profile_details']['d']["UserGUID"])
        all_data['get_messages'] = fetch_messages(
            all_data['profile_details']['d']["UserGUID"])
        all_data['medical_status'] = fetch_medical_status(
            all_data['profile_details']['d']["CommunityID"], all_data['profile_details']['d']["UserGUID"])
        all_data['behavioural_history'] = fetch_behavioural_history(
            all_data['profile_details']['d']["UID"], all_data['profile_details']['d']["YearLevelCode"], all_data['profile_details']['d']["UserGUID"])
        all_data['commendations'] = fetch_commendations(
            all_data['profile_details']['d']["UserGUID"])
        all_data['EnrollmentInfo'] = fetch_enrollment_info(
            studentID, all_data['profile_details']['d']["UserGUID"])

        return True, all_data

    except Exception as e:
        print("Timeout or another exception occurred:", e)
        driver.close()
        return False


