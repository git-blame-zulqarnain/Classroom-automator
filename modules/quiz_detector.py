from colorama import Fore
import re
from datetime import datetime, timedelta
from config.settings import MY_SECTION


QUIZ_KEYWORDS = [
    "quiz",
    "test",
    "mcq",
    "lab sessional",
    "lab-sessional",
    "assignment based quiz",
    "assignment-based quiz",
]


def contains_quiz(text):

    text = text.lower()

    for keyword in QUIZ_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword) + r'\b', text):
            return True

    return False


def forMySection(title):

    title = title.upper()

    otherSections = ["B", "C", "D", "E", "F", "G"]

    for sec in otherSections:
        if f"SECTION {sec}" in title or f"SEC {sec}" in title or f"CS-{sec}" in title or f"CS {sec}" in title:
            return False

    
    return True


def extractPossibleDeadline(text):

    patterns = [
        r"\d{1,2}:\d{2}",
        r"\d{1,2}\s*(am|pm)",
        r"today",
        r"tomorrow",
        r"monday|tuesday|wednesday|thursday|friday|saturday|sunday"
    ]

    matches = []

    for pattern in patterns:
        found = re.findall(pattern, text.lower())
        matches.extend(found)

    return matches


def is_upcoming(creation_time, text):

    try:
        created = datetime.strptime(creation_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    except:
        return True  

    now = datetime.utcnow()
    text = text.lower()

    if "today" in text:
        return (now - created) <= timedelta(days=1)

    if "tomorrow" in text:
        return (now - created) <= timedelta(days=2)

    days_map = {
        "monday": 0, "tuesday": 1, "wednesday": 2,
        "thursday": 3, "friday": 4,
        "saturday": 5, "sunday": 6
    }

    for day in days_map:
        if day in text:

            today_idx = now.weekday()
            target_idx = days_map[day]

            diff = (target_idx - today_idx) % 7

            if diff == 0:
                return True

            return diff <= 3

    return (now - created) <= timedelta(days=3)


def detectQuizzes(classroom, courses):

    print()
    print(Fore.MAGENTA + "=============================================================")
    print(Fore.MAGENTA + "\t\t SCANNING QUIZZES")
    print(Fore.MAGENTA + "=============================================================")

    detected = []

    for course in courses:

        course_name = course['name']

        try:
            results = classroom.courses().announcements().list(
                courseId=course['id']
            ).execute()

        except Exception as e:
            import traceback
            traceback.print_exc()
            continue

        announcements = results.get('announcements', [])

        for a in announcements:

            text = a.get('text', "")
            creation_time = a.get("creationTime", "")

            if not text:
                continue

            if not contains_quiz(text):
                continue

            if not forMySection(text):
                continue

            if not is_upcoming(creation_time, text):
                continue

            deadlines = extractPossibleDeadline(text)

            detected.append({
                "course": course_name,
                "announcement": text,
                "deadlines": deadlines
            })

    if not detected:
        print(Fore.GREEN + "NO ACTIVE QUIZZES FOUND")
        return

    print()
    print(Fore.RED + "\t\t ACTIVE QUIZZES")
    print()

    for q in detected:

        print(Fore.CYAN + f"Course: {q['course']}")
        print(Fore.WHITE + f"Announcement: {q['announcement']}")

        if q['deadlines']:
            print(Fore.YELLOW + f"Possible Time: {', '.join(q['deadlines'])}")
            print(Fore.RED + "UPCOMING QUIZ")

        print("-" * 50)