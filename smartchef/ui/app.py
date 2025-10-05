# smartchef/ui/api.py
import os, uuid, csv
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from smartchef.edge.detector import detect_foods

# import your gemini file, no matter its folder name
from smartchef.api.gemini_generator import generate_recipe_gemini


app = FastAPI(title="SmartChef API")

# CORS: start permissive; tighten later
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://smartchefapp.tech",
        "https://shayunariful.github.io",
        "*",  # optional fallback
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

RECIPES_CSV = os.path.join(os.getcwd(), "smartchef", "cloud", "sample_recipes.csv")
if not os.path.exists(RECIPES_CSV):
    # create a tiny recipe bank if missing
    os.makedirs(os.path.dirname(RECIPES_CSV), exist_ok=True)
    with open(RECIPES_CSV, "w", encoding="utf-8", newline="") as f:
        f.write("title,ingredients,steps,tags\n")
        f.write("Spinach Tomato Omelette,\"egg,spinach,tomato,salt,oil\",\"Beat eggs; Saute veg; Add eggs; Fold.\",breakfast\n")
        f.write("Tomato Pasta,\"pasta,tomato,garlic,olive oil,salt\",\"Boil pasta; Make sauce; Toss.\",dinner\n")

def normalize(s: str) -> str:
    return s.lower().strip()

def load_recipes() -> list[dict]:
    with open(RECIPES_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def baseline_recommend(items: List[str]) -> List[Dict[str, Any]]:
    S = set(map(normalize, items))
    out = []
    for r in load_recipes():
        ing = set(map(normalize, r["ingredients"].split(",")))
        score = 1.0 * len(S & ing) - 0.7 * len(ing - S)
        if score > 0:
            out.append({
                "title": r["title"],
                "ingredients": sorted(list(ing)),
                "score": round(score, 2),
                "tags": r.get("tags","")
            })
    return sorted(out, key=lambda x: x["score"], reverse=True)[:10]

@app.get("/health")
def health():
    return {"ok": True, "time": datetime.utcnow().isoformat()}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    fn = f"{uuid.uuid4()}_{file.filename}"
    path = os.path.join(UPLOAD_DIR, fn)
    with open(path, "wb") as f:
        f.write(await file.read())
    labels = detect_foods(path)
    recs = baseline_recommend(labels)
    return {"image": fn, "labels": labels, "recipes": recs}

class AIReq(BaseModel):
    items: List[str]
    prefs: Optional[Dict[str, Any]] = None

@app.post("/ai-recipe")
def ai_recipe(body: AIReq):
    recipe = generate_recipe_gemini(body.items, body.prefs or {})
    return {"recipe": recipe}


