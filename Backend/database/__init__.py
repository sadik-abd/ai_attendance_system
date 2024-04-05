import json
import shutil
import os

class Database:
    def __init__(self) -> None:
        self.data = {}
        self.file_path = "data.json"

    def load(self):
        """Load data from the JSON file."""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                self.data = json.load(file)
    
    def add(self, username, record, image_path):
        """Add a new user and move the image to ./images/."""
        # Move the image to ./images/
        image_name = os.path.basename(image_path)
        new_image_path = f"./images/{image_name}"
        shutil.move(image_path, new_image_path)

        # Add user data to the database
        self.data[username] = record
        self.data[username]['image'] = new_image_path

        # Save the updated data to the JSON file
        self.save()

    def delete(self, username):
        """Delete a user from the database."""
        if username in self.data:
            # Optionally, delete the image file
            image_path = self.data[username].get('image')
            if image_path and os.path.exists(image_path):
                os.remove(image_path)

            del self.data[username]
            self.save()

    def save(self):
        """Save the current state of the database to a JSON file."""
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file, indent=4)

class Record:
    def __init__(self) -> None:
        self.records = []
    
    def attend(self):
        pass

    def get_attend(self, date):
        pass

    def entrance_times(self, date):
        pass

    def exit_times(self, date):
        pass

    def save(self):
        """Save the current state of the database to a JSON file."""
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file, indent=4)