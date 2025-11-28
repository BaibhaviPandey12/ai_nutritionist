# nutrition/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    ACTIVITY_LEVEL_CHOICES = [
        ('sedentary', 'Sedentary'),
        ('light', 'Lightly active'),
        ('moderate', 'Moderately active'),
        ('active', 'Active'),
        ('very_active', 'Very active'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField(default=18)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, default='M')
    height = models.FloatField(null=True, blank=True)  # in cm
    weight = models.FloatField(null=True, blank=True)  # in kg
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVEL_CHOICES, default='sedentary')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class MealPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    day = models.PositiveIntegerField()  # 1,2,3 for 3-day plan
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Plan for {self.user.username} - Day {self.day}"


class Meal(models.Model):
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]

    plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name='meals')
    name = models.CharField(max_length=100)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES, default='breakfast')
    calories = models.PositiveIntegerField(default=0)
    protein = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    fat = models.FloatField(default=0)

    def __str__(self):
        return f"{self.name} ({self.meal_type})"


class MealLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    consumed = models.BooleanField(default=False)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Log for {self.user.username} - {self.meal.name} on {self.date}"
