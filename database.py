
import os
from datetime import date

# Path to the file where the limit information will be stored
LIMIT_FILE = 'limit_data.txt'

def get_limit_data():
    """
    Retrieves the saved date and request count from the file.
    Returns (saved_date, count). If the file does not exist, returns (None, 0).
    """
    if not os.path.exists(LIMIT_FILE):
        return None, 0
    try:
        with open(LIMIT_FILE, 'r') as f:
            lines = f.readlines()
            if len(lines) == 2:
                saved_date = lines[0].strip()
                count = int(lines[1].strip())
                return saved_date, count
    except (IOError, ValueError):
        # If the file is corrupted or unreadable
        return None, 0
    return None, 0

def set_limit_data(new_date: str, new_count: int):
    """
    Saves the new date and request count to the file.
    """
    try:
        with open(LIMIT_FILE, 'w') as f:
            f.write(f"{new_date}\n")
            f.write(f"{new_count}\n")
    except IOError as e:
        print(f"Error writing to the limit file: {e}")