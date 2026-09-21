from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)
    target_career = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.full_name


class Skill(models.Model):
    SKILL_CATEGORY = [
        ('technical', 'Technical'),
        ('tool', 'Tool / Platform'),
        ('soft', 'Soft Skill'),
        ('domain', 'Domain Skill'),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=SKILL_CATEGORY)

    def __str__(self):
        return self.name


class UserSkill(models.Model):
    PROFICIENCY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency = models.CharField(
        max_length=20,
        choices=PROFICIENCY_LEVELS,
        default='beginner'
    )

    def __str__(self):
        return f"{self.user.username} - {self.skill.name}"


class JobRole(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class JobSkill(models.Model):
    IMPORTANCE_LEVELS = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    job_role = models.ForeignKey(
        JobRole,
        on_delete=models.CASCADE
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE
    )
    importance = models.CharField(
        max_length=20,
        choices=IMPORTANCE_LEVELS,
        default='medium'
    )

    def __str__(self):
        return f"{self.job_role.name} - {self.skill.name}"


class Education(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    degree = models.CharField(max_length=100)
    institution = models.CharField(max_length=200)
    specialization = models.CharField(max_length=100, blank=True)
    passing_year = models.IntegerField()
    percentage = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.degree}"


class UserProject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    technologies_used = models.CharField(max_length=300, blank=True)
    project_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class Experience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.job_title}"


class SkillGap(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    job_role = models.ForeignKey(JobRole, on_delete=models.CASCADE)

    current_level = models.IntegerField(default=0)
    required_level = models.IntegerField(default=5)
    gap = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.skill} - Gap: {self.gap}"


class CareerRecommendation(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    job_role = models.ForeignKey(JobRole, on_delete=models.CASCADE)

    match_score = models.FloatField(default=0)
    reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.job_role}"


class Roadmap(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    job_role = models.ForeignKey(JobRole, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_weeks = models.IntegerField(default=4)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.title}"


class RoadmapSkill(models.Model):
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    priority = models.IntegerField(default=1)
    target_level = models.IntegerField(default=5)
    estimated_hours = models.IntegerField(default=10)

    def __str__(self):
        return f"{self.roadmap} - {self.skill}"


class SkillProgress(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    current_level = models.IntegerField(default=0)
    target_level = models.IntegerField(default=5)
    progress_percentage = models.FloatField(default=0)

    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.skill} - {self.progress_percentage}%"


class CareerSimulation(models.Model):
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE
    )

    job_role = models.ForeignKey(
        JobRole,
        on_delete=models.CASCADE
    )

    selected_skills = models.ManyToManyField(
        Skill
    )

    current_score = models.FloatField(default=0)

    simulated_score = models.FloatField(default=0)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user} - {self.job_role} Simulation"