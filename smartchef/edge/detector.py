# edge/detector.py
import os
import sys
import json
import time
import cv2
from ultralytics import YOLO

# Allow imports from the parent directory (so we can use api/gemini_generator.py)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.gemini_generator import generate_recipe_gemini  # ✅ import your Gemini generator

def load_food_classes(path="smartchef/edge/food_classes.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return {line.strip().lower() for line in f if line.strip()}

FOOD_CLASSES = load_food_classes()

# Load YOLOv8 Nano model (fastest lightweight version)
model = YOLO("yolov8n.pt")

def detect_from_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open webcam.")
        return

    print("Press 'q' to quit.")
    last_detected = set()  # track last detection to avoid duplicate recipe calls
    last_recipe_time = 0   # prevent spamming Gemini

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Run YOLO detection
        results = model(frame, verbose=False)
        annotated_frame = results[0].plot()

        # --- Extract detected object names ---
        names = model.names
        detected = set()
        for r in results:
            for box in r.boxes:
                cls = int(box.cls)
                label = model.names[cls]
                if label in FOOD_CLASSES:
                    detected.add(label)

        # --- If new items are detected, call Gemini ---
        if detected and detected != last_detected and (time.time() - last_recipe_time > 5):
            print(f"\n🍽️ Detected new items: {list(detected)}")
            print("🔮 Generating recipe suggestion...")

            try:
                recipe = generate_recipe_gemini(list(detected), {"quick_meal": True})
                print("\n--- Suggested Recipe ---")
                print(json.dumps(recipe, indent=2))
            except Exception as e:
                print("⚠️ Error generating recipe:", e)

            last_detected = detected
            last_recipe_time = time.time()

        # --- Display live annotated view ---
        cv2.imshow("SmartChef Vision", annotated_frame)

        # Quit if user presses 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

def detect_foods(image_path: str):
    results = model(image_path, verbose=False)
    names = model.names
    detected = set()
    for r in results:
        for box in r.boxes:
            cls = int(box.cls)
            label = names[cls]
            if label in FOOD_CLASSES:
                detected.add(label)
    return list(detected)

if __name__ == "__main__":
    detect_from_camera()

