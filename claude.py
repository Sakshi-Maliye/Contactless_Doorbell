import os
import cv2
import time
import threading
import customtkinter as ctk
from PIL import Image, ImageTk

class DoorbellApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Doorbell App")
        self.root.geometry("800x600")

        # Create assets folder if it doesn't exist
        if not os.path.exists("assets"):
            os.makedirs("assets")

        # Initialize camera variables
        self.camera = None
        self.is_camera_running = False
        self.capture_thread = None
        self.display_thread = None

        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # App title
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="Doorbell App", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=10)

        # Camera display
        self.camera_frame = ctk.CTkFrame(self.main_frame)
        self.camera_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.camera_label = ctk.CTkLabel(self.camera_frame, text="Camera feed will appear here")
        self.camera_label.pack(fill="both", expand=True)

        # Button frame
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(fill="x", padx=20, pady=10)

        # Camera toggle button
        self.camera_button = ctk.CTkButton(
            self.button_frame,
            text="Open Camera",
            command=self.toggle_camera
        )
        self.camera_button.pack(pady=10)

        # Status label
        self.status_label = ctk.CTkLabel(self.main_frame, text="Camera is off")
        self.status_label.pack(pady=5)

    def toggle_camera(self):
        if self.is_camera_running:
            self.stop_camera()
            self.camera_button.configure(text="Open Camera")
            self.status_label.configure(text="Camera is off")
        else:
            success = self.start_camera()
            if success:
                self.camera_button.configure(text="Close Camera")
                self.status_label.configure(text="Camera is on - Capturing images")
            else:
                self.status_label.configure(text="Failed to open camera")

    def start_camera(self):
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                return False
                
            self.is_camera_running = True
            
            # Start the camera feed display thread
            self.display_thread = threading.Thread(target=self.update_display)
            self.display_thread.daemon = True
            self.display_thread.start()
            
            # Start the image capture thread
            self.capture_thread = threading.Thread(target=self.capture_images)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            
            return True
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False

    def stop_camera(self):
        self.is_camera_running = False
        if self.display_thread:
            self.display_thread.join(timeout=1.0)
        if self.capture_thread:
            self.capture_thread.join(timeout=1.0)
        if self.camera:
            self.camera.release()
        self.camera = None
        self.camera_label.configure(text="Camera feed will appear here")

    def update_display(self):
        """Thread to continuously update the camera feed display"""
        while self.is_camera_running:
            if self.camera and self.camera.isOpened():
                ret, frame = self.camera.read()
                if ret:
                    # Convert the image from BGR to RGB format
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Resize while maintaining aspect ratio
                    h, w, _ = frame_rgb.shape
                    max_size = 600
                    scale = min(max_size / w, max_size / h)
                    new_w, new_h = int(w * scale), int(h * scale)
                    frame_resized = cv2.resize(frame_rgb, (new_w, new_h))
                    
                    # Convert to PhotoImage
                    img = Image.fromarray(frame_resized)
                    imgtk = ImageTk.PhotoImage(image=img)
                    
                    # Update label
                    self.camera_label.imgtk = imgtk
                    self.camera_label.configure(image=imgtk, text="")
            time.sleep(0.03)  # ~30fps

    def capture_images(self):
        """Thread to capture and save images every 5 seconds"""
        last_capture_time = 0
        
        while self.is_camera_running:
            current_time = time.time()
            
            # Capture every 5 seconds
            if current_time - last_capture_time >= 5:
                if self.camera and self.camera.isOpened():
                    ret, frame = self.camera.read()
                    if ret:
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        filename = f"assets/doorbell_capture_{timestamp}.jpg"
                        cv2.imwrite(filename, frame)
                        print(f"Image saved: {filename}")
                        last_capture_time = current_time
            
            time.sleep(0.1)

def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    app = DoorbellApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop_camera(), root.destroy()))
    root.mainloop()

if __name__ == "__main__":
    main()