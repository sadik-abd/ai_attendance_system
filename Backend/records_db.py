import json
import random
from constant import *
from datetime import datetime,timedelta
import requests
import time
import threading
from PIL import Image, ImageDraw
import base64
import io

class Records:
    def __init__(self) -> None:
        self.file_path = RECORD_DB
        self.records = json.load(open(RECORD_DB))
    def __getitem__(self, key):
        return self.records.get(key)

    def add_user(self,username,start_date):
        self.records[username] = dict()
        self.records[username][start_date] = {
                "entry":[],
                "exit":[]
            }
        self.save()
        
    def add_record(self, record):
        name = record["username"]
        dtime = record["datetime"]
        action = record["action"]
        action_type = action["type"]
        action_time = action["time"]
        try:
            self.records[name][dtime][action_type].append(action_time)
        except KeyError as k:
            self.records[name][dtime] = {
                "entry":[],
                "exit":[]
            }
            self.records[name][dtime][action_type].append(action_time)
        def thred_runner():
            time.sleep(0.3)
            if not record["image"]:
                img_save(record["link"],action_type,record["bbox"])
            else:
                img_save_b64(record["image"],action_type,record["bbox"])
        thr = threading.Thread(target=thred_runner)
        
        self.save()
        
        thr.start()
    def save(self):
        """Save the current state of the database to a JSON file."""
        with open(self.file_path, 'w') as file:
            json.dump(self.records, file, indent=4)

def generate_random_time():
    """
    Generates a random time with hours and minutes of a day.
    """
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)

    return f"{hours:02d}:{minutes:02d}"

def calculate_office_metrics(data):
    results = {}
    for employee, dates in data.items():
        for date, times in dates.items():
            # Initialize the daily data for this employee if not already present
            if employee not in results:
                results[employee] = {}
            # Count the number of entries and exits
            num_entries = len(times.get("entry", []))
            num_exits = len(times.get("exit", []))
            # Calculate total time spent in the office
            total_time = 0
            entry_times = [datetime.strptime(time, "%H:%M:%S") for time in times.get("entry", [])]
            exit_times = [datetime.strptime(time, "%H:%M:%S") for time in times.get("exit", [])]
            for i in range(min(len(entry_times), len(exit_times))):
                total_time += (exit_times[i] - entry_times[i]).total_seconds()
            # Store results
            results[employee][date] = {
                "entries": num_entries,
                "exits": num_exits,
                "hours_in_office": total_time / 3600
            }
    return results

def days_since_last_entry(user_records):
    most_recent_date = None
    for date_str in user_records.keys():
        record_date = datetime.strptime(date_str, '%Y-%m-%d')
        if most_recent_date is None or record_date > most_recent_date:
            most_recent_date = record_date
    if most_recent_date is not None:
        return (datetime.now() - most_recent_date).days
    return None  # No entry found

# Function to format the absence duration
def format_absence_duration(days):
    if days is None:
        return "never attended"
    elif days >= 14:
        weeks = days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''}"
    else:
        return f"{days} day{'s' if days > 1 else ''}"

# Main function to find users' absences
def find_user_absences(data):
    user_absences = []
    for user, records in data.items():
        days_absent = days_since_last_entry(records)
        if days_absent is not None and days_absent > 0:  # Check if the user has been absent
            absence_duration = format_absence_duration(days_absent)
            user_absences.append(f"{user} is absent for {absence_duration}")
        elif days_absent is None:  # User never attended
            user_absences.append(f"{user} has {format_absence_duration(days_absent)}")
    return user_absences

def sum_values_between_dates(datas, start_date, end_date):
    # Convert string dates to datetime objects
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Initialize sums

    ret_data = dict()
    # Iterate through each date in the dictionary
    for name, data in datas.items():
        total_hours = 0
        entries = 0
        exits = 0
        for date_str, values in data.items():
            current_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Check if the current date falls within the start and end dates
            if start_date <= current_date <= end_date:
                # Sum up the values
                total_hours += int(values.get('hours_in_office', 0))
                entries += int(values.get('entries', 0))
                exits += int(values.get('exits', 0))

        ret_data[name] = {
            'hours_in_office': total_hours,
            'entries': entries,
            'exits': exits
        }
    # Return the total sums
    return ret_data

def img_save(url, label, bbox):
    response = requests.get("http://127.0.0.1:6677/video?link="+url, stream=True)

    # Check if the request was successful
    if response.status_code == 200:
        # Convert stream to PIL Image
        image = Image.open(response.raw)

        # Draw bounding box
        draw = ImageDraw.Draw(image)
        draw.rectangle(bbox, outline="green", width=2)

        # Save the image
        img_path = f"{label}_{datetime.now().strftime('%Y-%m-%dT%H_%M_%S')}.jpg"
        image.save(f"{RECORD_IMAGE_PATH}/{img_path}")

    else:
        print("Failed to retrieve the image")


def img_save_b64(image_b64, label, bbox):
    # Decode the base64 image
    image_bytes = base64.b64decode(image_b64)
    
    # Convert bytes to a PIL Image
    image = Image.open(io.BytesIO(image_bytes))

    # Draw bounding box
    draw = ImageDraw.Draw(image)
    draw.rectangle(bbox, outline="green", width=2)

    # Save the image
    img_path = f"{label}_{datetime.now().strftime('%Y-%m-%dT%H_%M_%S')}.jpg"
    image.save(f"{RECORD_IMAGE_PATH}/{img_path}")


if __name__ == "__main__":
    # Example usage
    db = Records()
    for i in range(10):
        random_time = generate_random_time()
        random_entry = random.choice(["entry","exit"])
        random_day = "2024-1-"+str(random.randint(0,30))
        
        db.add_record({
            "username":"sadik1",
            "datetime":random_day,
            "action":{
                "type":random_entry,
                "time":random_time
                }
        })
    print(db["sadik1"])
    

