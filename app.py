from __future__ import print_function
import os.path
from flask import Flask, request
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = Flask(__name__)

# Change ngrok listening port accordingly
# ./ngrok http 5000

@app.route("/test", methods=['POST'])
def test():
    print('Received test JSON: {}'.format(request.json))
    return 'ok'

# GITHUB ENDPOINT
@app.route("/github", methods=['POST'])
def github():
    print('Received event from GitHub: {}'.format(request.json))
    received_json = request.json
    event_type = request.headers["X-Github-Event"]
    # RELEASE EVENT
    if event_type == "release":
        # PUBLISHED RELEASE
        if received_json["action"] == "released":
            value1 = received_json["release"]["published_at"].replace("T", " ", 1).replace("Z", "", 1)
            # Galima atsirinkti pagal repozitoriją arba skirtingų paslaugų duomenis rinkti skirtingais endpoint adresais
            value2 = "Svetainė"
            value3 = received_json["release"]["tag_name"]
            value4 = 0
            google_api_post(value1, value2, value3, value4)
    else:
        print("false")

    return 'ok'

# GITHUB ACTIONS ENDPOINT pvz.
@app.route("/actions", methods=['POST'])
def actions():
    print('Received event from GitHub Actions: {}'.format(request.json))
    return 'ok'

# JIRA ENDPOINT pvz.
@app.route("/jira", methods=['POST'])
def jira():
    print('Received event from JIRA: {}'.format(request.json))
    return 'ok'

def google_api_post(value1, value2, value3, value4):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)
        # Call the Sheets API
        sheet = service.spreadsheets()

        values = [
            [
                value1, value2, value3, value4
            ]
        ]
        body = {
            'values': values
        }
        result = service.spreadsheets().values().append(
            spreadsheetId="1H0l-JEdy9j7tfq6iWSLRFFLdQ2nA2tV7lDux1Ge3TE4", range="Diegimai ir gedimai",
            valueInputOption="USER_ENTERED", body=body).execute()
        print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
        return result
        
    except HttpError as err:
        print(err)