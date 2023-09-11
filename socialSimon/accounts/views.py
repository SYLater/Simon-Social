import json
import re  # for regular expression

import requests
from bs4 import BeautifulSoup
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import HttpResponse
from django.shortcuts import redirect, render
from helium import click, start_chrome, write
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .models import StudentProfile

from .forms import UserRegistrationForm


def login(request):
    form = UserRegistrationForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            user_email = form.cleaned_data['user_email']
            password = form.cleaned_data['password']

            print("Username: " + user_email, " Password: " + password) 

            # Check if user exists in Django database
            user = authenticate(username=user_email, password=password)

            if user is not None:
                print("User authenticated")
                auth_login(request, user)
                return redirect("/")
            
            success ,data = simonAuthChk(username=user_email, password=password)

            if success:  # Check with Simon

                print("User authenticated with Simon")
                
                user_instance = form.save(commit=False)  # Don't commit yet, we'll update some fields
                print("Created user in database")

                # Update User instance with new data
                FullName = data['profile_details']['d']['FullName']
                first_name, last_name = FullName.split(" ", 1)

                if "@" in user_email:
                    user_instance.user_Name = user_email.split("@")[0]
                    user_instance.user_email = user_email
                else:
                    user_instance.user_Name = user_email
                user_instance.user_firstName = first_name
                user_instance.user_lastName = last_name
                user_instance.cookies = json.dumps(data['cookies'])
                
                user_instance.save()  # Now save the User instance

                # Create and save the associated StudentProfile
                StudentProfile.objects.create(
                    user=user_instance,
                    studentGUID=data['profile_details']['d']['UserGUID'],
                    communityID=data['profile_details']['d']['CommunityID'],
                    communityUID=data['profile_details']['d']['UID'],
                    FullName=FullName,
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
                return redirect('login')
            else:
                print("Incorrect credentials or you don't have a Simon account.")
                messages.error(request, "Incorrect credentials or you don't have a Simon account.")
    
    else:
        form = UserRegistrationForm()
       
    return render(request, "accounts/login.html", {"form": form})

def scrap(request):
    print("Scraping")

    result = simonAuthChk(username="milll18@s.padua.vic.edu.au", password="ghd931PC")
    if result is not None:
        success, data = result
        print("Authentication successful.")
    else:
        print("Authentication failed.")
        return redirect("/login")
    
    studentGUID = data['profile_details']['d']['UserGUID']
    communityID = data['profile_details']['d']['CommunityID']
    communityUID = data['profile_details']['d']['UID']
    FullName = data['profile_details']['d']['FullName']
    first_name, last_name = FullName.split(" ", 1)
    YearLevelCode = data['profile_details']['d']['YearLevelCode']
    HouseDescription = data['profile_details']['d']['HouseDescription']
    HomeroomCode = data['profile_details']['d']['HomeroomCode']
    HomeroomDescription = data['profile_details']['d']['HomeroomDescription']
    HomeroomTeachers = data['profile_details']['d']['HomeroomTeachers']  # This is a list
    StudentID = data['profile_details']['d']['StudentID']
    StudentPersonalRefId = data['profile_details']['d'].get('StudentPersonalRefId', None)  # Using get in case the key doesn't exist
    NoteCount = data['profile_details']['d']['NoteCount']
    NoteImportantCount = data['profile_details']['d']['NoteImportantCount']
    ImportantMedicalWarning = data['profile_details']['d']['ImportantMedicalWarning']

    return redirect("/login")

def simonAuthChk(username, password):
    #helium 3.2.5

    chromedriver_path  = 'accounts/chromedriver.exe'  # Update this path

    url = 'https://intranet.padua.vic.edu.au/Login/Default.aspx?ReturnUrl=%2F'

    service = Service(executable_path=chromedriver_path )
    driver = start_chrome(url, headless=False)

    # Fill in login details
    write(username, into='Username')
    write(password, into='Password')

    # Click the login button
    click(('Sign in'))

    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/noscript')))
        

        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/nav/div[1]/div[1]/div[2]/div/a[1]')))    
        # Locate the element containing the four-digit number
        element = driver.find_element_by_xpath('/html/body/div[2]/div[1]/nav/div[1]/div[1]/div[2]/div/a[1]')
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

        # Create a dictionary to hold the headers
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
        all_data = {}

        # Fetch profile details
        profile_details_url = 'https://intranet.padua.vic.edu.au/WebModules/Profiles/Student/StudentProfiles.asmx/StudentProfileDetails'
        profile_headers = {
            **common_headers,
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Referer': f'https://intranet.padua.vic.edu.au/profiles/students/{studentID}/aspx/GeneralInformation/StudentProfilePersonalDetails.aspx/',
        }
        payload = json.dumps({"studentId": studentID})
        response = requests.post(profile_details_url, headers=profile_headers, cookies=cookies, data=payload)
        response_dict = response.json()
        all_data['profile_details'] = response_dict
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
    #helium 3.2.5

    CHROMEDRIVER_PATH = 'accounts/chromedriver.exe'  # Update this path

    url = 'https://intranet.padua.vic.edu.au/Login/Default.aspx?ReturnUrl=%2F'
    TimeTable = 'https://intranet.padua.vic.edu.au/WebModules/Timetables/StudentTimetable.aspx'

    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = start_chrome(url, headless=True)

    # Fill in login details
    write(username, into='Username')
    write(password, into='Password')

    # Click the login button
    click(('Sign in'))

    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/noscript')))
        print('worked')

        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/nav/div[1]/div[1]/div[2]/div/a[1]')))    
        # Locate the element containing the four-digit number
        element = driver.find_element_by_xpath('/html/body/div[2]/div[1]/nav/div[1]/div[1]/div[2]/div/a[1]')
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

        # Create a dictionary to hold the headers
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
        all_data = {}

        # Fetch profile details
        profile_details_url = 'https://intranet.padua.vic.edu.au/WebModules/Profiles/Student/StudentProfiles.asmx/StudentProfileDetails'
        profile_headers = {
            **common_headers,
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Referer': f'https://intranet.padua.vic.edu.au/profiles/students/{studentID}/aspx/GeneralInformation/StudentProfilePersonalDetails.aspx/',
        }
        payload = json.dumps({"studentId": studentID})
        response = requests.post(profile_details_url, headers=profile_headers, cookies=cookies, data=payload)
        response_dict = response.json()
        print(response_dict)
        all_data['profile_details'] = response_dict
        all_data['cookies'] = cookies
        

        studentGUID = response_dict['d']['UserGUID']
        communityID = response_dict['d']['CommunityID']
        communityUID = response_dict['d']['UID']
        FullName = response_dict['d']['FullName']
        YearLevelCode = response_dict['d']['YearLevelCode']
        HouseDescription = response_dict['d']['HouseDescription']
        HomeroomCode = response_dict['d']['HomeroomCode']
        HomeroomDescription = response_dict['d']['HomeroomDescription']
        HomeroomTeachers = response_dict['d']['HomeroomTeachers']  # This is a list
        StudentID = response_dict['d']['StudentID']
        StudentPersonalRefId = response_dict['d'].get('StudentPersonalRefId', None)  # Using get in case the key doesn't exist
        NoteCount = response_dict['d']['NoteCount']
        NoteImportantCount = response_dict['d']['NoteImportantCount']
        ImportantMedicalWarning = response_dict['d']['ImportantMedicalWarning']

        # Fetch dashboard data
        dashboard_url = 'https://intranet.padua.vic.edu.au/WebModules/Profiles/Student/GeneralInformation/StudentDashboard.aspx/GetDashboardData'
        dashboard_headers = {
            **common_headers,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://intranet.padua.vic.edu.au/WebModules/Profiles/Student/GeneralInformation/StudentDashboard.aspx?UserGUID={studentGUID}',
        }
        payload = json.dumps({"guidString": studentGUID, "semester": 33})
        response = requests.post(dashboard_url, headers=dashboard_headers, cookies=cookies, data=payload)
        response_dict = response.json()
        all_data['dashboard'] = response_dict

        # Fetch timetable data
        timetable_url = 'https://intranet.padua.vic.edu.au/Default.asmx/GetUserInfo?1693648835712'
        timetable_headers = {
            **common_headers,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/json; charset=utf-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://intranet.padua.vic.edu.au/WebModules/Profiles/Student/GeneralInformation/StudentProfileTimetable.aspx?UserGUID={studentGUID}',
        }
        response = requests.post(timetable_url, headers=timetable_headers, cookies=cookies)
        response_dict = response.json()
        all_data['timetable'] = response_dict

        # Fetch User Information
        user_info_url = 'https://intranet.padua.vic.edu.au/Default.asmx/UserInformation'
        user_info_headers = {
            **common_headers,
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Referer': f'https://intranet.padua.vic.edu.au/profiles/students/{studentID}/aspx/GeneralInformation/StudentProfileTimetable.aspx/',
        }

        # The payload appears to be just "{}" based on the Content-Length: 2
        payload = json.dumps({})
        response = requests.post(user_info_url, headers=user_info_headers, cookies=cookies, data=payload)
        response_dict = response.json()
        all_data['user_info'] = response_dict

        # Fetch Alerts
        alerts_url = 'https://intranet.padua.vic.edu.au/Default.asmx/GetAlerts'
        alerts_headers = {
            **common_headers,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/json; charset=utf-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://intranet.padua.vic.edu.au/WebModules/Profiles/Student/GeneralInformation/StudentProfileTimetable.aspx?UserGUID={studentGUID}',
        }

        # The Content-Length is 0, so no payload is needed
        response = requests.post(alerts_url, headers=alerts_headers, cookies=cookies)
        response_dict = response.json()
        all_data['alerts'] = response_dict

        # Fetch Messages
        get_messages_url = 'https://intranet.padua.vic.edu.au/Default.asmx/GetMessages'
        get_messages_headers = {
            **common_headers,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/json; charset=utf-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://intranet.padua.vic.edu.au/WebModules/Profiles/Student/GeneralInformation/StudentProfileTimetable.aspx?UserGUID={studentGUID}',
        }

        # The payload appears to be empty based on Content-Length: 0
        payload = json.dumps({})  # Empty payload
        response = requests.post(get_messages_url, headers=get_messages_headers, cookies=cookies, data=payload)
        response_dict = response.json()
        all_data['get_messages'] = response_dict

        # Fetch Medical Student Status
        medical_status_url = 'https://intranet.padua.vic.edu.au/Webmodules/medical/Medical.asmx/GETmedicalStudentStatus'
        medical_status_headers = {
            **common_headers,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://intranet.padua.vic.edu.au/WebModules/Profiles/Student/MedicalInformation/MedicalStatus.aspx?UserGUID={studentGUID}',
        }

        # The payload appears to be 22 characters long, replace with your actual payload
        payload = json.dumps({"communityID": communityID})  # Replace with your actual payload
        response = requests.post(medical_status_url, headers=medical_status_headers, cookies=cookies, data=payload)
        response_dict = response.json()
        all_data['medical_status'] = response_dict

        # Fetch Behavioral History
        behavioural_history_url = 'https://intranet.padua.vic.edu.au/WebServices/BehaviouralTracking.asmx/GetStudentProfileBehaviouralHistory?1693652261176'
        behavioural_history_headers = {
            **common_headers,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://intranet.padua.vic.edu.au/WebModules/Profiles/Student/SocialBehaviour/StudentProfileBehaviouralHistory.aspx?UserGUID={studentGUID}',
        }

        # The payload should be 72 bytes long, replace with your actual payload
        payload = json.dumps({"selectedAcademicYearID": 21,"communityUID": communityUID ,"yearLevelCode": YearLevelCode})  # Replace with your actual payload

        response = requests.post(behavioural_history_url, headers=behavioural_history_headers, cookies=cookies, data=payload)
        response_dict = response.json()
        all_data['behavioural_history'] = response_dict

        # Fetch Behavioral Tracking Commendations
        commendations_url = 'https://intranet.padua.vic.edu.au/WebServices/BehaviouralTracking.asmx/GetWorkDeskCommendationsPaged'
        commendations_headers = {
            **common_headers,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://intranet.padua.vic.edu.au/WebModules/Profiles/Student/SocialBehaviour/StudentProfileBehaviouralHistory.aspx?UserGUID={studentGUID}',
        }

        # Payload
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

        response = requests.post(commendations_url, headers=commendations_headers, cookies=cookies, data=commendations_payload)
        response_dict = response.json()
        all_data['commendations'] = response_dict
        # Fetch Student Profile Details
        profile_details_url = 'https://intranet.padua.vic.edu.au/WebModules/Profiles/Student/StudentProfiles.asmx/StudentProfileDetails'
        profile_details_headers = {
            **common_headers,
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Referer': f'https://intranet.padua.vic.edu.au/profiles/students/{studentID}/aspx/EnrolmentInformation/StudentProfileStudentStatus.aspx/',
        }

        # The Content-Length is 20, so a payload is likely needed
        payload = json.dumps({"studentId": studentID})  # Replace with your actual payload
        response = requests.post(profile_details_url, headers=profile_details_headers, cookies=cookies, data=payload)
        response_dict = response.json()
        all_data['profile_details'] = response_dict
        # Fetch Student Enrollment Information
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

        response = requests.get(enrollment_info_url, headers=enrollment_info_headers, cookies=cookies)
        response_text = response.text

        # Parse the HTML content


        soup = BeautifulSoup(response_text, 'html.parser')

        # Extract student information
        gov_student_number = soup.find('input', {'id': 'FormPlaceHolder_FormContent_DefaultContainer_DefaultContainer_PageContent_GovernmentStudentNumberEdit'})['value']
        barcode = soup.find('input', {'id': 'FormPlaceHolder_FormContent_DefaultContainer_DefaultContainer_PageContent_BarcodeEdit'})['value']
        year_level = soup.find('select', {'id': 'FormPlaceHolder_FormContent_DefaultContainer_DefaultContainer_PageContent_YearLevelEdit'}).find('option', selected=True).text
        homeroom = soup.find('select', {'id': 'FormPlaceHolder_FormContent_DefaultContainer_DefaultContainer_PageContent_HomeroomEdit'}).find('option', selected=True).text
        house = soup.find('select', {'id': 'FormPlaceHolder_FormContent_DefaultContainer_DefaultContainer_PageContent_HouseEdit'}).find('option', selected=True).text
        campus = soup.find('select', {'id': 'FormPlaceHolder_FormContent_DefaultContainer_DefaultContainer_PageContent_CampusEdit'}).find('option', selected=True).text
        status = soup.find('select', {'id': 'FormPlaceHolder_FormContent_DefaultContainer_DefaultContainer_PageContent_StatusEdit'}).find('option', selected=True).text
        
        # Extract student information
        enrollment_info = {}
        enrollment_info['gov_student_number'] = soup.find('input', {'id': 'FormPlaceHolder_FormContent_DefaultContainer_DefaultContainer_PageContent_GovernmentStudentNumberEdit'})['value']
        enrollment_info['barcode'] = soup.find('input', {'id': 'FormPlaceHolder_FormContent_DefaultContainer_DefaultContainer_PageContent_BarcodeEdit'})['value']
        enrollment_info['year_level'] = soup.find('select', {'id': 'FormPlaceHolder_FormContent_DefaultContainer_DefaultContainer_PageContent_YearLevelEdit'}).find('option', selected=True).text
        enrollment_info['homeroom'] = soup.find('select', {'id': 'FormPlaceHolder_FormContent_DefaultContainer_DefaultContainer_PageContent_HomeroomEdit'}).find('option', selected=True).text
        enrollment_info['house'] = soup.find('select', {'id': 'FormPlaceHolder_FormContent_DefaultContainer_DefaultContainer_PageContent_HouseEdit'}).find('option', selected=True).text
        enrollment_info['campus'] = soup.find('select', {'id': 'FormPlaceHolder_FormContent_DefaultContainer_DefaultContainer_PageContent_CampusEdit'}).find('option', selected=True).text
        enrollment_info['status'] = soup.find('select', {'id': 'FormPlaceHolder_FormContent_DefaultContainer_DefaultContainer_PageContent_StatusEdit'}).find('option', selected=True).text
        
        # Add the enrollment info to the all_data dictionary
        all_data['EnrollmentInfo'] = enrollment_info

        # Extract entry and exit history
        entry_exit_table = soup.find('table', {'class': 'table'})
        entry_exit_history = []
        for row in entry_exit_table.find_all('tr')[1:]:
            date, action = [cell.text for cell in row.find_all('td')]
            entry_exit_history.append({'Date': date, 'Action': action})

        # Print or store the extracted information
        print(f'Government Student Number: {gov_student_number}')
        print(f'Barcode: {barcode}')
        print(f'Year Level: {year_level}')
        print(f'Homeroom: {homeroom}')
        print(f'House: {house}')
        print(f'Campus: {campus}')
        print(f'Status: {status}')
        print('Entry and Exit History:', entry_exit_history)
     



        #print(response_dict)
       # print_keys_recursively(response_dict)

        # keys_within_d = response_dict['d'].keys()
        # print(keys_within_d)
        # Sample function to list all attendance records for a specific semester
        # def list_attendance_records_for_semester(data, semester_name):
        #     semester_data = data['d']['SemesterBasedData']
        #     attendance_records = []

        #     for semester in semester_data:
        #         if semester['Name'] == semester_name:
        #             attendance_records = semester.get('ParentNotifiedAbsences', [])
        #             break
        #     else:
        #         return f"No records found for semester: {semester_name}"
            
        #     return attendance_records

        # attendance_records_2023_S2 = list_attendance_records_for_semester(response_dict, "2023, Semester 2")
        # print(attendance_records_2023_S2)
        # print("Amount of records:", len(attendance_records_2023_S2))
 


        driver.close()
        return True
    except Exception as e:
        print("Timeout or another exception occurred:", e)
        driver.close()
        return False
