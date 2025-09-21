# From https://core-electronics.com.au/guides/raspberry-pi/getting-started-with-yolo-object-and-animal-recognition-on-the-raspberry-pi/
from dataclasses import dataclass
from re import I
from typing import List, Optional
import cv2
import os
from time import sleep
from gpiozero import Buzzer, RGBLED
from colorzero import Color
from picamera2 import Picamera2
from polars import duration
from ultralytics import YOLO
from ultralytics.engine.results import Results, Boxes
import asyncio

import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


MODELS_DIR = ".models/"


class StopDetectionLoop(Exception):
    """Custom exception to stop the detection loop."""

    pass


@dataclass
class DetectionClass:
    name: str
    confidence: float
    color: Optional[Color] = None
    buzz: bool = True


# class CatBuzzerDeviceHandler():
#     """
#     Class which allows for async handling of buzzer and LED actions.

#     The class will maintain the active state of the buzzer and LED
#     and allow for state updates from another thread.
#     """

#     def __init__(self, buzzer: Buzzer, rgb_led: RGBLED):
#         self.buzzer = buzzer
#         self.rgb_led = rgb_led


#     def set_buzzer(self, on: bool, duration_ms: int = 100):
#         if on:
#             self.buzzer.on()
#             sleep(duration_ms / 1000)
#             self.buzzer.off()
#         else:
#             self.buzzer.off()


class CatBuzzerRunner:

    IDLE_LED_COLOR = Color("green")
    DEFAULT_CLASSES = [
        DetectionClass("cat", 0.5, Color("red")),
        DetectionClass("teddy bear", 0.5, Color("blue")),
        DetectionClass("person", 0.8, buzz=False),
    ]

    picam: Picamera2
    show_preview: bool
    model: YOLO
    buzzer: Buzzer
    rgb_led: RGBLED

    def __init__(
        self,
        show_preview: bool = True,
        detection_classes: List[DetectionClass] = DEFAULT_CLASSES,
        buzzer_pin: int = 17,
        led_pins: tuple = (5, 6, 13),
        common_cathode: bool = False,
    ):
        # Set up the camera with Picam
        logger.info("Setting up camera...")
        self.show_preview = show_preview
        self.picam = self.setup_camera()
        if self.show_preview:
            self.picam.configure("preview")

        # Load a YOLO11n PyTorch model
        logger.info("Setting up detection model...")
        self.model = self.load_yolo_model()

        self.buzzer = Buzzer(buzzer_pin)
        self.rgb_led = RGBLED(*led_pins, active_high=common_cathode)

    def main(self):
        self.picam.start()
        self.rgb_led.color = self.IDLE_LED_COLOR

        try:
            while True:
                self.run_loop()
        except StopDetectionLoop as e:
            logger.info("Stopping detection loop...", e)

        # Close all windows
        cv2.destroyAllWindows()
        self.picam.stop()
        self.rgb_led.off()
        self.buzzer.off()

    def run_loop(self) -> bool:
        """
        Run the main loop for capturing frames and processing detections.
        """
        # Capture a frame from the camera
        frame = self.picam.capture_array()

        # Run YOLO model on the captured frame and store the results
        # We pass a single frame, so we get a list with one Results object
        results: List[Results] = self.model.predict(frame, verbose=False)[0]

        if self.show_preview:
            self.update_preview(results)

        self.process_boxes(results.boxes)

    def update_preview(self, results: List[Results]):
        """
        Handle post-prediction actions such as buzzing and LED color changes.
        """
        # Output the visual detection data, we will draw this on our camera preview window
        annotated_frame = results[0].plot()

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

        # Stop execution if 'q' is pressed
        if cv2.waitKey(1) == ord("q"):
            raise StopDetectionLoop("'q' pressed, stopping detection loop.")

    def process_boxes(self, boxes: List[Boxes]):
        """
        Process the detected boxes to determine actions.
        """
        if not hasattr(self, "_ids_to_detection_classes"):
            names_to_ids = {class_name: class_id for class_id, class_name in self.model.names.items()}
            self._ids_to_detection_classes = {
                names_to_ids[dc.name]: dc for dc in self.DEFAULT_CLASSES if dc.name in names_to_ids
            }

        for box in boxes:
            class_id = int(box.cls[0])
            if class_id in self._ids_to_detection_classes:
                detection_class = self._ids_to_detection_classes[class_id]
                if detection_class.buzz:
                    self.buzzer.on()
                    sleep(0.1)
                    self.buzzer.off()
                if detection_class.color:
                    self.rgb_led.color = detection_class.color

    @staticmethod
    def setup_camera() -> Picamera2:
        """
        Set up the Picamera2 camera with the desired configuration.
        Once returned, the camera still needs to be started with `picam2.start()`.
        """
        # Set up the camera with Picam
        picam2 = Picamera2()
        picam2.preview_configuration.main.size = (1280, 1280)
        picam2.preview_configuration.main.format = "RGB888"
        picam2.preview_configuration.align()
        return picam2

    @staticmethod
    def load_yolo_model(model_name: str = "yolo11n") -> YOLO:
        """
        Load the YOLO model with the specified name.
        If the NCNN version of the model does not exist, it will be downloaded and
        created from the PyTorch version.
        """
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
    runner = CatBuzzerRunner(show_preview=True)
    runner.main()
