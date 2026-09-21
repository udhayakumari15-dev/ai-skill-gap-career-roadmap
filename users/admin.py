from django.contrib import admin
from .models import (
    UserProfile,
    Skill,
    UserSkill,
    JobRole,
    JobSkill,
    Education,
    UserProject,
    Experience,
    SkillGap,
    CareerRecommendation,
    Roadmap,
    RoadmapSkill,
    SkillProgress,
    CareerSimulation,
)

admin.site.register(UserProfile)
admin.site.register(Skill)
admin.site.register(UserSkill)
admin.site.register(JobRole)
admin.site.register(JobSkill)
admin.site.register(Education)
admin.site.register(UserProject)
admin.site.register(Experience)
admin.site.register(SkillGap)
admin.site.register(CareerRecommendation)
admin.site.register(Roadmap)
admin.site.register(RoadmapSkill)
admin.site.register(SkillProgress)
admin.site.register(CareerSimulation)