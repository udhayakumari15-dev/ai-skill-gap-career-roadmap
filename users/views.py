from django.shortcuts import render, get_object_or_404, redirect 
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import (
    UserProfile,
    JobRole,
    Skill,
    Roadmap,
    RoadmapSkill,
    SkillProgress,
    SkillGap,
    CareerRecommendation,
    CareerSimulation,
)

from .services import (
    analyze_skill_gap,
    create_career_roadmap,
    generate_career_recommendations,
    simulate_career,
)


@login_required
def skill_gap_analysis(request, job_role_id):

    profile = get_object_or_404(
        UserProfile,
        user_id=request.user.id
    )

    job_role = get_object_or_404(
        JobRole,
        id=job_role_id
    )

    result = analyze_skill_gap(
        profile,
        job_role
    )

    create_career_roadmap(
        profile,
        job_role
    )

    return render(
        request,
        "users/skill_gap_analysis.html",
        {
            "result": result
        }
    )

@login_required
def job_role_selection(request):

    job_roles = JobRole.objects.all()

    return render(
        request,
        "users/job_role_selection.html",
        {
            "job_roles": job_roles
        }
    )


@login_required
def roadmap_view(request, job_role_id):

    profile = get_object_or_404(
        UserProfile,
        user_id=request.user.id
    )

    job_role = get_object_or_404(
        JobRole,
        id=job_role_id
    )

    roadmap = get_object_or_404(
        Roadmap,
        user=profile,
        job_role=job_role
    )

    roadmap_skills = RoadmapSkill.objects.filter(
        roadmap=roadmap
    ).order_by("priority")

    active_roadmap_skills = []
    completed_roadmap_skills = []

    for item in roadmap_skills:

        progress = SkillProgress.objects.filter(
            user=profile,
            skill=item.skill
        ).first()

        if progress:

            item.progress_percentage = progress.progress_percentage

            if progress.current_level < progress.target_level:
                active_roadmap_skills.append(item)
            else:
                completed_roadmap_skills.append(item)

        else:

            item.progress_percentage = 0
            active_roadmap_skills.append(item)

    roadmap_skills = active_roadmap_skills

    return render(
        request,
        "users/roadmap.html",
        {
            "roadmap": roadmap,
            "roadmap_skills": roadmap_skills,
            "completed_roadmap_skills": completed_roadmap_skills,
        }
    )


def update_skill_progress(request, skill_id):

    profile = get_object_or_404(
        UserProfile,
        user_id=request.user.id
    )

    skill = get_object_or_404(
        Skill,
        id=skill_id
    )

    progress = SkillProgress.objects.filter(
        user=profile,
        skill=skill
    ).first()

    roadmap_skill = RoadmapSkill.objects.filter(
        roadmap__user=profile,
        skill=skill
    ).first()

    job_role_id = roadmap_skill.roadmap.job_role.id

    if request.method == "POST":

        progress_percentage = float(
            request.POST.get(
                "progress_percentage",
                0
            )
        )

        progress_percentage = max(
            0,
            min(progress_percentage, 100)
        )

        progress.progress_percentage = progress_percentage

        progress.current_level = round(
            (progress_percentage / 100) *
            progress.target_level
        )

        progress.save()

        skill_gap = SkillGap.objects.filter(
            user=profile,
            skill=skill,
            job_role=roadmap_skill.roadmap.job_role
        ).first()

        if skill_gap:

            skill_gap.current_level = progress.current_level

            skill_gap.gap = max(
                skill_gap.required_level - progress.current_level,
                0
            )

            skill_gap.save()

            analyze_skill_gap(
                profile,
                roadmap_skill.roadmap.job_role
            )

        create_career_roadmap(
            profile,
            roadmap_skill.roadmap.job_role
        )

        return redirect(
            "roadmap",
            job_role_id=job_role_id
        )

    return render(
        request,
        "users/update_progress.html",
        {
            "skill": skill,
            "progress": progress,
        }
    )

@login_required
def career_recommendations(request):

    profile = get_object_or_404(
        UserProfile,
        user_id=request.user.id
    )

    recommendations = generate_career_recommendations(
        profile
    )

    recommendations = sorted(
        recommendations,
        key=lambda x: x.match_score,
        reverse=True
    )

    return render(
        request,
        "users/career_recommendations.html",
        {
            "recommendations": recommendations,
        }
    )
@login_required
def career_simulation(request):
    profile = UserProfile.objects.get(user=request.user)

    job_roles = JobRole.objects.all()

    selected_job_role_id = request.GET.get("job_role")

    selected_job_role = None
    skills = []

    if selected_job_role_id:
        selected_job_role = JobRole.objects.get(
            id=selected_job_role_id
        )

        skills = SkillProgress.objects.filter(
            user=profile
        )

    simulation = None

    if request.method == "POST":

        job_role_id = request.POST.get("job_role")

        selected_skill_ids = request.POST.getlist(
            "selected_skills"
        )

        selected_job_role = JobRole.objects.get(
            id=job_role_id
        )

        simulation = simulate_career(
            profile,
            selected_job_role,
            selected_skill_ids
        )

    improvement = None

    if simulation:
        improvement = round(
            simulation.simulated_score - simulation.current_score,
            2
        )

    return render(
        request,
        "users/career_simulation.html",
        {
            "job_roles": job_roles,
            "selected_job_role": selected_job_role,
            "skills": skills,
            "simulation": simulation,
            "improvement": improvement,
        }
    )
def simulation_history(request):
    profile = UserProfile.objects.get(user=request.user)

    simulations = CareerSimulation.objects.filter(
        user=profile
    ).order_by("-created_at")

    return render(
        request,
        "users/simulation_history.html",
        {
            "simulations": simulations,
        }
    )
@login_required
def dashboard(request):
    profile = UserProfile.objects.get(user=request.user)

    latest_simulation = CareerSimulation.objects.filter(
        user=profile
    ).order_by("-id").first()

    skill_gap_count = SkillGap.objects.filter(
        user=profile
    ).count()

    simulation_count = CareerSimulation.objects.filter(
        user=profile
    ).count()

    return render(
        request,
        "users/dashboard.html",
        {
            "profile": profile,
            "latest_simulation": latest_simulation,
            "skill_gap_count": skill_gap_count,
            "simulation_count": simulation_count,
        }
    )
def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        return render(
            request,
            "users/login.html",
            {
                "error": "Invalid username or password."
            }
        )

    return render(
        request,
        "users/login.html"
    )


def logout_view(request):
    logout(request)
    return redirect("login")
def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        full_name = request.POST.get("full_name")

        if User.objects.filter(username=username).exists():
            return render(
                request,
                "users/register.html",
                {
                    "error": "Username already exists."
                }
            )

        user = User.objects.create_user(
            username=username,
            password=password
        )

        UserProfile.objects.create(
            user=user,
            full_name=full_name
        )

        login(request, user)

        return redirect("dashboard")

    return render(
        request,
        "users/register.html"
    )