import os
import io
import sys
import json


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.filePath import DOWNLOAD_FOLDER

from googleapiclient.http import MediaIoBaseDownload

from utils.classifier import classify_file
from utils.folder_manager import ensure_folder
from utils.parser import extract_number

from colorama import Fore, Style

DRY_RUN = True


def getCourseMaterials(service,course_id):
    
    try:
        results=service.courses().courseWorkMaterials().list(courseId=course_id).execute()
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return []

    materials=results.get('courseWorkMaterial',[])

    return materials



def getCourseWork(service,course_id):
    
    try:
        results=service.courses().courseWork().list(courseId=course_id).execute()
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return []

    coursework=results.get('courseWork',[])

    return coursework

def extractDriveFiles(materials):
    files=[]

    for m in materials:

        title = m.get("title")

        materials_list=m.get("materials",[])


        for item in materials_list:
            drive=item.get("driveFile")

            if drive:

                file_id=drive["driveFile"]["id"]

                name=drive["driveFile"]["title"]
                

                files.append({
                    "title": title,
                    "file_id": file_id,
                    "name": name
                })

    
    return files



def downloadFile(drive_service,file_id,filename,folder):

    ensure_folder(folder)

    filepath=os.path.join(folder,filename)

    if os.path.exists(filepath):
        print(Fore.YELLOW + f"File {filename} already exists, skipping download.")
        return

    if DRY_RUN:
        print(Fore.MAGENTA + f"DRY RUN: Would download {filename} to {filepath}")
        return

    request=drive_service.files().get_media(fileId=file_id)
    
    fh=io.FileIO(filepath,'wb')

    downloader=MediaIoBaseDownload(fh,request)

    done=False

    while not done:
        status,done=downloader.next_chunk()
    
    print(Fore.GREEN + f"Downloaded {filename} to {filepath}")


def normalize_course_name(name):

    name=name.lower()

    if "artificial intelligence" in name or "ai-2002" in name:
        return "Artificial Intelligence"
    
    if "operating systems" in name:
        return "Operating Systems"
    
    if "database" in name:
        return "Database Systems"
    
    if "probability" in name or "statistics" in name or "prob" in name or "stats" in name:
        return "Probability and Statistics"
    
    if "pakistan studies" in name:
        return "Pakistan Studies"

    if "sda" in name or "software design & analysis" in name:
        return "Software Design & Analysis"
    
    return name.title()


def downloadNotes(classroom,drive,courses):

    with open("data/relevant_courses.json") as f:
        relevant = json.load(f)["courses"]

    for course in courses:

        course_name=course["name"]
        isLab="lab" in course_name.lower()

        if course_name not in relevant:
            continue

        
        print()
        print(Fore.CYAN + "====================================")
        print(Fore.CYAN + "Scanning Course:", course_name)
        print(Fore.CYAN + "====================================")

        materials=getCourseMaterials(classroom,course["id"])
        coursework=getCourseWork(classroom,course["id"])

        materialFiles=extractDriveFiles(materials)
        assignmentFiles=extractDriveFiles(coursework)

        files=materialFiles + assignmentFiles

        if not files:
            print(Fore.YELLOW + "No files found for this course.")
            continue

        normalized_name=normalize_course_name(course_name)

        course_folder=os.path.join(DOWNLOAD_FOLDER, normalized_name)

        for f in files:

            filename=f["name"]
            title=f["title"]
            category=classify_file(filename + " " + title)
            number=extract_number(title)


            if category == "Assignments" and number:
                folder = os.path.join(course_folder, "Theory", "Assignments", f"Assignment {int(number)}")

            elif category=="Deliverable" and number:
                folder = os.path.join(course_folder, "Theory", "Deliverables", f"Deliverable {int(number)}")

            elif category == "Lecture Slides" and number:
                folder = os.path.join(course_folder, "Theory", "Lecture Slides", f"Lecture {int(number)}")
            
            elif category == "Homework" and number:
                folder = os.path.join(course_folder, "Theory", "Homework", f"Homework {int(number)}")

            elif category == "Class Activities" and number:
                folder = os.path.join(course_folder, "Theory", "Class Activities", f"Activity {int(number)}")

            elif category == "Lab Work":

                if number:
                    folder = os.path.join(course_folder, "Lab", "Lab Work", f"Lab {int(number)}")
                    
                else:
                    folder = os.path.join(course_folder, "Lab", "Lab Work")

            elif isLab:
                folder = os.path.join(course_folder, "Lab", category)

            else:
                folder = os.path.join(course_folder, "Theory", category)
            
            print(Fore.BLUE + f"Processing file: {filename} | Classified as: {category} | Title: {title}")

            downloadFile(drive,f["file_id"],filename,folder)

        
