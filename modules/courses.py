import json


def getCourses(service):

    results=service.courses().list().execute()


    courses=results.get('courses',[])

    return courses
    

def loadRelevantCourses():
    with open('data/relevant_courses.json',"r") as f:
        data=json.load(f)



    return data["courses"]


def filterCourses(courses):

    relevant_names=loadRelevantCourses()

    filtered=[]

    for course in courses:

        if course["name"] in relevant_names:
            filtered.append(course)

    return filtered


def printCourses(courses):

    for course in courses:
        print(course['name'],"| Section:",course.get('section','N/A',),"| ID:",course['id'])

        