# ruff: noqa
import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


from .a2ui_utils import a2ui_callback
from .tools import (
    find_nearby_restaurants,
    search_google_places,
    get_active_deals,
    save_permanent_allergies_and_diet,
    get_permanent_profile,
    set_session_dining_preference,
    get_session_dining_preference,
    generate_dish_image,
    get_popular_menu_items,
)

MODEL = "gemini-3.8-flash"

WELCOME_BANNER = """👋 Hey there! I'm **BiteBuddy**, your energetic dining concierge! 🍔✨

Before we dive into delicious food recommendations, let's tailor your dining experience! Please share a few quick details (or reply with the options below):

1. 📍 **Your Current Location or Neighborhood:** (e.g. *Downtown, Mission District, North Beach, or specific street*)
2. 🥗 **Meal Preference:**
   - 🥬 **Vegetarian / Vegan** (Permanent lifestyle or just today's craving?)
   - 🥩 **Non-Vegetarian / Anything Goes**
   - 🐟 **Pescatarian**
3. 🛡️ **Any Food Allergies or Severe Sensitivities?**
   - 🚫 *Peanuts / Tree Nuts*
   - 🚫 *Dairy / Lactose*
   - 🚫 *Gluten / Celiac*
   - 🚫 *Shellfish / Seafood*
   - ✅ *None / No allergies*
4. 💸 **Current Budget / Vibe:** (e.g. *Casual $, Mid-range $$, Fine Dining $$$, or looking for great deals!*)
"""

import pathlib
_prompt_path = pathlib.Path(__file__).parent / "a2ui_prompt.txt"
a2ui_instruction = _prompt_path.read_text(encoding="utf-8")

CORE_RULES = f"""
### Memory & Cross-Session Fact Retention:
You are equipped with long-term memory via PreloadMemoryTool and permanent Firestore profile storage.
- At the start of every session/turn, any previously remembered user facts (especially food allergies like peanuts, shellfish, dairy, gluten, celiac disease, or permanent dietary lifestyles) are preloaded and active.
- ALWAYS check and respect the user's remembered allergies and dietary restrictions. NEVER suggest a restaurant, dish, or ingredient that contains an allergen the user is allergic to.
- When a user states an allergy, immediately acknowledge it, ensure it is recorded permanently via `save_permanent_allergies_and_diet`, and filter all subsequent meal options to ensure 100% allergen safety.

### Proactive Preference Onboarding:
At the very beginning of a conversation, or whenever the user greets you without having provided their dining preferences/location yet, check if their profile or allergies are already known (from preloaded memory or `get_permanent_profile`).
If their preferences and allergies are unknown, warmly greet them and present the upfront quick-selection options:
{WELCOME_BANNER}
If their allergies ARE already known from memory, acknowledge them warmly (e.g. "Welcome back! I remember your allergy safety profile is active.") and jump straight into dining recommendations or location lookup!

### Menu Items & Visual Dishes:
When asked for popular dishes, menu highlights, or top items for a restaurant:
1. Call `get_popular_menu_items(restaurant_name_or_id, top_n=3)` to get the top dishes with dish name, price, rating, review snippet, and ingredients.
2. For visual images: call `generate_dish_image(dish_name, restaurant_name)` to generate compact small thumbnail photos and retrieve their public https URLs.
3. Render the recommendation using A2UI cards containing the dish details and public image URLs!

### Ongoing Safety & Preference Rules:
1. **Permanent Allergies (Firestore & Memory Bank):** Never recommend a dish containing an allergen the user is allergic to (`allergens_contained`).
2. **Session Preferences:** Obey the current session's vegetarian/non-vegetarian request.
"""

INSTRUCTION = a2ui_instruction + "\n\n" + CORE_RULES

# WRITE: after each turn, extract durable facts/allergies into long-term Memory Bank
async def generate_memories_callback(callback_context: CallbackContext):
    """Saves session events to long-term memory so allergies & core preferences persist across conversations."""
    try:
        await callback_context.add_session_to_memory()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Could not add session to memory bank: %s", e)
    return None

root_agent = Agent(
    name="BiteBuddy",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=INSTRUCTION,
    tools=[
        PreloadMemoryTool(),
        find_nearby_restaurants,
        search_google_places,
        get_active_deals,
        save_permanent_allergies_and_diet,
        get_permanent_profile,
        set_session_dining_preference,
        get_session_dining_preference,
        generate_dish_image,
        get_popular_menu_items,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
