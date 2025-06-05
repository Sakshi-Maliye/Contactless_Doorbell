import customtkinter as ctk
import cv2
import os
import time
from PIL import Image, ImageTk
import threading
from datetime import datetime

# Set Customtkinter appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class DoorbellApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Doorbell App")
        self.root.geometry("800x600")

        # Create assets folder if it doesn't exist
        self.assets_folder = "assets"
        if not os.path.exists(self.assets_folder):
            os.makedirs(self.assets_folder)

        # UI Elements
        self.label = ctk.CTkLabel(
            master=self.root,
            text="Doorbell App",
            font=("Arial", 24, "bold")
        )
        self.label.pack(pady=20)

        self.start_button = ctk.CTkButton(
            master=self.root,
            text="Start Camera",
            command=self.start_camera
        )
        self.start_button.pack(pady=10)

        # Video display label
        self.video_label = ctk.CTkLabel(master=self.root, text="")
        self.video_label.pack(pady=10)

        # Camera variables
        self.cap = None
        self.running = False
        self.last_capture = 0

    def start_camera(self):
        if not self.running:
            self.cap = cv2.VideoCapture(0)  # Open default camera
            if not self.cap.isOpened():
                self.label.configure(text="Error: Could not open camera")
                return
            self.running = True
            self.start_button.configure(text="Stop Camera")
            # Start camera loop in a separate thread
            threading.Thread(target=self.update_frame, daemon=True).start()
        else:
            self.running = False
            self.start_button.configure(text="Start Camera")
            if self.cap:
                self.cap.release()
            self.video_label.configure(image=None, text="Camera Stopped")

    def update_frame(self):
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Convert frame to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Resize frame for display
                frame_resized = cv2.resize(frame_rgb, (640, 480))
                # Convert to PIL Image
                image = Image.fromarray(frame_resized)
                photo = ctk.CTkImage(light_image=image, dark_image=image, size=(640, 480))
                # Update video label
                self.video_label.configure(image=photo)
                self.video_label.image = photo  # Keep reference

                # Capture image every 5 seconds
                current_time = time.time()
                if current_time - self.last_capture >= 5:
                    self.save_image(frame)
                    self.last_capture = current_time

            self.root.update()
        # Cleanup
        if self.cap:
            self.cap.release()

    def save_image(self, frame):
        # Save image with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.assets_folder, f"capture_{timestamp}.jpg")
        cv2.imwrite(filename, frame)
        print(f"Saved image: {filename}")

    def on_closing(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = DoorbellApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()