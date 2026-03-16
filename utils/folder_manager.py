import os

def ensure_folder(path):

    if os.path.exists(path):
        return
    
    if not os.path.exists(path):
        os.makedirs(path)