# nutrition/forms.py
from django import forms
from .models import UserProfile, MealLog

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['age', 'sex', 'height', 'weight', 'activity_level']  # updated field names

class MealLogForm(forms.ModelForm):
    class Meta:
        model = MealLog
        fields = ['meal', 'consumed', 'date']  # include the fields you want users to edit
