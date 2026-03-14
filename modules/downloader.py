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
    results=service.courses().courseWorkMaterials().list(courseId=course_id).execute()

    materials=results.get('courseWorkMaterial',[])

    return materials


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




def downloadNotes(classroom,drive,courses):

    with open("data/relevant_courses.json") as f:
        relevant = json.load(f)["courses"]

    for course in courses:

        course_name=course["name"]

        if course_name not in relevant:
            continue

        
        print()
        print(Fore.CYAN + "====================================")
        print(Fore.CYAN + "Scanning Course:", course_name)
        print(Fore.CYAN + "====================================")

        materials=getCourseMaterials(classroom,course["id"])

        files=extractDriveFiles(materials)

        if not files:
            print(Fore.YELLOW + "No files found for this course.")
            continue

        course_folder=os.path.join(DOWNLOAD_FOLDER, course_name.replace(" ", "_"))

        for f in files:

            filename=f["name"]
            title=f["title"]
            category=classify_file(filename)
            number=extract_number(title)


            if category=="Assignments" and number:
                folder=os.path.join(course_folder,"Theory","Assignments",f"Assignment {number}")
            
            elif category=="Lecture Slides" and number:
                folder=os.path.join(course_folder,"Theory","Lecture Slides",f"Lecture {number}")

            elif category=="Lab Work" and number:
                folder=os.path.join(course_folder,"Lab","Lab Work",f"Lab {number}")

            else:
                folder=os.path.join(course_folder,"Theory",category)
            
            print(Fore.BLUE + f"Processing file: {filename} | Classified as: {category} | Title: {title}")

            downloadFile(drive,f["file_id"],filename,folder)

        
    