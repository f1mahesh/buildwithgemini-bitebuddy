"""Seed script for BiteBuddy Firestore database with rich menu items including ingredients, price, and reviews."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-0ec1576f1d28"

RESTAURANTS_DATA = [
    {
        "id": "verde-bistro",
        "name": "Verde Vegan Bistro",
        "neighborhood": "Downtown",
        "address": "450 Market St, San Francisco, CA 94105",
        "latitude": 37.7915,
        "longitude": -122.3999,
        "cuisine": "Vegan / Mediterranean",
        "price_range": "$$",
        "rating": 4.8,
        "allergens_free": ["dairy", "shellfish", "eggs"],
        "dietary_tags": ["vegan", "vegetarian", "plant-based"],
        "signature_dishes": ["Truffle Mushroom Risotto", "Crispy Falafel Mezze Plate", "Charred Avocado Toast"],
        "popular_menu": [
            {
                "dish_name": "Truffle Mushroom Risotto",
                "price": "$22",
                "rating": 4.9,
                "review_snippet": "Incredibly creamy and flavorful without any dairy. A must-try masterpiece!",
                "ingredients": ["Carnaroli rice", "wild forest mushrooms", "white truffle oil", "thyme", "cashew cream parmesan"],
                "dietary": "Vegan, Dairy-Free, Gluten-Free",
                "allergens_contained": ["tree nuts (cashew)"]
            },
            {
                "dish_name": "Crispy Falafel Mezze Plate",
                "price": "$18",
                "rating": 4.8,
                "review_snippet": "Crispy on the outside, fluffy inside. The homemade garlic tahini is to die for.",
                "ingredients": ["Organic chickpeas", "fresh parsley", "garlic", "tahini sesame", "sumac pickled onions", "warm pita"],
                "dietary": "Vegan, Nut-Free",
                "allergens_contained": ["sesame", "gluten (pita)"]
            },
            {
                "dish_name": "Mediterranean Charred Avocado Bowl",
                "price": "$19",
                "rating": 4.7,
                "review_snippet": "Super fresh and energizing lunch bowl loaded with healthy fats and grain crunch.",
                "ingredients": ["Hass avocado", "tricolor quinoa", "kalamata olives", "heirloom tomatoes", "cucumber", "lemon-herb vinaigrette"],
                "dietary": "Vegan, Gluten-Free, Nut-Free",
                "allergens_contained": []
            }
        ],
        "deals": [
            {
                "title": "Green Monday Special",
                "description": "20% off all plant-based bowls every Monday.",
                "valid_days": ["Monday"],
                "discount": "20%"
            },
            {
                "title": "Happy Hour Mezze",
                "description": "Free fresh pita & hummus with any craft kombucha or drink between 4-6 PM.",
                "valid_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "discount": "Free Appetizer"
            }
        ]
    },
    {
        "id": "tokyo-noodle-bar",
        "name": "Tokyo Ramen & Yakitori",
        "neighborhood": "Uptown / Japantown",
        "address": "1737 Post St, San Francisco, CA 94115",
        "latitude": 37.7852,
        "longitude": -122.4298,
        "cuisine": "Japanese",
        "price_range": "$$",
        "rating": 4.7,
        "allergens_free": ["dairy", "peanuts"],
        "dietary_tags": ["halal-chicken-available", "pescatarian"],
        "signature_dishes": ["Black Garlic Tonkotsu Ramen", "Gluten-Free Shoyu Ramen with Rice Noodles", "Grilled Chicken Yakitori"],
        "popular_menu": [
            {
                "dish_name": "Black Garlic Tonkotsu Ramen",
                "price": "$19",
                "rating": 4.9,
                "review_snippet": "Rich, deeply aromatic broth layered with savory black garlic oil. Peak comfort food.",
                "ingredients": ["20-hour simmered pork bone broth", "charred chashu pork belly", "black garlic oil", "marinated soft-boiled egg", "scallions", "artisan ramen noodles"],
                "dietary": "Dairy-Free, Peanut-Free",
                "allergens_contained": ["gluten", "egg", "soy"]
            },
            {
                "dish_name": "Gluten-Free Shoyu Ramen",
                "price": "$20",
                "rating": 4.8,
                "review_snippet": "Finally a legit gluten-free ramen with bouncy rice noodles that doesn't sacrifice broth depth!",
                "ingredients": ["Tamari gluten-free shoyu broth", "slow-poached chicken breast", "fresh artisanal rice noodles", "wood ear mushrooms", "nori", "bamboo shoots"],
                "dietary": "Gluten-Free, Dairy-Free, Peanut-Free",
                "allergens_contained": ["soy", "egg"]
            },
            {
                "dish_name": "Tare Glazed Chicken Yakitori Skewers",
                "price": "$14",
                "rating": 4.7,
                "review_snippet": "Smoky char from binchotan charcoal with sweet and savory homemade tare glaze.",
                "ingredients": ["Free-range chicken thighs", "scallions", "sweet mirin tare reduction", "shichimi togarashi spice"],
                "dietary": "Dairy-Free, Peanut-Free",
                "allergens_contained": ["soy"]
            }
        ],
        "deals": [
            {
                "title": "Ramen Wednesday",
                "description": "Buy 1 Ramen, get 50% off second bowl for your buddy.",
                "valid_days": ["Wednesday"],
                "discount": "BOGO 50%"
            }
        ]
    },
    {
        "id": "casa-fuego",
        "name": "Casa del Fuego",
        "neighborhood": "Mission District",
        "address": "2850 Mission St, San Francisco, CA 94110",
        "latitude": 37.7516,
        "longitude": -122.4183,
        "cuisine": "Mexican",
        "price_range": "$",
        "rating": 4.6,
        "allergens_free": ["peanuts", "tree-nuts", "shellfish"],
        "dietary_tags": ["gluten-free-options", "halal-beef"],
        "signature_dishes": ["Birria Tacos with Consomé", "Charred Street Corn Esquites", "Crispy Carnitas Bowl"],
        "popular_menu": [
            {
                "dish_name": "Crispy Birria Tacos with Consomé",
                "price": "$16",
                "rating": 4.9,
                "review_snippet": "Insanely tender braised beef wrapped in griddled corn tortillas with a rich sipping broth.",
                "ingredients": ["Slow-braised spiced beef shank", "melted Oaxaca cheese", "fresh cilantro", "diced white onions", "guajillo chile dipping broth", "crispy corn tortillas"],
                "dietary": "Gluten-Free, Peanut-Free, Shellfish-Free",
                "allergens_contained": ["dairy (cheese)"]
            },
            {
                "dish_name": "Charred Street Corn Esquites",
                "price": "$9",
                "rating": 4.8,
                "review_snippet": "The roasted sweet corn with smoky tajín and creamy cotija is bursting with bold flavor.",
                "ingredients": ["Fire-roasted sweet corn off the cob", "cotija cheese", "chipotle crema", "fresh lime juice", "tajín chili powder"],
                "dietary": "Vegetarian, Gluten-Free, Peanut-Free",
                "allergens_contained": ["dairy"]
            },
            {
                "dish_name": "Carnitas Fiesta Bowl",
                "price": "$15",
                "rating": 4.6,
                "review_snippet": "Golden pork carnitas cooked in citrus and lard paired with zesty black beans and guacamole.",
                "ingredients": ["Slow-simmered crispy pork shoulder", "cilantro-lime rice", "black beans", "fresh guacamole", "pico de gallo"],
                "dietary": "Gluten-Free, Nut-Free, Shellfish-Free",
                "allergens_contained": []
            }
        ],
        "deals": [
            {
                "title": "Taco Tuesday Fiesta",
                "description": "$2.50 Birria and Carnitas tacos all day Tuesday.",
                "valid_days": ["Tuesday"],
                "discount": "$2.50 Tacos"
            },
            {
                "title": "Lunch Combo",
                "description": "3 Tacos + Drink + Churro for $12 from 11:30 AM to 2:30 PM.",
                "valid_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "discount": "$12 Combo"
            }
        ]
    },
    {
        "id": "bella-italia",
        "name": "Trattoria Bella Italia",
        "neighborhood": "Downtown",
        "address": "580 Bush St, San Francisco, CA 94108",
        "latitude": 37.7904,
        "longitude": -122.4072,
        "cuisine": "Italian",
        "price_range": "$$$",
        "rating": 4.9,
        "allergens_free": ["peanuts", "shellfish"],
        "dietary_tags": ["vegetarian-friendly", "gluten-free-pasta-available"],
        "signature_dishes": ["Handmade Gluten-Free Pappardelle with Wild Boar", "Woodfired Margherita DOC", "Truffle Gnocchi"],
        "popular_menu": [
            {
                "dish_name": "Handmade Gluten-Free Pappardelle",
                "price": "$28",
                "rating": 4.9,
                "review_snippet": "Silky, melt-in-your-mouth pasta with a 12-hour Tuscan ragù that rivals any high-end Florence trattoria.",
                "ingredients": ["Hand-rolled gluten-free pasta ribbons", "slow-braised wild boar shoulder", "San Marzano tomatoes", "aged Parmigiano-Reggiano", "fresh rosemary"],
                "dietary": "Gluten-Free, Peanut-Free",
                "allergens_contained": ["dairy", "egg"]
            },
            {
                "dish_name": "Woodfired Margherita DOC Pizza",
                "price": "$23",
                "rating": 4.8,
                "review_snippet": "Classic Neapolitan crust blistered to perfection with creamy buffalo mozzarella and sweet basil.",
                "ingredients": ["Double-fermented dough", "San Marzano tomato sauce", "mozzarella di bufala Campana", "fresh basil leaves", "extra virgin olive oil"],
                "dietary": "Vegetarian, Peanut-Free",
                "allergens_contained": ["gluten", "dairy"]
            },
            {
                "dish_name": "Truffle Ricotta Gnocchi",
                "price": "$26",
                "rating": 4.7,
                "review_snippet": "Pillowy soft ricotta dumplings coated in a velvety black summer truffle butter glaze.",
                "ingredients": ["Handmade sheep's milk ricotta gnocchi", "Norcia black truffle paste", "browned sage butter", "grated pecorino romano"],
                "dietary": "Vegetarian, Peanut-Free",
                "allergens_contained": ["gluten", "dairy", "egg"]
            }
        ],
        "deals": [
            {
                "title": "Wine & Pasta Thursday",
                "description": "Complimentary glass of Chianti with any handmade pasta entree.",
                "valid_days": ["Thursday"],
                "discount": "Free Wine"
            }
        ]
    },
    {
        "id": "harbor-catch",
        "name": "Harbor Catch Seafood & Grill",
        "neighborhood": "Marina",
        "address": "3120 Scott St, San Francisco, CA 94123",
        "latitude": 37.8012,
        "longitude": -122.4411,
        "cuisine": "Seafood / American",
        "price_range": "$$$",
        "rating": 4.5,
        "allergens_free": ["peanuts", "dairy"],
        "dietary_tags": ["pescatarian", "keto"],
        "signature_dishes": ["Pan-Seared Pacific Halibut", "Garlic Butter King Crab Legs", "Ceviche Mixto"],
        "popular_menu": [
            {
                "dish_name": "Pan-Seared Pacific Halibut",
                "price": "$34",
                "rating": 4.8,
                "review_snippet": "Crispy golden skin, flaky tender white fish atop asparagus and citrus reduction.",
                "ingredients": ["Wild-caught Pacific halibut filet", "grilled asparagus spears", "Meyer lemon emulsion", "microgreens", "sea salt"],
                "dietary": "Pescatarian, Keto, Gluten-Free, Dairy-Free, Peanut-Free",
                "allergens_contained": ["fish"]
            },
            {
                "dish_name": "Garlic Herb Alaskan King Crab Legs",
                "price": "$48",
                "rating": 4.9,
                "review_snippet": "Sweet, colossal crab meat bursting with juice, served with drawn herb oil and lemon.",
                "ingredients": ["Steamed Alaskan red king crab legs", "roasted garlic herb oil", "fresh chives", "grilled lemon wedges"],
                "dietary": "Pescatarian, Keto, Gluten-Free, Dairy-Free",
                "allergens_contained": ["crustacean shellfish"]
            },
            {
                "dish_name": "Citrus Coastal Ceviche",
                "price": "$21",
                "rating": 4.7,
                "review_snippet": "Refreshing cured sea bass with serrano peppers and avocado—light and vibrant.",
                "ingredients": ["Fresh local striped bass", "lime juice", "serrano chiles", "red onions", "avocado", "cilantro", "plantain chips"],
                "dietary": "Pescatarian, Gluten-Free, Dairy-Free, Peanut-Free",
                "allergens_contained": ["fish"]
            }
        ],
        "deals": [
            {
                "title": "Weekend Catch Special",
                "description": "15% off chef's special whole fish platter on weekends.",
                "valid_days": ["Saturday", "Sunday"],
                "discount": "15%"
            }
        ]
    }
]


def seed():
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    restaurants_col = db.collection("restaurants")

    for item in RESTAURANTS_DATA:
        doc_id = item["id"]
        doc_ref = restaurants_col.document(doc_id)
        doc_ref.set(item)
        print(f"  ✓ Seeded restaurant with top 3 popular dishes: {item['name']} ({doc_id})")

    print("\nFirestore database successfully seeded with popular menus!")


if __name__ == "__main__":
    seed()
