from picamera2 import Picamera2
import time
import os

class Camera:
    def __init__(self):
        try:
            self.camera = Picamera2()

            # Configure the camera with appropriate parameters
            camera_config = self.camera.create_still_configuration(
                main={"size": (1280, 720)},
                lores={"size": (640, 480)},
                display="main"
            )
            self.camera.configure(camera_config)
        except Exception as e:
            print(f"Error initializing camera: {e}")
            self.camera = None

    def capture_image(self, save_path="/home/pi/BUZZWatch/captured_images/"):
        if self.camera is None:
            print("Camera not initialized.")
            return None

        try:
            # Ensure the directory exists
            os.makedirs(save_path, exist_ok=True)

            # Generate a unique filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            file_name = f"image_{timestamp}.jpg"
            full_path = os.path.join(save_path, file_name)

            # Capture the image
            self.camera.start()
            self.camera.capture_file(full_path)
            self.camera.stop()

            print(f"Image saved at {full_path}")
            return full_path
        except Exception as e:
            print(f"Error capturing image: {e}")
            return None

    def release_camera(self):
        """Release the camera resource."""
        if self.camera is not None:
            try:
                self.camera.close()
                print("Camera released.")
            except Exception as e:
                print(f"Error releasing camera: {e}")
