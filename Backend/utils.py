import os
from datetime import datetime, timedelta
from constant import *
def find_nearest_image(folder_path, input_time, tpe):
    """
    Finds the image with the timestamp closest to the input_time in the given folder.

    Args:
        folder_path (str): The path to the folder containing the images.
        input_time (str): The input time in '%Y-%m-%dT%H_%M' format.

    Returns:
        str: The path to the image with the closest timestamp.
    """
    # Convert input_time string to datetime object
    input_datetime = datetime.strptime(input_time, "%Y-%m-%dT%H_%M_%S")

    
    # Initialize minimum time difference and path of the nearest image
    min_diff = timedelta.max
    nearest_image_path = None
    
    # Loop through all files in the given folder
    for file in os.listdir(folder_path):
        if file.endswith(".jpg"):  # Check if the file is a JPG image
            # Extract timestamp from the file name and convert to datetime object
            if tpe in file:
                file = file[6:]
            else:
                continue
            file_time_str = file.rstrip('.jpg')
            file_datetime = datetime.strptime(file_time_str, "%Y-%m-%dT%H_%M_%S")
            
            # Calculate the time difference between input_time and file time
            time_diff = abs(input_datetime - file_datetime)
            
            # Update nearest image if this file is closer to the input time
            if time_diff < min_diff:
                min_diff = time_diff
                nearest_image_path = os.path.join(folder_path, f"{tpe}_"+file)
                
    return nearest_image_path
