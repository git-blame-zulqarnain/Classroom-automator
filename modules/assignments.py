

def getAssignments(service,course_id):

    results=service.courses().courseWork().list( courseId=course_id).execute()

    courseWork=results.get('courseWork',[])

    assignments=[]

    for work in courseWork:

        assignment={
            "id":work["id"],
            "title":work["title"],
            "description":work.get("description",""),
            "dueDate":work.get("dueDate",{}),
            "dueTime":work.get("dueTime",{})
        }

        assignments.append(assignment)

    return assignments




def getSubmissionStatus(service,course_id,courseWork_id):

    results=service.courses().courseWork().studentSubmissions().list(courseId=course_id,courseWorkId=courseWork_id).execute()


    submissions=results.get('studentSubmissions',[])


    if not submissions:
        return "UNKNOWN"
    
    return submissions[0].get("state","UNKNOWN")

