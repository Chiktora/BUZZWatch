from raspberry_pi_code.hardware_layer.camera import Camera

if __name__ == "__main__":
    camera = Camera()
    image_path = camera.capture_image("/home/pi/BUZZWatch/captured_images/test_images")
    if image_path:
        print(f"Image captured successfully: {image_path}")
    else:
        print("Failed to capture image.")
