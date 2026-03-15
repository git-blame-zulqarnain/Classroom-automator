from auth.google_auth import getServices
from modules.courses import filterCourses, getCourses,printCourses
from modules.assignments import (getAssignments,getSubmissionStatus,stillDue,forMySection,sortByDue)
from colorama import Fore,Style,init
from modules.downloader import (getCourseMaterials,extractDriveFiles,downloadFile,downloadNotes)

init(autoreset=True)


    

def main():

    SHOW_NO_DUE = input("Show assignments with NO due date? (y/n): ").lower() == "y"

    classroom, drive = getServices()

    if classroom and drive:
        print("Connected to Google APIs")

        all_courses = getCourses(classroom)
        relevant_courses=filterCourses(all_courses)

        print("Relevant Courses\n")

        printCourses(relevant_courses)

        print("\n Fetching Assignments \n")

        for course in relevant_courses:
            
            assignments=getAssignments(classroom,course["id"])

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

                status=getSubmissionStatus(classroom,course["id"],a["id"])

                if status!="TURNED_IN":
                    print(Fore.RED + "Pending :", a["title"], "| Due:", a["dueDate"] , " | Time:", a["dueTime"])

                else:
                    print(Fore.GREEN + "Submitted :", a["title"], "| Due:", a["dueDate"] , " | Time:", a["dueTime"])


            print()
    

        choice=input("Do you want to download course materials? (y/n): ").lower()

        if choice=="y":
            print(Fore.CYAN + "\nDownloading course materials...\n" )
            
            downloadNotes(classroom,drive,relevant_courses)
            

    else:
        print("Failed to connect ")


if __name__ == "__main__":
    
    main()
