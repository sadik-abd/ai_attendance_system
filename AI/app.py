import tkinter as tk
from tkinter import ttk, PhotoImage

class CameraApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        frame.tkraise()

class SetupPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Camera Link:").grid(row=0, column=0, padx=10, pady=10)
        rtsp_entry = ttk.Entry(self)
        rtsp_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self, text="Camera Label (entry/exit):").grid(row=1, column=0, padx=10, pady=10)
        label_entry = ttk.Entry(self)
        label_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self, text="Video Port:").grid(row=2, column=0, padx=10, pady=10)
        port_entry = ttk.Entry(self)
        port_entry.grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(self, text="Server Link:").grid(row=3, column=0, padx=10, pady=10)
        server_entry = ttk.Entry(self)
        server_entry.grid(row=3, column=1, padx=10, pady=10)

        ttk.Label(self, text="Refresh Time (seconds):").grid(row=4, column=0, padx=10, pady=10)
        refresh_entry = ttk.Entry(self)
        refresh_entry.grid(row=4, column=1, padx=10, pady=10)

        ttk.Button(self, text="Start Camera", command=lambda: print("Starting Camera...")).grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(self, text="Check Running Cameras", command=lambda: controller.show_frame(CamerasPage)).grid(row=6, column=0, columnspan=2, pady=10)

class CamerasPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Running Cameras").pack(pady=10, padx=10)
        ttk.Button(self, text="Go Back to Setup", command=lambda: controller.show_frame(SetupPage)).pack()

        # Example list of running cameras, you would dynamically generate this based on actual data
        self.cameras = ["Camera 1", "Camera 2", "Camera 3"]  # Sample camera names

        # Dynamically create labels and delete buttons for each camera
        for camera in self.cameras:
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
        self.cameras.remove(camera)
        # Redraw the camera list, this requires a more dynamic update method
        self.update_camera_list()

    def update_camera_list(self):
        # Clear all current cameras and repopulate the list (simple refresh strategy)
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Frame):  # Assuming all camera entries are in their own Frame
                widget.destroy()
        # Re-create camera list
        for camera in self.cameras:
            frame = ttk.Frame(self)  # Create a frame for each camera
            ttk.Label(frame, text=f"{camera}: Running...").pack(side="left", pady=2, padx=10)
            delete_button = ttk.Button(frame, text="Delete Camera", command=lambda c=camera: self.delete_camera(c))
            delete_button.pack(side="right", padx=10)
            frame.pack()


if __name__ == "__main__":
    app = CameraApp()
    app.mainloop()
