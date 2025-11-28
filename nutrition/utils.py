# nutrition/utils.py
import random
from .models import MealPlan, Meal
from datetime import datetime


SAMPLE_RECIPES = [
    # Name, dietary tags list, allergies list, calories, protein, carbs, fat, recipe text
    ("Oats porridge with milk & bananas", ["vegetarian","omnivore"], ["nuts"], 350, 12, 55, 8, "Oats cooked in milk with sliced banana and a tsp honey."),
    ("Chickpea salad", ["vegan","vegetarian","omnivore"], [], 300, 15, 30, 10, "Chickpeas, cucumber, tomato, lemon, olive oil."),
    ("Grilled chicken & veggies", ["omnivore"], [], 500, 40, 35, 18, "Grilled chicken breast with roasted vegetables."),
    ("Paneer curry with rice", ["vegetarian","omnivore"], [], 600, 25, 70, 20, "Paneer cooked in tomato gravy served with rice."),
    ("Fruit & yogurt bowl", ["vegetarian","omnivore"], [], 200, 8, 30, 4, "Mixed fruits with yogurt."),
    ("Peanut butter toast", ["vegetarian","omnivore"], ["peanuts"], 320, 12, 30, 16, "Wholegrain toast with peanut butter."),
    ("Mixed nuts small bowl", ["vegetarian","omnivore"], ["nuts"], 180, 6, 8, 15, "Handful of mixed nuts."),
    ("Tofu stir fry", ["vegan","vegetarian","omnivore"], [], 420, 20, 40, 18, "Tofu with mixed vegetables and soy sauce."),
    ("Boiled eggs and spinach", ["omnivore"], [], 250, 18, 6, 15, "2 boiled eggs with sautéed spinach."),
]

def parse_allergies(allergies_str):
    return [a.strip().lower() for a in (allergies_str or "").split(",") if a.strip()]

def calculate_bmr(weight_kg, height_cm, age, sex):
    # Mifflin-St Jeor
    if sex == 'male':
        bmr = 10*weight_kg + 6.25*height_cm - 5*age + 5
    else:
        bmr = 10*weight_kg + 6.25*height_cm - 5*age - 161
    return bmr

def activity_multiplier(activity):
    mapping = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9
    }
    return mapping.get(activity, 1.2)

def goal_calorie_adjust(calories, goal):
    if goal == 'lose':
        return int(calories - 300)  # mild deficit ~300 kcal/day
    if goal == 'gain':
        return int(calories + 300)
    return int(calories)

def select_recipe(diet_pref, allergies, min_cal=None, max_cal=None):
    # filter
    choices = []
    for r in SAMPLE_RECIPES:
        name, tags, allergs, cal, p, c, f, recipe_text = r
        # allergies: if any recipe allergen matches user's allergy, skip
        if any(a.lower() in [x.lower() for x in allergs] for a in allergies):
            continue
        # dietary pref: if user is vegan, recipe must have 'vegan' tag, etc. If empty or 'omnivore', accept most.
        if diet_pref:
            dp = diet_pref.lower()
            if dp == 'vegan' and 'vegan' not in tags:
                continue
            if dp == 'vegetarian' and 'vegetarian' not in tags and dp not in tags:
                continue
        # cal range
        if min_cal and cal < min_cal: continue
        if max_cal and cal > max_cal: continue
        choices.append(r)
    if not choices:
        # fallback to any recipe not conflicting allergies
        for r in SAMPLE_RECIPES:
            if not any(a.lower() in [x.lower() for x in r[2]] for a in allergies):
                choices.append(r)
    return random.choice(choices) if choices else None

def generate_day_plan(user_profile, day=1):
    # compute calorie target
    bmr = calculate_bmr(user_profile.weight_kg, user_profile.height_cm, user_profile.age, user_profile.sex)
    tdee = bmr * activity_multiplier(user_profile.activity)
    target = goal_calorie_adjust(tdee, user_profile.goal)
    # split: breakfast 25%, lunch 30%, dinner 30%, snacks 15% (split into 2 snack slots)
    slots = {
        "breakfast": int(target * 0.25),
        "lunch": int(target * 0.30),
        "dinner": int(target * 0.30),
        "snack1": int(target * 0.075),
        "snack2": int(target * 0.075),
    }
    allergies = parse_allergies(user_profile.allergies)
    plan_meals = []
    for slot, calories in slots.items():
        # allow +/- 15% flexibility on target per meal
        min_c = int(calories * 0.85)
        max_c = int(calories * 1.15)
        recipe = select_recipe(user_profile.dietary_pref, allergies, min_c, max_c)
        if recipe:
            name, tags, allergs, cal, p, c, f, recipe_text = recipe
            plan_meals.append({
                "slot": slot,
                "name": name,
                "recipe": recipe_text,
                "calories": cal,
                "protein": p,
                "carbs": c,
                "fat": f
            })
        else:
            # fallback: create a placeholder meal
            plan_meals.append({
                "slot": slot,
                "name": "Simple meal",
                "recipe": "No recipe available. Mix protein + carbs + veg.",
                "calories": calories,
                "protein": round(calories*0.15/4,1),
                "carbs": round(calories*0.5/4,1),
                "fat": round(calories*0.35/9,1)
            })
    explanation = f"Calorie target ~{target} kcal/day based on Mifflin-St Jeor and activity. Split across meals to match goal '{user_profile.goal}'."
    return {
        "total_calories": target,
        "meals": plan_meals,
        "explanation": explanation
    }

def create_and_save_plan(user, user_profile, day):
    plan_data = generate_day_plan(user_profile, day)
    plan = MealPlan.objects.create(
        user=user,
        day=day,
        total_calories=plan_data["total_calories"],
        explanation=plan_data["explanation"]
    )
    for m in plan_data["meals"]:
        Meal.objects.create(
            plan=plan,
            slot=m["slot"],
            name=m["name"],
            recipe=m["recipe"],
            calories=m["calories"],
            protein_g=m["protein"],
            carbs_g=m["carbs"],
            fat_g=m["fat"]
        )
    return plan
