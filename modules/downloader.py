import os
import io
import time
import sys
import json


from concurrent.futures import ThreadPoolExecutor
from config.settings import MY_SECTION
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.filePath import DOWNLOAD_FOLDER

from googleapiclient.http import MediaIoBaseDownload

from utils.classifier import classify_file
from utils.folder_manager import ensure_folder
from utils.parser import extract_number,sanitize_filename

from colorama import Fore, Style

from utils.dashboard import generate_dashboard

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

def getAnnouncements(service,course_id):

    try:
        results=service.courses().announcements().list(courseId=course_id).execute()
    except Exception as e:
        import traceback
        traceback.print_exc()
        return []

    announcements=results.get("announcements",[])

    return announcements


def extractAnnouncementFiles(announcements):

    files=[]

    for a in announcements:

        title=a.get("text","Announcement")

        materials=a.get("materials",[])

        for item in materials:
            
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

    time.sleep(0.15)
    
    print(Fore.GREEN + f"Downloaded {filename} to {filepath}")


def mySection(title):

    title=title.upper()

    otherSections=["B","C","D","E","F","G"]
    

    for sec in otherSections:
        if f"SECTION {sec}" in title or f"SEC {sec}" in title or f"CS-{sec}" in title or f"CS {sec}" in title:
            return False

    if f"SECTION {MY_SECTION}" in title or f"SEC {MY_SECTION}" in title or f"CS-{MY_SECTION}" in title or f"CS {MY_SECTION}" in title:
        return True
    

    return True

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

        announcement=getAnnouncements(classroom,course["id"])
        announcementFiles=extractAnnouncementFiles(announcement)

        materialFiles=extractDriveFiles(materials)
        assignmentFiles=extractDriveFiles(coursework)

        files=materialFiles + assignmentFiles + announcementFiles

        if not files:
            print(Fore.YELLOW + "No files found for this course.")
            continue

        normalized_name=normalize_course_name(course_name)

        course_folder=os.path.join(DOWNLOAD_FOLDER, normalized_name)

        seen=set()

        tasks=[]

        for f in files:

            if f["file_id"] in seen:
                continue

            seen.add(f["file_id"])

            filename=sanitize_filename(f["name"])
            title=f["title"]
            category=classify_file(filename + " " + title)
            number=extract_number(title)


            if category == "Assignments" and number:
                base = os.path.join(course_folder, "Theory", "Assignments", f"Assignment {int(number)}")

                if mySection(title):
                    folder = base
                else:
                    folder = os.path.join(base, "0. Other Sections")

            elif category=="Deliverable" and number:
                base = os.path.join(course_folder, "Theory", "Deliverables", f"Deliverable {int(number)}")

                if mySection(title):
                    folder = base
                else:
                    folder = os.path.join(base, "0. Other Sections")

            elif category == "Lecture Slides" and number:
                folder = os.path.join(course_folder, "Theory", "Lecture Slides", f"Lecture {int(number)}")
            
            elif category == "Homework" and number:
                base = os.path.join(course_folder, "Theory", "Homework", f"Homework {int(number)}")

                if mySection(title):
                    folder = base
                else:
                    folder = os.path.join(base, "0. Other Sections")


            elif category == "Lab Work":
                if number:
                    base = os.path.join(course_folder, "Lab", "Lab Work", f"Lab {int(number)}")

                    if mySection(title):
                        folder = base
                    else:
                        folder=os.path.join(base, "0. Other Sections")
                        
                else:
                    folder = os.path.join(course_folder, "Lab", "Lab Work")

            elif isLab:
                folder = os.path.join(course_folder, "Lab", category)

            else:
                folder = os.path.join(course_folder, "Theory", category)
            
            print(Fore.BLUE + f"Processing file: {filename} | Classified as: {category} | Title: {title}")

            tasks.append((f["file_id"], filename, folder))
    
        print(Fore.CYAN + f"Total files to download for {course_name}: {len(tasks)}")

        print(Fore.CYAN + f"Total unique files detected: {len(seen)}")



        with ThreadPoolExecutor(max_workers=3) as executor:
            
            futures = [executor.submit(downloadFile, drive, file_id, filename, folder) for file_id, filename, folder in tasks]

            for _ in tqdm(futures, desc=f"Downloading {course_name}", unit="file"):
                _.result()


    generate_dashboard(DOWNLOAD_FOLDER)

        
