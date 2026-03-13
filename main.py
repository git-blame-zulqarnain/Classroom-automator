from auth.google_auth import getClassroomService
from modules.courses import filterCourses, getCourses,printCourses


def main():
    service = getClassroomService()

    if service:
        print("Connected to Google Classroom API")

        all_courses = getCourses(service)
        relevant_courses=filterCourses(all_courses)

        print("Relevant Courses\n")

        printCourses(relevant_courses)

    

    else:
        print("Failed to connect to Google Classroom API")



if __name__ == "__main__":
    main()