from auth.google_auth import getClassroomService
from modules.courses import filterCourses, getCourses,printCourses
from modules.assignments import (getAssignments,getSubmissionStatus,stillDue,forMySection,sortByDue)
from colorama import Fore,Style,init



init(autoreset=True)

def main():

    SHOW_NO_DUE = input("Show assignments with NO due date? (y/n): ").lower() == "y"

    service = getClassroomService()

    if service:
        print("Connected to Google Classroom API")

        all_courses = getCourses(service)
        relevant_courses=filterCourses(all_courses)

        print("Relevant Courses\n")

        printCourses(relevant_courses)

        print("\n Fetching Assignments \n")

        for course in relevant_courses:
            
            assignments=getAssignments(service,course["id"])

            assignments=sortByDue(assignments)

            if not assignments:
                continue

            print(Fore.CYAN +"Course: ",course["name"])


            for a in assignments:

                dueDate=a["dueDate"]

                if not dueDate:
                    if not SHOW_NO_DUE:
                        continue
                elif not stillDue(dueDate):
                    continue

                if not forMySection(a["title"]):
                    continue

                status=getSubmissionStatus(service,course["id"],a["id"])

                if status!="TURNED_IN":
                    print(Fore.RED + "Pending :", a["title"], "| Due:", a["dueDate"] , " | Time:", a["dueTime"])

                else:
                    print(Fore.GREEN + "Submitted :", a["title"], "| Due:", a["dueDate"] , " | Time:", a["dueTime"])


            print()
    

    else:
        print("Failed to connect to Google Classroom API")


if __name__ == "__main__":
    main()