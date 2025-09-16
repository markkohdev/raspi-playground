# From https://core-electronics.com.au/guides/raspberry-pi/getting-started-with-yolo-object-and-animal-recognition-on-the-raspberry-pi/
from typing import List
import cv2
import os
from time import sleep
from gpiozero import Buzzer, LED
from picamera2 import Picamera2
from ultralytics import YOLO
from ultralytics.engine.results import Results

import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


MODELS_DIR = ".models/"


def run():
    # Set up the camera with Picam
    picam = setup_camera()

    # Load a YOLO11n PyTorch model
    model = load_yolo_model()

    buzzer = Buzzer(17)
    red_led = LED(5)
    yellow_led = LED(6)
    green_led = LED(13)

    class_id_map = {class_name: class_id for class_id, class_name in model.names.items()}

    # Get the class index for "cat"
    cat_class = class_id_map.get("cat")
    teddy_bear_class = class_id_map.get("teddy bear")

    while True:
        # Capture a frame from the camera
        frame = picam.capture_array()

        # Run YOLO model on the captured frame and store the results
        results: List[Results] = model.predict(frame, verbose=False)

        # Output the visual detection data, we will draw this on our camera preview window
        annotated_frame = results[0].plot()

        boxes = results[0].boxes

        for idx, class_id in enumerate(boxes.cls):
            if class_id == cat_class:
                conf = boxes.conf[idx]
                if conf > 0.5:  # Only log if confidence is greater than 50%
                    logger.info(f"Cat detected with confidence {conf:.2f}")
                    buzzer.on()
                    sleep(0.1)
                    buzzer.off()
            if class_id == teddy_bear_class:
                conf = boxes.conf[idx]
                if conf > 0.5:  # Only log if confidence is greater than 50%
                    logger.info(f"Teddy bear detected with confidence {conf:.2f}")
                    buzzer.on()
                    sleep(0.1)
                    buzzer.off()

        # Get inference time
        inference_time = results[0].speed["inference"]
        fps = 1000 / inference_time  # Convert to milliseconds
        text = f"FPS: {fps:.1f}"

        # Define font and position
        font = cv2.FONT_HERSHEY_SCRIPT_COMPLEX
        text_size = cv2.getTextSize(text, font, 1, 2)[0]
        text_x = annotated_frame.shape[1] - text_size[0] - 10  # 10 pixels from the right
        text_y = text_size[1] + 10  # 10 pixels from the top

        # Draw the text on the annotated frame
        cv2.putText(annotated_frame, text, (text_x, text_y), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Display the resulting frame
        cv2.imshow("Camera", annotated_frame)

        # # Exit the program if q is pressed
        if cv2.waitKey(1) == ord("q"):
            break

    # Close all windows
    cv2.destroyAllWindows()


def setup_camera() -> Picamera2:
    logger.info("Setting up camera...")
    # Set up the camera with Picam
    picam2 = Picamera2()
    picam2.preview_configuration.main.size = (1280, 1280)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.preview_configuration.align()
    picam2.configure("preview")
    picam2.start()
    return picam2


def load_yolo_model(model_name: str = "yolo11n") -> YOLO:
    # Check if the ncnn model already exists
    if not os.path.exists(os.path.join(MODELS_DIR, f"{model_name}_ncnn_model")):
        logger.info("NCNN model not found, downloading PyTorch model...")
        # Load a YOLO11n PyTorch model
        pt_model = YOLO(os.path.join(MODELS_DIR, f"{model_name}.pt"))

        # Export the model to NCNN format
        logger.info("Exporting model to NCNN format...")
        pt_model.export(format="ncnn")  # creates '{model_name}_ncnn_model'

        logger.info("NCNN model exported successfully.")

    logger.info("Loading NCNN model...")  # Use logger instead of
    # Load the exported NCNN model
    model = YOLO(os.path.join(MODELS_DIR, f"{model_name}_ncnn_model"))
    return model


if __name__ == "__main__":
    run()
