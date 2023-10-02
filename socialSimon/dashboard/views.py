from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import requests
import json

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
    
        url = 'https://intranet.padua.vic.edu.au/WebModules/Timetables/MasterTimetable.aspx'
        
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'intranet.padua.vic.edu.au',
            'Origin': 'https://intranet.padua.vic.edu.au',
            'Referer': 'https://intranet.padua.vic.edu.au/WebModules/Timetables/MasterTimetable.aspx',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            **common_headers  # Adding the common headers
        }
        
        payload_data = {}  # TODO: Fill in the payload data as required by the server.
        
        response = requests.post(url, headers=headers, cookies=cookies, data=payload_data)
        
        return response.text

def dashboard(request):
    # Fetch timetable data
    cookies = json.loads(request.user.cookies)
    timetable_data = fetch_timetable(cookies)
    print(timetable_data)
    context = {
        'student': request.user,  # Assuming the user model has the necessary attributes
        'timetable': timetable_data  # Pass the timetable data to the template
    }
    return render(request, 'dashboard/dashboard.html', context)



def timetable(request):
    user = request.user
    cookies = json.loads(user.cookies)
    timetable = fetch_timetable(cookies)
    print(timetable)

    return render(request, 'dashboard/timetable.html')

