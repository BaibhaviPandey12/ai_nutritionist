# nutrition/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm, MealLogForm
from .models import UserProfile, MealPlan, Meal, MealLog
from .utils import create_and_save_plan
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

@login_required
def profile_edit(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            prof = form.save(commit=False)
            prof.user = request.user
            prof.save()
            return redirect('nutrition:generate_plan')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'nutrition/profile_form.html', {'form': form, 'profile': profile})

@login_required
def generate_plan_view(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    # generate 3-day plan (delete existing generated plans for simplicity)
    Meal.objects.filter(plan__user=request.user).delete()
    MealPlan.objects.filter(user=request.user).delete()
    plans = []
    for day in range(1,4):
        plan = create_and_save_plan(request.user, profile, day)
        plans.append(plan)
    return render(request, 'nutrition/plan_list.html', {'plans': plans})

@login_required
def plan_detail(request, plan_id):
    plan = get_object_or_404(MealPlan, id=plan_id, user=request.user)
    meals = plan.meals.all()
    log_form = MealLogForm()
    return render(request, 'nutrition/plan_detail.html', {'plan': plan, 'meals': meals, 'log_form': log_form})

@login_required
def log_meal(request, plan_id):
    if request.method == 'POST':
        plan = get_object_or_404(MealPlan, id=plan_id, user=request.user)
        form = MealLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.plan = plan
            log.date = date.today()
            log.save()
    return redirect('nutrition:plan_detail', plan_id=plan_id)

@login_required
def dashboard(request):
    # compliance: logs consumed / planned meals for plans generated in last 7 days
    plans = MealPlan.objects.filter(user=request.user).order_by('-created_at')[:10]
    logs = MealLog.objects.filter(user=request.user).order_by('-date')[:50]
    # compute simple compliance: consumed logs / total planned meals in those plans
    total_planned = sum(p.meals.count() for p in plans) or 1
    consumed = MealLog.objects.filter(user=request.user, consumed=True, plan__in=plans).count()
    compliance = int(consumed / total_planned * 100) if total_planned else 0
    # weight trend: use latest profile weight; we don't store historical weight in this simplified model
    profile = UserProfile.objects.filter(user=request.user).first()
    return render(request, 'nutrition/dashboard.html', {
        'plans': plans,
        'logs': logs,
        'compliance': compliance,
        'profile': profile
    })

