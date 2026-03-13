from auth.google_auth import getClassroomService

service = getClassroomService()

if service:
    print("Connected to Google Classroom API")
else:
    print("Failed to connect to Google Classroom API")