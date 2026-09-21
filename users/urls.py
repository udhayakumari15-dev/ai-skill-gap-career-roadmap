from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard,
         name="dashboard"),
    path(
        "skill-gap/<int:job_role_id>/",
        views.skill_gap_analysis,
        name="skill_gap_analysis"
    ),

    path(
        "job-roles/",
        views.job_role_selection,
        name="job_role_selection"
    ),

    path(
        "roadmap/<int:job_role_id>/",
        views.roadmap_view,
        name="roadmap"
    ),

    path(
        "update-progress/<int:skill_id>/",
        views.update_skill_progress,
        name="update_skill_progress"
    ),

    path(
        "career-recommendations/",
        views.career_recommendations,
        name="career_recommendations"
    ),
    path(
        "career-simulation/",
        views.career_simulation, 
        name="career_simulation"
     ),
     path(
    "login/",
    views.login_view,
    name="login"
),

path(
    "logout/",
    views.logout_view,
    name="logout"
),
path(
    "register/",
    views.register_view,
    name="register"
),
    
]