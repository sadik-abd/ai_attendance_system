import json
import random
from constant import *

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
        self.save()
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
if __name__ == "__main__":
    # Example usage
    db = Records()
    for i in range(10):
        random_time = generate_random_time()
        random_entry = random.choice(["entry","exit"])
        random_day = "2023-12-"+str(random.randint(0,30))
        
        db.add_record({
            "username":"sadik1",
            "datetime":random_day,
            "action":{
                "type":random_entry,
                "time":random_time
                }
        })
    print(db["sadik1"])
    

