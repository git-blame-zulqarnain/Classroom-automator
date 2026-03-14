import re


def extract_number(title):
    match=re.search(r'\d+', title)

    if match:
        return match.group()
    
    return None
    
