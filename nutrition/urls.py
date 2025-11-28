# nutrition/urls.py
from django.urls import path
from . import views

app_name = 'nutrition'

urlpatterns = [
    path('profile/', views.profile_edit, name='profile_edit'),
    path('generate/', views.generate_plan_view, name='generate_plan'),
    path('plans/<int:plan_id>/', views.plan_detail, name='plan_detail'),
    path('plans/<int:plan_id>/log/', views.log_meal, name='log_meal'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
