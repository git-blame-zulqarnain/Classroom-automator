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


def detect_quiz_type(text):
    text = text.lower()
    for keyword in QUIZ_KEYWORDS:
        if keyword in text:
            return keyword
    return None


def forMySection(title):
    title = title.upper()

    if not MY_SECTION:
        return True

    my_patterns = [
        f"SECTION {MY_SECTION}",
        f"SEC {MY_SECTION}",
        f"CS-{MY_SECTION}",
        f"CS {MY_SECTION}",
        f"SECTIONS {MY_SECTION}",
        f"AND {MY_SECTION}",
        f",{MY_SECTION}",
        f"SECTIONS ({MY_SECTION}",
        f"AND {MY_SECTION})"
    ]

    for p in my_patterns:
        if p in title:
            return True

    all_sections = ["A", "B", "C", "D", "E", "F", "G"]

    for sec in all_sections:
        if sec == MY_SECTION:
            continue

        patterns = [
            f"SECTION {sec}",
            f"SEC {sec}",
            f"CS-{sec}",
            f"CS {sec}",
            f"SECTIONS {sec}",
            f"AND {sec}",
            f",{sec}",
            f"SECTIONS ({sec}",
            f"AND {sec})"
        ]
        for p in patterns:
            if p in title:
                return False

    return True


def extractPossibleDeadline(text):
    patterns = [
        r"\d{1,2}:\d{2}",
        r"\d{1,2}\s*(?:am|pm)",
        r"today",
        r"tomorrow",
        r"monday|tuesday|wednesday|thursday|friday|saturday|sunday"
    ]
    matches = []
    for pattern in patterns:
        found = re.findall(pattern, text.lower())
        matches.extend(found)
    return matches


def get_best_deadline(deadlines):
    return deadlines[0] if deadlines else "Not specified"


def clean_text(text):
    text = text.replace("\n", " ")
    words = text.split()
    return " ".join(words[:15]) + ("..." if len(words) > 15 else "")


def extract_topic(text):
    text_lower = text.lower()
    patterns = [
        r"on ([a-zA-Z0-9\s]+)",
        r"from ([a-zA-Z0-9\s]+)",
        r"topics?[:\-]\s*([a-zA-Z0-9\s,]+)",
        r"covering ([a-zA-Z0-9\s,]+)"
    ]
    for p in patterns:
        match = re.search(p, text_lower)
        if match:
            topic = match.group(1).strip()
            return topic.title()
    return "Not specified"


def format_date_info(text, creation_time):
    text = text.lower()
    try:
        created = datetime.strptime(creation_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    except:
        return "Not specified"

    now = datetime.now()

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
            target_date = now + timedelta(days=diff)
            return f"{created.date()} -> {target_date.strftime('%A')}"

    if "today" in text:
        return f"{created.date()} -> {now.strftime('%A')}"

    if "tomorrow" in text:
        tmr = now + timedelta(days=1)
        return f"{created.date()} -> {tmr.strftime('%A')}"

    return created.date().isoformat()


def is_upcoming(text, creation_time):
    text = text.lower()

    try:
        created = datetime.strptime(creation_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    except:
        return False

    now = datetime.now()

    if created.date() < now.date():
        if "tomorrow" not in text and "today" not in text:
            return False

    if "today" in text:
        return created.date() == now.date()

    if "tomorrow" in text:
        return (created.date() + timedelta(days=1)) >= now.date()

    days_map = {
        "monday": 0, "tuesday": 1, "wednesday": 2,
        "thursday": 3, "friday": 4,
        "saturday": 5, "sunday": 6
    }

    for day in days_map:
        if day in text:
            target_idx = days_map[day]
            created_idx = created.weekday()

            diff = (target_idx - created_idx) % 7
            quiz_date = created + timedelta(days=diff)

            return quiz_date.date() >= now.date()

    return False


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

            try:
                created = datetime.strptime(creation_time, "%Y-%m-%dT%H:%M:%S.%fZ")
                now = datetime.now()

                if (now - created).days > 5:
                    continue
            except:
                continue

            if not text:
                continue

            if not contains_quiz(text):
                continue

            if not forMySection(text):
                continue

            if not is_upcoming(text, creation_time):
                continue

            quiz_type = detect_quiz_type(text)
            deadlines = extractPossibleDeadline(text)
            best_deadline = get_best_deadline(deadlines)
            topic = extract_topic(text)
            formatted_date = format_date_info(text, creation_time)

            detected.append({
                "course": course_name,
                "type": quiz_type,
                "time": best_deadline,
                "topic": topic,
                "date_info": formatted_date,
                "detailed_info": text,
            })

    if not detected:
        print(Fore.GREEN + "NO ACTIVE QUIZZES FOUND")
        return
    
    detected.sort(key=lambda q: datetime.strptime(str(q['date_info']).split(' -> ')[0], "%Y-%m-%d"))

    print()
    print(Fore.RED + "\t\t ACTIVE QUIZZES")
    print()

    for q in detected:

        print(Fore.CYAN + f"Course Name: {q['course']}")
        print(Fore.YELLOW + f"Quiz Type: {q['type']}")
        print(Fore.GREEN + f"Quiz Date Expected: {q['date_info']}")
        print(Fore.WHITE + f"Quiz Topic: {q['topic']}")
        print(Fore.WHITE + f"Detailed Info: {q['detailed_info']}")
        print("-" * 50)