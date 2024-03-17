import tkinter as tk
from tkinter import ttk, PhotoImage
import requests
import subprocess
import threading
import queue

def execute_main_async(cctv_link, video_port, label, server_link):
    # Define the command and arguments
    command = 'python'
    script = 'main.py'

    # Assemble the full command with arguments
    full_command = [
        command,
        script,
        '--cctv_link', cctv_link,
        '--video_port', str(video_port),
        '--label', label,
        '--server_link', server_link
    ]

    # Execute the command without waiting for it to finish
    process = subprocess.Popen(full_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True)

    # Create queues to hold the output and errors
    output_queue = queue.Queue()
    error_queue = queue.Queue()

    # Define a function for processing stream output
    def enqueue_output(stream, queue):
        for line in iter(stream.readline, ''):
            queue.put(line)
        stream.close()

    # Start threads for reading output and errors
    output_thread = threading.Thread(target=enqueue_output, args=(process.stdout, output_queue))
    error_thread = threading.Thread(target=enqueue_output, args=(process.stderr, error_queue))
    output_thread.daemon = True
    error_thread.daemon = True
    output_thread.start()
    error_thread.start()

    # You can now handle the output and errors in your main program, for example:
    def check_output():
        # Check the output queue
        while not output_queue.empty():
            line = output_queue.get_nowait()
            print("Output:", line, end='')  # Print output lines from the process
        # Check the error queue
        while not error_queue.empty():
            line = error_queue.get_nowait()
            print("Error:", line, end='')  # Print error lines from the process

    # Return the process and the check_output function so you can use them outside
    return process, check_output



class CameraApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cams = []
        self.title("Camera Settings")
        self.geometry("400x300")  # Set starting window size
        self.frames = {}
        img = PhotoImage(file='./ico.png')
        self.iconphoto(False, img)


        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        for F in (SetupPage, CamerasPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(SetupPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        if cont == CamerasPage:  # Check if the CamerasPage is the one being shown
            frame.update_camera_list()
        frame.tkraise()

class SetupPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Camera Link:").grid(row=0, column=0, padx=10, pady=10)
        self.rtsp_entry = ttk.Entry(self)
        self.rtsp_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self, text="Camera Label (entry/exit):").grid(row=1, column=0, padx=10, pady=10)
        self.label_entry = ttk.Combobox(self, values=["entry","exit"])
        self.label_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self, text="Video Port:").grid(row=2, column=0, padx=10, pady=10)
        self.port_entry = ttk.Entry(self)
        self.port_entry.grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(self, text="Server Link:").grid(row=3, column=0, padx=10, pady=10)
        self.server_entry = ttk.Entry(self)
        self.server_entry.grid(row=3, column=1, padx=10, pady=10)

        ttk.Label(self, text="Refresh Time (seconds):").grid(row=4, column=0, padx=10, pady=10)
        self.refresh_entry = ttk.Entry(self)
        self.refresh_entry.grid(row=4, column=1, padx=10, pady=10)

        ttk.Button(self, text="Start Camera", command=self.start_camera).grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(self, text="Check Running Cameras", command=lambda: controller.show_frame(CamerasPage)).grid(row=6, column=0, columnspan=2, pady=10)


    def start_camera(self):
        """Starts the camera using the information provided in the entry fields."""
        cctv_link = self.rtsp_entry.get()
        video_port = self.port_entry.get()
        label = self.label_entry.get()
        server_link = self.server_entry.get()
        
        self.controller.cams.append("Camera " + label + ":" + video_port)
        
        # Assuming video_port should be an integer, validate this:
        try:
            video_port = int(video_port)  # Convert video_port to int
        except ValueError:
            print("Error: Video Port must be an integer.")
            return  # Exit the method if conversion fails

        print("Starting Camera...")
        print(self.controller.cams)
        execute_main_async(cctv_link, video_port, label, server_link)  # Call your async function with the parameters
class CamerasPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Running Cameras").pack(pady=10, padx=10)
        ttk.Button(self, text="Go Back to Setup", command=lambda: controller.show_frame(SetupPage)).pack()

        # Example list of running cameras, you would dynamically generate this based on actual data
        print(self.controller.cams)
        # Dynamically create labels and delete buttons for each camera
        for camera in self.controller.cams:
            frame = ttk.Frame(self)  # Create a frame for each camera
            ttk.Label(frame, text=f"{camera}: Running...").pack(side="left", pady=2, padx=10)

            # Delete button for each camera, command should be linked to actual deletion logic
            delete_button = ttk.Button(frame, text="Delete Camera", command=lambda c=camera: self.delete_camera(c))
            delete_button.pack(side="right", padx=10)

            frame.pack()
    
    def delete_camera(self, camera):
        # Placeholder for deletion logic, you should replace this with actual code to delete the camera
        print(f"Deleting {camera}...")
        # Update your camera list and UI accordingly
        port = int(camera.split(":")[-1])
        requests.get(f"http://127.0.0.1:{port}/stop")
        self.controller.cams.remove(camera)
        # Redraw the camera list, this requires a more dynamic update method
        self.update_camera_list()

    def update_camera_list(self):
        # Clear all current cameras and repopulate the list (simple refresh strategy)
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Frame):  # Assuming all camera entries are in their own Frame
                widget.destroy()
        
        # Re-create camera list
        for camera in self.controller.cams:
            frame = ttk.Frame(self)  # Create a frame for each camera
            ttk.Label(frame, text=f"{camera}: Running...").pack(side="left", pady=2, padx=10)
            delete_button = ttk.Button(frame, text="Delete Camera", command=lambda c=camera: self.delete_camera(c))
            delete_button.pack(side="right", padx=10)
            frame.pack()


if __name__ == "__main__":
    app = CameraApp()
    app.mainloop()
