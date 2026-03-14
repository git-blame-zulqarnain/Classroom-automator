import os
import io

from googleapiclient.http import MediaIoBaseDownload


def getCourseMaterials(service,course_id):
    results=service.courses().courseWorkMaterials().list(courseId=course_id).execute()

    materials=results.get('courseWorkMaterial',[])

    return materials