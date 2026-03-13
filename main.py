from auth.google_auth import getClassroomService
from modules.courses import getCourses


def main():
    service = getClassroomService()

    if service:
        print("Connected to Google Classroom API")
        courses = getCourses(service)

    else:
        print("Failed to connect to Google Classroom API")



if __name__ == "__main__":
    main()