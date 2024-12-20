from picamera import PiCamera
import time

camera = PiCamera()

def capture_image():
    """Captures an image using the PiCamera."""
    image_path = f"/home/pi/captured_images/image_{int(time.time())}.jpg"
    camera.capture(image_path)
    return image_path
