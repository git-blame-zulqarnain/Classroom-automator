from datetime import date
from config.settings import MY_SECTION


def forMySection(title):
    title=title.upper()

    otherSections=["B","C","D","E","F","G"]
    

    for sec in otherSections:
        if f"SECTION {sec}" in title or f"SEC {sec}" in title or f"CS-{sec}" in title or f"CS {sec}" in title:
            return False

    if f"SECTION {MY_SECTION}" in title or f"SEC {MY_SECTION}" in title or f"CS-{MY_SECTION}" in title or f"CS {MY_SECTION}" in title:
        return True
    

    return True


def stillDue(dueDate):

    if not dueDate or dueDate=={}:
        return False

    today=date.today()

    due=date(dueDate["year"],dueDate["month"],dueDate["day"])


    return due>=today



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




def sortByDue(assignments):
    
    def key(a):
        dueDate=a.get("dueDate")
        dueTime=a.get("dueTime")

        if not dueDate:
            return (9999,12,31,23,59)


        year=dueDate["year"]
        month=dueDate["month"]
        day=dueDate["day"]

        hours=dueTime.get("hours",23) if dueTime else 23
        minutes=dueTime.get("minutes",59) if dueTime else 59


        return (year,month,day,hours,minutes)


    return sorted(assignments,key=key)

