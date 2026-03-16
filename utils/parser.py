import re


def extract_number(title):
    match=re.search(r'\d+', title)

    if match:
        return match.group()
    
    return None
    
def sanitize_filename(name):

    name = re.sub(r'[<>:"/\\|?*]', '', name)

    return name.strip()