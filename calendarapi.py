from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def auth():
    """Get authentication token fot the module to work
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)


def get_calendar_id(name):
    """
    loop over the calendars in calendarList to get the calendar Id
    by the given name
    """
    service = auth()
    page_token = None
    while True:
        calendar_list = service.calendarList().list(
            pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            if calendar_list_entry['summary'] == name:
                calendar_id = calendar_list_entry['id']
                return calendar_id
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
    raise 'NoCalendarIdEntryError'


def create_event(data):
    """ Create Google Calendar Event with given Information
    data format: {shift': '', 'start_date': '', 'start_time': '',
     'end_time': '', 'end_date': ''}
    """
    service = auth()
    work_id = get_calendar_id('Work')

    event = {
        'summary': "".join(data['shift']),
        'location': 'Prospekt Dzerzhinskogo 104, Minsk 220089',
        'start': {
            'dateTime': '{}T{}'.format(
                data['start_date'], data['start_time']),
            'timeZone': 'Europe/Minsk',
        },
        'end': {
            'dateTime': '{}T{}'.format(
                data['end_date'], data['end_time']),
            'timeZone': 'Europe/Minsk',
        },
        'reminders': {
            'useDefault': True,
        },
    }

    event = service.events().insert(calendarId=work_id, body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))
