# My agent: BiteBuddy
One-liner: A friendly, energetic dining companion that helps hungry diners discover nearby restaurants, snag live food deals, and get safe dish recommendations personalized to their allergies, dietary restrictions, and cravings.

Tool coverage:
- Memory: Remembers user dietary preferences (vegan, keto, halal), food allergies (peanuts, shellfish, gluten, dairy), favorite cuisines, spice tolerance, and past spots visited.
- Tools:
  - `find_nearby_restaurants`: Search nearby restaurants and menus filtered by neighborhood/radius, cuisine, price, and allergen safety.
  - `get_active_deals`: Look up ongoing promotional offers, happy hour specials, and dining discounts.
  - `save_user_dietary_profile`: Persist user taste preferences, allergies, and dietary restrictions.
  - `make_reservation`: Book a table with dietary/allergy safety notes automatically forwarded to the restaurant.
- Catalog/UI: Rich A2UI restaurant cards (rating, cuisine, price range, allergy-safe badges) and deal comparison tables.
- Image gen: Generates mouth-watering visuals of signature dishes and restaurant ambiance.
- Sandbox: Computes bill splits, tip amounts, and discount savings.

Recommended for every project: memory, storage, tools, image generation, A2UI
Agent-specific / stretch (pick what fits): Code sandbox for discount/bill calculations, Firestore restaurant & deals database, live location filtering.
