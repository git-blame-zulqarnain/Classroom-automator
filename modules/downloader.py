import os
import io
import json
from config.filePath import DOWNLOAD_FOLDER

from googleapiclient.http import MediaIoBaseDownload
from utils.classifier import classify_file
from utils.folder_manager import ensure_folder
from utils.parser import extract_number

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
    
    os.makedirs(folder,exist_ok=True)

    request=drive_service.files().get_media(fileId=file_id)

    filepath=os.path.join(folder,filename)

    if os.path.exists(filepath):
        print(f"File {filename} already exists, skipping download.")
        return

    fh=io.FileIO(filepath,'wb')

    downloader=MediaIoBaseDownload(fh,request)

    done=False

    while not done:
        status,done=downloader.next_chunk()
    
    print(f"Downloaded {filename} to {filepath}")




def downloadNotes(classroom,drive,courses):

    with open("data/relevant_courses.json") as f:
        relevant = json.load(f)["courses"]

    for course in courses:

        course_name=course["name"]

        if course_name not in relevant:
            continue

        
        print("\nScanning",course_name)

        materials=getCourseMaterials(classroom,course["id"])

        files=extractDriveFiles(materials)

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
            
            ensure_folder(folder)

            downloadFile(drive,f["file_id"],filename,course_folder)

        
    