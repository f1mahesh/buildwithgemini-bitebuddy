"""Tools for BiteBuddy with real Google Places API (New), compact dish image generation, permanent profiles, and menu carousels."""

import io
import re
import math
import json
import os
import uuid
import datetime
import urllib.parse
import urllib.request
from typing import List, Optional
from PIL import Image

from google import genai
from google.genai import types
from google.cloud import firestore
from google.cloud import storage
from google.adk.tools import ToolContext

# Explicitly hardcoded Project ID & Bucket Name (NOT project number, NOT env var)
FIRESTORE_PROJECT = "qwiklabs-gcp-04-0ec1576f1d28"
GCS_BUCKET_NAME = "bitebuddy-assets-qwiklabs-gcp-04-0ec1576f1d28"
PLACES_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY") or os.environ.get("PLACES_API_KEY") or ""

# In-memory session store for current session preferences (e.g. today's meal choice: veg vs non-veg)
_SESSION_PREFERENCES = {}

def _get_db() -> firestore.Client:
    return firestore.Client(project=FIRESTORE_PROJECT)


def _get_storage_client() -> storage.Client:
    return storage.Client(project=FIRESTORE_PROJECT)


async def generate_dish_image(
    dish_name: str,
    restaurant_name: Optional[str] = None,
    tool_context: Optional[ToolContext] = None,
) -> dict:
    """Generates a realistic, compact thumbnail image of a dish using gemini-3.1-flash-lite-image in the global region.

    Resizes the image to a compact small card format (360x270px) so it loads fast and fits cleanly in cards and carousels.
    Saves the image into the Playground Artifacts panel and uploads it to the public Cloud Storage bucket.

    Args:
        dish_name: Name of the dish (e.g. 'Truffle Mushroom Risotto', 'Crispy Birria Tacos with Consomé').
        restaurant_name: Optional restaurant name for context.
        tool_context: Injected ToolContext to save artifacts in Playground.

    Returns:
        Dict with public Cloud Storage URL (https://storage.googleapis.com/<bucket>/<object>) and artifact details.
    """
    prompt = (
        f"Gourmet culinary close-up photo of {dish_name}"
        + (f" at {restaurant_name}" if restaurant_name else "")
        + ", realistic food photography, plated restaurant presentation, authentic texture, beautiful natural light, mouth-watering"
    )

    # 1. Call gemini-3.1-flash-lite-image in global region
    genai_client = genai.Client(vertexai=True, project=FIRESTORE_PROJECT, location="global")
    response = genai_client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
    )

    image_bytes = None
    if response.candidates:
        for part in response.candidates[0].content.parts:
            if getattr(part, "inline_data", None) and getattr(part.inline_data, "data", None):
                image_bytes = part.inline_data.data
                break

    if not image_bytes:
        return {"error": "Failed to extract image bytes from gemini-3.1-flash-lite-image response."}

    # 2. Resize to compact small thumbnail size (e.g. max 360x270)
    try:
        pil_img = Image.open(io.BytesIO(image_bytes))
        pil_img.thumbnail((360, 270), Image.Resampling.LANCZOS)
        thumb_buffer = io.BytesIO()
        pil_img.save(thumb_buffer, format="JPEG", quality=85, optimize=True)
        compact_image_bytes = thumb_buffer.getvalue()
    except Exception as e:
        print(f"Thumbnail resize fallback: {e}")
        compact_image_bytes = image_bytes

    clean_dish = re.sub(r"[^a-zA-Z0-9]+", "_", dish_name.strip()).lower()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{clean_dish}_sm_{timestamp}.jpg"

    # 3. Save with tool_context.save_artifact so it shows in Playground's Artifacts panel
    artifact_saved = False
    if tool_context:
        try:
            artifact_part = types.Part.from_bytes(data=compact_image_bytes, mime_type="image/jpeg")
            await tool_context.save_artifact(
                filename=filename,
                artifact=artifact_part,
                custom_metadata={"dish_name": dish_name, "restaurant_name": restaurant_name or "", "size": "compact_thumbnail"},
            )
            artifact_saved = True
        except Exception as e:
            print(f"Warning: tool_context.save_artifact failed: {e}")

    # 4. Upload directly to public Cloud Storage bucket without local file writes
    storage_client = _get_storage_client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(compact_image_bytes, content_type="image/jpeg")

    public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{filename}"

    return {
        "status": "success",
        "dish_name": dish_name,
        "restaurant_name": restaurant_name or "",
        "public_image_url": public_url,
        "filename": filename,
        "size": "compact_small",
        "artifact_saved_to_playground": artifact_saved,
    }


def get_popular_menu_items(
    restaurant_name_or_id: str,
    top_n: int = 3,
) -> dict:
    """Fetches the top popular menu items for a restaurant including dish name, price, rating, review snippet, ingredients, and allergen info.

    Args:
        restaurant_name_or_id: Name or ID of the restaurant (e.g. 'Verde Vegan Bistro', 'verde-bistro', 'Tokyo Ramen', 'Casa del Fuego').
        top_n: Number of top dishes to return (defaults to 3).

    Returns:
        Structured menu data with dish details ready for horizontal scrollable display.
    """
    db = _get_db()
    docs = db.collection("restaurants").stream()

    matched_restaurant = None
    query_str = restaurant_name_or_id.lower().strip()

    for doc in docs:
        data = doc.to_dict()
        r_name = data.get("name", "").lower()
        r_id = data.get("id", "").lower()
        if query_str in r_name or query_str in r_id or r_name in query_str:
            matched_restaurant = data
            break

    if not matched_restaurant:
        return {"status": "not_found", "message": f"Could not find restaurant matching '{restaurant_name_or_id}'."}

    menu_items = matched_restaurant.get("popular_menu", [])[:top_n]

    return {
        "status": "success",
        "restaurant_name": matched_restaurant.get("name"),
        "neighborhood": matched_restaurant.get("neighborhood"),
        "cuisine": matched_restaurant.get("cuisine"),
        "top_dishes_count": len(menu_items),
        "dishes": menu_items,
    }


def search_google_places(
    query: str,
    location_bias_text: Optional[str] = "San Francisco",
    max_results: int = 5,
) -> List[dict]:
    """Searches live restaurants using Google Places API (New)."""
    search_text = f"{query} in {location_bias_text}" if location_bias_text else query
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": PLACES_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.priceLevel,places.googleMapsUri,places.location,places.regularOpeningHours.openNow",
    }
    payload = json.dumps({"textQuery": search_text, "pageSize": min(max_results, 10)}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers=headers)

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            places = data.get("places", [])
            results = []
            for p in places:
                loc = p.get("location", {})
                results.append({
                    "name": p.get("displayName", {}).get("text", "Unknown"),
                    "address": p.get("formattedAddress", ""),
                    "rating": p.get("rating", "N/A"),
                    "user_ratings_total": p.get("userRatingCount", 0),
                    "price_level": p.get("priceLevel", "PRICE_LEVEL_UNSPECIFIED"),
                    "is_open_now": p.get("regularOpeningHours", {}).get("openNow"),
                    "google_maps_url": p.get("googleMapsUri", ""),
                    "latitude": loc.get("latitude"),
                    "longitude": loc.get("longitude"),
                    "source": "Google Places API (New)",
                })
            return results
    except Exception as e:
        return [{"error": f"Failed to query Google Places API: {str(e)}"}]


def find_nearby_restaurants(
    neighborhood: Optional[str] = None,
    cuisine: Optional[str] = None,
    allergy_to_avoid: Optional[str] = None,
    dietary_preference: Optional[str] = None,
    max_price: Optional[str] = None,
    use_live_google_places: bool = False,
) -> List[dict]:
    """Finds restaurants matching criteria such as neighborhood, cuisine, allergies, dietary restrictions, or live Google Places."""
    if use_live_google_places:
        query_parts = [cuisine or "", dietary_preference or "", "restaurants"]
        query = " ".join(p for p in query_parts if p).strip()
        return search_google_places(query=query, location_bias_text=neighborhood or "San Francisco")

    db = _get_db()
    docs = db.collection("restaurants").stream()
    results = []

    for doc in docs:
        data = doc.to_dict()

        if neighborhood and neighborhood.lower() not in data.get("neighborhood", "").lower():
            continue

        if cuisine and cuisine.lower() not in data.get("cuisine", "").lower():
            continue

        if allergy_to_avoid:
            allergens_free = [a.lower() for a in data.get("allergens_free", [])]
            if allergy_to_avoid.lower() not in allergens_free:
                continue

        if dietary_preference:
            dietary_tags = [d.lower() for d in data.get("dietary_tags", [])]
            cuisine_text = data.get("cuisine", "").lower()
            if dietary_preference.lower() not in dietary_tags and dietary_preference.lower() not in cuisine_text:
                continue

        if max_price:
            price_map = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}
            rest_val = price_map.get(data.get("price_range", "$$"), 2)
            max_val = price_map.get(max_price, 3)
            if rest_val > max_val:
                continue

        results.append(data)

    return results


def get_active_deals(
    day_of_week: Optional[str] = None,
    restaurant_name_or_id: Optional[str] = None,
) -> List[dict]:
    """Looks up ongoing dining deals, happy hours, and promotional discounts."""
    db = _get_db()
    if not day_of_week:
        day_of_week = datetime.datetime.now().strftime("%A")

    docs = db.collection("restaurants").stream()
    matched_deals = []

    for doc in docs:
        data = doc.to_dict()
        rest_name = data.get("name", "")
        rest_id = data.get("id", "")

        if restaurant_name_or_id:
            query_str = restaurant_name_or_id.lower()
            if query_str not in rest_name.lower() and query_str not in rest_id.lower():
                continue

        deals = data.get("deals", [])
        for deal in deals:
            valid_days = [d.lower() for d in deal.get("valid_days", [])]
            if not day_of_week or day_of_week.lower() in valid_days:
                matched_deals.append({
                    "restaurant_name": rest_name,
                    "neighborhood": data.get("neighborhood", ""),
                    "cuisine": data.get("cuisine", ""),
                    "deal_title": deal.get("title"),
                    "description": deal.get("description"),
                    "discount": deal.get("discount"),
                    "valid_days": deal.get("valid_days"),
                })

    return matched_deals


def save_permanent_allergies_and_diet(
    user_id: str,
    food_allergies: List[str],
    diet_lifestyle: Optional[str] = None,
    is_always_vegetarian: Optional[bool] = None,
    notes: Optional[str] = None,
) -> dict:
    """Permanently saves critical food allergies and dietary lifestyle in Firestore."""
    db = _get_db()
    user_ref = db.collection("user_profiles").document(user_id)
    payload = {
        "user_id": user_id,
        "permanent_allergies": food_allergies,
        "diet_lifestyle": diet_lifestyle or "",
        "is_always_vegetarian": is_always_vegetarian,
        "notes": notes or "",
        "updated_at": firestore.SERVER_TIMESTAMP,
    }
    user_ref.set(payload, merge=True)
    return {
        "status": "success",
        "scope": "permanent (Firestore)",
        "message": f"Permanent allergy & diet profile stored for user '{user_id}'.",
        "data": payload,
    }


def get_permanent_profile(user_id: str) -> dict:
    """Retrieves a user's permanent allergy safety and dietary preferences from Firestore."""
    db = _get_db()
    doc = db.collection("user_profiles").document(user_id).get()
    if not doc.exists:
        return {"status": "not_found", "message": f"No permanent profile found for user '{user_id}'."}
    return {"status": "found", "profile": doc.to_dict()}


def set_session_dining_preference(
    meal_choice: str,
    session_id: Optional[str] = "current_session",
    craving: Optional[str] = None,
) -> dict:
    """Sets a temporary dining preference for the CURRENT conversation/meal only (session scope)."""
    _SESSION_PREFERENCES[session_id] = {
        "meal_choice": meal_choice,
        "craving": craving or "",
        "timestamp": datetime.datetime.now().isoformat(),
    }
    return {
        "status": "success",
        "scope": "session_only (temporary)",
        "message": f"Set preference for this meal to '{meal_choice}' (will not affect permanent settings).",
        "current_session_preference": _SESSION_PREFERENCES[session_id],
    }


def get_session_dining_preference(session_id: Optional[str] = "current_session") -> dict:
    """Retrieves the temporary dining choice for the current session."""
    pref = _SESSION_PREFERENCES.get(session_id)
    if not pref:
        return {"status": "not_set", "message": "No session-specific meal preference set for this session."}
    return {"status": "found", "session_preference": pref}
