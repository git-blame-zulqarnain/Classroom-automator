

def getCourses(service):

    results=service.courses().list().execute()


    courses=results.get('courses',[])

    for course in courses:
        print(course['name'],"| Section:",course.get('section','N/A',),"| ID:",course['id'])

    return courses
    

