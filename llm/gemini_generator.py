import os, json, time
from typing import List, Dict, Any
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv

# Load your API key from .env
load_dotenv()

# --- Gemini SDK ---
import google.generativeai as genai
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ---------- Schema ----------
class Recipe(BaseModel):
    title: str = Field(min_length=3, max_length=80)
    ingredients: List[str] = Field(min_items=2, max_items=20)
    steps: List[str] = Field(min_items=2, max_items=10)
    notes: List[str] = Field(default_factory=list, max_items=5)

# Pantry items allowed even if not detected
PANTRY = {
    "water", "salt", "pepper", "oil", "olive oil",
    "butter", "sugar", "flour", "garlic", "onion powder"
}

# ---------- Prompt templates ----------
SYSTEM_PROMPT = (
    "You are a concise home-cook recipe generator. "
    "Return STRICT JSON only, no markdown, no commentary. "
    "Use only the listed items plus common pantry staples "
    "(oil, salt, pepper, water, butter, sugar, flour, garlic, onion powder). "
    "Prefer 4-6 steps, simple techniques, 12-15 minute prep/cook. "
    "If not enough items for a real dish, make a snack or toast variation."
)

USER_TEMPLATE = (
    "Items: {items}\n"
    "Preferences: {prefs}\n\n"
    "Output JSON with EXACT keys: "
    "title (string), ingredients (string[]), steps (string[]), notes (string[]). "
    "Keep ingredient quantities realistic; if an item is already a whole food "
    "(e.g., 'bread'), don't duplicate it unnecessarily."
)


def _format_items(items: List[str]) -> List[str]:
    """Normalize and deduplicate ingredient names."""
    return sorted({i.strip().lower() for i in items if i.strip()})


def generate_recipe_gemini(
    items: List[str],
    prefs: Dict[str, Any] | None = None,
    model_name: str = "gemini-2.5-flash",
    temperature: float = 0.3,
    max_retries: int = 1,
) -> Dict[str, Any]:
    """
    Generate a recipe card via Gemini 2.5 Flash with strict JSON schema.
    Returns a dict validated by the Recipe Pydantic model.
    """
    if prefs is None:
        prefs = {}

    items = _format_items(items) or ["bread", "cheese", "tomato"]

    # Build user prompt
    user_prompt = USER_TEMPLATE.format(
        items=", ".join(items),
        prefs=json.dumps(prefs),
    )

    # Configure the Gemini model with a system instruction and schema
    model = genai.GenerativeModel(
        model_name,
        system_instruction=SYSTEM_PROMPT,
        generation_config=genai.types.GenerationConfig(
            temperature=temperature,
            response_mime_type="application/json",
        ),
    )

    last_err = None
    for _ in range(max_retries + 1):
        try:
            resp = model.generate_content(user_prompt)
            text = resp.text
            print("Gemini raw output (first 200 chars):", text[:200])  # debug helper

            raw = json.loads(text)
            recipe = Recipe(**raw).model_dump()
            return recipe

        except (ValidationError, json.JSONDecodeError) as e:
            last_err = e
            time.sleep(0.3)

    # --- Fallback so demo never stalls ---
    title = f"{items[0].title()} Quick Snack"
    return {
        "title": title,
        "ingredients": [
            f"{'2 slices ' if 'bread' in items else ''}"
            f"{'bread' if 'bread' in items else items[0]}",
            *(i for i in items[1:] if i != 'bread'),
            "1 tbsp oil or butter",
            "Salt and pepper",
        ],
        "steps": [
            "Preheat a non-stick pan to medium heat.",
            "Assemble items (layer on bread or mix in a bowl).",
            "Cook or toast 3–6 min until lightly browned and warmed through.",
            "Season to taste and serve.",
        ],
        "notes": ["Fallback recipe due to JSON validation error."],
    }


# --- Quick manual test (optional) ---
if __name__ == "__main__":
    recipe = generate_recipe_gemini(["tomato", "bread", "cheese"], {"vegetarian": True})
    print(json.dumps(recipe, indent=2))
