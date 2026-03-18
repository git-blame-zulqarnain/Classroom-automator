from auth.google_auth import getServices
from modules.courses import filterCourses, getCourses, printCourses
from modules.assignments import getAssignments, getSubmissionStatus, stillDue, forMySection, sortByDue
from modules.downloader import downloadNotes
from modules.quiz_detector import detectQuizzes
from colorama import Fore, Style, init
from datetime import datetime
from zoneinfo import ZoneInfo
import sys

init(autoreset=True)

try:
    import msvcrt
    def get_key():
        return msvcrt.getch().decode('utf-8')
except ImportError:
    import tty, termios
    def get_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def formatDeadline(dueDate, dueTime):
    try:
        year = dueDate["year"]
        month = dueDate["month"]
        day = dueDate["day"]

        hour = dueTime.get("hours", 0)
        minute = dueTime.get("minutes", 0)

        due_obj = datetime(year, month, day, hour, minute, tzinfo=ZoneInfo("UTC"))
        due_pkt = due_obj.astimezone(ZoneInfo("Asia/Karachi"))

        return due_pkt.strftime("%d %B %Y | %H:%M")

    except Exception as e:
        return f"{dueDate} | {dueTime}"

def timeRemaining(dueDate, dueTime):
    try:
        year = dueDate["year"]
        month = dueDate["month"]
        day = dueDate["day"]

        hour = dueTime.get("hours", 0)
        minute = dueTime.get("minutes", 0)

        due_obj = datetime(year, month, day, hour, minute, tzinfo=ZoneInfo("UTC"))

        due_pkt = due_obj.astimezone(ZoneInfo("Asia/Karachi"))

        now_pkt = datetime.now(ZoneInfo("Asia/Karachi"))

        diff = due_pkt - now_pkt

        if diff.total_seconds() < 0:
            return "Past Due"

        days = diff.days
        hours = diff.seconds // 3600

        return f"{days}d {hours}h remaining"

    except Exception as e:
        return "Unknown"

    
def main():

    classroom, drive = getServices()

    print("\n" + Fore.MAGENTA + "="*60)
    print(Fore.MAGENTA + "\t\tCLASSROOM AUTOMATOR")
    print(Fore.MAGENTA + "="*60 + "\n")

    if not (classroom and drive):
        print(Fore.RED + "Failed to connect to Google APIs\n")
        return

    print(Fore.GREEN + "CONNECTED TO GOOGLE APIS\n")

    all_courses = getCourses(classroom)
    relevant_courses = filterCourses(all_courses)

    print(Fore.CYAN + "Relevant Courses\n")
    for idx, c in enumerate(relevant_courses, 1):
        print(Fore.YELLOW + f"{idx}. {c['name']}")
    print()

    while True:

        print(Fore.MAGENTA + "Options:")
        print(Fore.CYAN + "1. View Quizzes")
        print(Fore.CYAN + "2. View Assignments")
        print(Fore.CYAN + "3. Download Materials")
        print(Fore.RED + "q. Quit")
        print(Fore.MAGENTA + "Press a key to choose an option: ", end="", flush=True)

        choice = get_key()
        print(choice + "\n")

        if choice.lower() == 'q':
            break

        elif choice == "1":

            detectQuizzes(classroom, relevant_courses)
            print()

        elif choice == "2":

            for selected_course in relevant_courses:
                
                assignments = getAssignments(classroom, selected_course["id"])
                assignments = sortByDue(assignments)

                if not assignments:
                    continue

                for a in assignments:

                    if not stillDue(a["dueDate"]):
                        continue
                    
                    if not forMySection(a["title"]):
                        continue
                    
                    status = getSubmissionStatus(classroom, selected_course["id"], a["id"])
                    
                    if status != "TURNED_IN":
                        status= "PENDING"
                        
                    deadline_str = formatDeadline(a["dueDate"], a["dueTime"])
                    remaining = timeRemaining(a["dueDate"], a["dueTime"])
                    
                    print(Fore.CYAN + f"Course Name: {selected_course['name']}")
                    print(Fore.YELLOW + f"Assignment Title: {a['title']}")
                    print(Fore.GREEN + f"Deadline: {deadline_str}")
                    print(Fore.MAGENTA + f"Time remaining: {remaining}")
                    print(Fore.RED + f"Status: {status}\n")
            
            print()

        elif choice == "3":

            print(Fore.CYAN + f"\nDownloading course materials for all relevant courses...\n")
            
            downloadNotes(classroom, drive, relevant_courses)
            
            print(Fore.GREEN + "Download complete!\n")

        else:

            print(Fore.RED + "Invalid option\n")

            

if __name__ == "__main__":
    main()