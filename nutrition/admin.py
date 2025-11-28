from django.contrib import admin
from .models import UserProfile, MealPlan, Meal

admin.site.register(UserProfile)
admin.site.register(MealPlan)
admin.site.register(Meal)
