import json
import random
from constant import *
from datetime import datetime
import requests
import time
import threading
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
        print(record["link"])
        def thred_runner():
            time.sleep(0.3)
            img_save(record["link"][1:-1],action_type)
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

from datetime import datetime

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

def img_save(url, label):
    response = requests.get(url, stream=True)

    # Check if the request was successful
    if response.status_code == 200:
        jpg_content = bytearray()
        in_jpeg = False
        for chunk in response.iter_content(chunk_size=1024):
            # Iterate through each byte
            for byte in chunk:
                if byte == 0xff:  # Possible start of JPEG marker
                    jpg_content.append(byte)  # Add it to array
                    in_jpeg = True
                elif in_jpeg:
                    jpg_content.append(byte)
                    
                    if jpg_content[-2:] == bytes([0xff, 0xd9]):  # JPEG end marker
                        # Save the image
                        img_path = label+"_"+datetime.now().strftime("%Y-%m-%dT%H_%M_%S")
                        with open(f"""{RECORD_IMAGE_PATH}/{img_path}.jpg""", 'wb') as f:
                            f.write(jpg_content)
                        in_jpeg = False  # Reset for the next image
                        break  # Exit after saving the first image
            if not in_jpeg:  # Break the outer loop if we've finished processing a JPEG
                break
    else:
        print("Failed to retrieve the image")


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
    

