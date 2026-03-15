

def classify_file(name):

    name=name.lower()

    if "assignment" in name:
        return "Assignments"

    if "lab" in name:
        return "Lab Work"

    if "lecture" in name or "slides" in name or "lec" in name or "ppt" in name:
        return "Lecture Slides"

    if "quiz" in name or "test" in name:
        return "Quizzes"

    if "outline" in name or "syllabus" in name:
        return "Course Outline"

    if "book" in name or "ebook" in name:
        return "E-Books"

    if "mid" in name or "final" in name or "sessional" in name:
        return "Past Papers"

    
    return "Notes"
