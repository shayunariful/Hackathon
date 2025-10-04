# edge/detector.py
from ultralytics import YOLO
import cv2
import time
# Load YOLOv8 Nano model (fastest lightweight version)
model = YOLO("yolov8n.pt")

def detect_from_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open webcam.")
        return

    print("Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Run YOLO detection
        results = model(frame, verbose=False)
        annotated_frame = results[0].plot()

        # --- Extract detected object names ---
        names = model.names  # YOLO's built-in label dictionary
        detected = set()

        for r in results:
            for box in r.boxes:
                cls = int(box.cls)
                detected.add(names[cls])

        if detected:
            print("Detected:", list(detected))

        # --- Display live annotated view ---
        cv2.imshow("SmartChef Vision", annotated_frame)


        time.sleep(0.5) 
        # Quit if user presses 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_from_camera()
