from .models import (
    UserProfile,
    UserSkill,
    JobRole,
    JobSkill,
    SkillGap,
    Roadmap,
    RoadmapSkill,
    SkillProgress,
    CareerRecommendation,
    CareerSimulation
)


PROFICIENCY_LEVELS = {
    "beginner": 1,
    "intermediate": 3,
    "advanced": 5,
}


IMPORTANCE_WEIGHTS = {
    "high": 3,
    "medium": 2,
    "low": 1,
}


def analyze_skill_gap(user_profile, job_role):

    job_skills = JobSkill.objects.filter(
        job_role=job_role
    )

    user_skills = UserSkill.objects.filter(
        user_id=user_profile.user_id
    )

    user_skill_levels = {}

    for user_skill in user_skills:
        user_skill_levels[user_skill.skill_id] = (
            PROFICIENCY_LEVELS.get(
                user_skill.proficiency,
                0
            )
        )

    total_weight = 0
    achieved_weight = 0
    results = []

    for job_skill in job_skills:

        skill = job_skill.skill
        required_level = 5

        skill_progress = SkillProgress.objects.filter(
            user=user_profile,
            skill=skill
        ).first()

        if skill_progress:
            current_level = skill_progress.current_level
        else:
            current_level = user_skill_levels.get(
                skill.id,
                0
            )

        gap = max(
            required_level - current_level,
            0
        )

        weight = IMPORTANCE_WEIGHTS.get(
            job_skill.importance,
            1
        )

        total_weight += weight

        achieved_weight += (
            current_level / required_level
        ) * weight

        SkillGap.objects.update_or_create(
            user=user_profile,
            skill=skill,
            job_role=job_role,
            defaults={
                "current_level": current_level,
                "required_level": required_level,
                "gap": gap,
            }
        )

        if current_level >= required_level:
            status = "Matched"

        elif current_level > 0:
            status = "Partially Matched"

        else:
            status = "Missing"

        results.append({
            "skill": skill.name,
            "current_level": current_level,
            "required_level": required_level,
            "gap": gap,
            "importance": job_skill.importance,
            "status": status,
        })

    if total_weight > 0:

        readiness_score = (
            achieved_weight / total_weight
        ) * 100

    else:

        readiness_score = 0

    return {
        "job_role": job_role.name,
        "job_role_id": job_role.id,
        "readiness_score": round(
            readiness_score,
            2
        ),
        "skill_gaps": results,
    }


def create_career_roadmap(user_profile, job_role):

    roadmap, created = Roadmap.objects.get_or_create(
        user=user_profile,
        job_role=job_role,
        defaults={
            "title": f"{job_role.name} Career Roadmap",
            "description": (
                f"Personalized learning roadmap for "
                f"becoming a {job_role.name}."
            ),
            "duration_weeks": 8,
        }
    )

    skill_gaps = SkillGap.objects.filter(
        user=user_profile,
        job_role=job_role,
        gap__gt=0
    ).order_by("-gap")

    priority = 1

    for gap in skill_gaps:

        skill = gap.skill

        roadmap_skill, created = RoadmapSkill.objects.get_or_create(
            roadmap=roadmap,
            skill=skill,
            defaults={
                "priority": priority,
                "target_level": gap.required_level,
                "estimated_hours": gap.gap * 10,
            }
        )

        if not created:

            roadmap_skill.priority = priority
            roadmap_skill.target_level = gap.required_level
            roadmap_skill.estimated_hours = gap.gap * 10
            roadmap_skill.save()

        SkillProgress.objects.get_or_create(
            user=user_profile,
            skill=skill,
            defaults={
                "current_level": gap.current_level,
                "target_level": gap.required_level,
                "progress_percentage": (
                    gap.current_level / gap.required_level
                ) * 100
                if gap.required_level > 0
                else 0,
            }
        )

        priority += 1

    return roadmap


def generate_career_recommendations(user_profile):

    job_roles = JobRole.objects.all()

    recommendations = []

    for job_role in job_roles:

        result = analyze_skill_gap(
            user_profile,
            job_role
        )

        match_score = result["readiness_score"]

        matched_skills = []
        partial_skills = []
        missing_skills = []

        for skill_data in result["skill_gaps"]:

            if skill_data["status"] == "Matched":
                matched_skills.append(
                    skill_data["skill"]
                )

            elif skill_data["status"] == "Partially Matched":
                partial_skills.append(
                    skill_data["skill"]
                )

            else:
                missing_skills.append(
                    skill_data["skill"]
                )

        if match_score >= 80:

            reason = (
                "Strong match based on your current skills. "
                "Only a few improvements may be required."
            )

        elif match_score >= 60:

            reason = (
                "Good potential for this career. "
                "Some important skills need improvement."
            )

        elif match_score >= 40:

            reason = (
                "Moderate match. "
                "Several skills should be developed for this career."
            )

        else:

            reason = (
                "Currently a low match. "
                "A significant number of required skills "
                "need to be developed."
            )

        recommendation, created = (
            CareerRecommendation.objects.update_or_create(
                user=user_profile,
                job_role=job_role,
                defaults={
                    "match_score": match_score,
                    "reason": reason,
                }
            )
        )

        recommendation.matched_skills = matched_skills
        recommendation.partial_skills = partial_skills
        recommendation.missing_skills = missing_skills

        recommendations.append(
            recommendation
        )

    return recommendations
def simulate_career(
    user_profile,
    job_role,
    selected_skill_ids
):
    result = analyze_skill_gap(
        user_profile,
        job_role
    )

    current_score = result["readiness_score"]

    simulated_score = current_score

    selected_skills = SkillProgress.objects.filter(
        user=user_profile,
        skill_id__in=selected_skill_ids
    )

    for progress in selected_skills:
        current_level = progress.current_level
        target_level = progress.target_level

        if target_level > current_level:
            improvement = (
                target_level - current_level
            )

            simulated_score += (
                improvement / target_level
            ) * 10

    simulated_score = min(
        simulated_score,
        100
    )

    simulation = CareerSimulation.objects.create(
        user=user_profile,
        job_role=job_role,
        current_score=current_score,
        simulated_score=round(
            simulated_score,
            2
        )
    )

    simulation.selected_skills.set(
        selected_skill_ids
    )

    return simulation