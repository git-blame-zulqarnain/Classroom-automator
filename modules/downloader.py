import os
import io
from config.filePath import DOWNLOAD_FOLDER

from googleapiclient.http import MediaIoBaseDownload

from config.filePath import DOWNLOAD_FOLDER


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

    fh=io.FileIO(filepath,'wb')

    downloader=MediaIoBaseDownload(fh,request)

    done=False

    while not done:
        status,done=downloader.next_chunk()
    
    print(f"Downloaded {filename} to {filepath}")




def downloadNotes(classroom,drive,courses):

    for course in courses:

        course_name=course["name"]

        print("\nScanning",course_name)
        materials=getCourseMaterials(classroom,course["id"])

        files=extractDriveFiles(materials)

        course_folder=os.path.join(DOWNLOAD_FOLDER, course_name.replace(" ", "_"))

        for f in files:
            downloadFile(drive,f["file_id"],f["name"],course_folder)

        
    