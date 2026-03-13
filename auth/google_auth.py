import os
import pickle


from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


SCOPES=[ "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.coursework.me.readonly",
    "https://www.googleapis.com/auth/classroom.announcements.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def getClassroomService():

    creds=None

    if os.path.exists('token.pk1'):
        with open('token.pk1', 'rb') as token:
            creds=pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow=InstalledAppFlow.from_client_secrets_file('API_Secrets\credentials.json', SCOPES)


            creds=flow.run_local_server(port=0)

        with open("token.pk1", 'wb') as token:
                pickle.dump(creds, token)


    service=build('classroom', 'v1', credentials=creds)


    return service


print(getClassroomService())
            

