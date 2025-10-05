# smartchef AI Powered Recipe Generator
SmartChef is an intelligent web app that helps users discover recipes using **computer vision** and **generative AI**.  
Simply take or upload a photo of your fridge or ingredients, and SmartChef will identify the food items using **YOLOv8** and generate creative, personalized recipes using **Google Gemini AI**.

# Features 
- 🧠 **AI Object Detection** — Detects ingredients from uploaded or live camera images using YOLOv8 Nano.
- 🤖 **Recipe Generation** — Generates custom recipes through Google Gemini API.
- 📸 **Live Camera Mode** — Take pictures directly from your webcam or phone camera.
- 🌐 **Web Integration** — FastAPI backend connected to a responsive web frontend hosted on Render and GitHub Pages.
- 🧾 **Fallback Recommendations** — Simple CSV-based recipe database for offline recommendations.


## 🏗️ Tech Stack
| Layer | Technology |
|-------|-------------|
| **Frontend** | HTML, CSS, JavaScript (Fetch API for backend calls) |
| **Backend API** | FastAPI (Python) |
| **AI / ML** | YOLOv8 (Ultralytics), Google Gemini |
| **Deployment** | Render (Backend), GitHub Pages (.tech frontend) |
| **Data** | CSV-based sample recipe storage |

## 📂 Project Structure
Hackathon/
│
├── smartchef/
│   ├── api/
│   │   ├── gemini_generator.py       # Handles Gemini recipe generation
│   │   └── test_key.py               # API key test file
│   │
│   ├── edge/
│   │   └── detector.py               # YOLOv8 food detection logic
│   │
│   ├── ui/
│   │   └── app.py                    # FastAPI app (main backend entrypoint)
│   │
│   └── cloud/
│       └── sample_recipes.csv        # Local fallback recipe database
│
├── index.html                        # Web interface
├── script.js                         # Handles camera + API requests
├── style.css                         # Styling
├── requirements.txt                  # Python dependencies
└── README.md                         # You are here 🙂


## Contributors
Tyler Lee - AI & Backend Integration, Full stack
Ahriful Shayun - Frontend, Testing
Bryce Wong - Frontend & Web Design
Saffat Uddin - Frontend & Web Design
