import os

from datetime import datetime

from modules import courses


def count_folders(path):

    if not os.path.exists(path):
        return 0
    

    return len([f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))])


def generate_dashboard(base_path):

    courses = os.listdir(base_path)

    lines=[]
    lines.append("# Course Dashboard\n")

    for course in courses:

        course_path=os.path.join(base_path,course)

        if not os.path.isdir(course_path):
            continue

        theory=os.path.join(course_path,"Theory")
        lab=os.path.join(course_path,"Lab")

        lectures=count_folders(os.path.join(theory,"Lecture Slides"))
        assignments=count_folders(os.path.join(theory,"Assignments"))
        labs=count_folders(os.path.join(lab,"Lab Work"))

        lines.append(f"## {course}")
        lines.append(f"- Lectures: {lectures}")
        lines.append(f"- Assignments: {assignments}")
        lines.append(f"- Labs: {labs}")
        lines.append(f"- Last Updated: {datetime.now().strftime('%Y-%m-%d')}")
        lines.append("")

    dashboard=os.path.join(base_path,"COURSE_INDEX.md")

    with open(dashboard,"w",encoding="utf-8") as f:
        f.write("\n".join(lines))