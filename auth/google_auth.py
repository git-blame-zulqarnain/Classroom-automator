
import os
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.student-submissions.me.readonly",
    "https://www.googleapis.com/auth/classroom.announcements.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly"
]




def getServices():

    creds=None

    if os.path.exists('token.pkl'):
        with open('token.pkl', 'rb') as token:
            creds=pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file('API_Secrets/credentials.json', SCOPES)
                creds = flow.run_local_server(port=51647)
            except FileNotFoundError:
                print("Error: 'API_Secrets/credentials.json' file not found. Please provide the correct credentials file.")
                return None
            except Exception as e:
                print(f"An error occurred during authentication: {e}")
                import traceback
                traceback.print_exc()
                return None 

        with open("token.pkl", 'wb') as token:
                pickle.dump(creds, token)


    classroom=build('classroom', 'v1', credentials=creds)
    drive=build('drive', 'v3', credentials=creds)

    return classroom,drive