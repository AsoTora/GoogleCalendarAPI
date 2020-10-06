import flask, os
import googleapiclient
import google.oauth2.credentials
import google_auth_oauthlib.flow

from dotenv import load_dotenv
load_dotenv()
API_SERVICE_NAME = os.getenv("API_SERVICE_NAME")
API_VERSION = os.getenv("API_VERSION")

def build_credentials():
    if not is_logged_in():
        raise Exception('User must be logged in')

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    return googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=flask.session['credentials'])


def credentials_to_dict(credentials):
    return {'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes}

def is_logged_in():
    return True if 'credentials' in flask.session else False

def print_index_table():
    return ('<table>' +
        '<tr><td><a href="/test">Test an API request</a></td>' +
        '<td>Submit an API request and see a formatted JSON response. ' +
        '    Go through the authorization flow if there are no stored ' +
        '    credentials for the user.</td></tr>' +
        '<tr><td><a href="/auth">Test the auth flow directly</a></td>' +
        '<td>Go directly to the authorization flow. If there are stored ' +
        '    credentials, you still might not be prompted to reauthorize ' +
        '    the application.</td></tr>' +
        '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
        '<td>Revoke the access token associated with the current user ' +
        '    session. After revoking credentials, if you go to the test ' +
        '    page, you should see an <code>invalid_grant</code> error.' +
        '</td></tr>' +
        '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
        '<td>Clear the access token currently stored in the user session. ' +
        '    After clearing the token, if you <a href="/test">test the ' +
        '    API request</a> again, you should go back to the auth flow.' +
        '</td></tr></table>')


def get_calendar_id(name):
    """
    Loop over the calendars in calendarList to get the calendar Id
    by the given name
    """
    calendar = build_credentials()

    page_token = None
    while True:
        calendar_list = calendar.calendarList().list(
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
    session = build_credentials()
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

    event = session.events().insert(calendarId=work_id, body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))