import os
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# File upload path functions
def notes_upload_path(instance, filename):
    """Organize notes by user and subject"""
    user_folder = f"user_{instance.created_by.id}"
    subject_folder = slugify(instance.subject.name if hasattr(instance.subject, 'name') else instance.subject)
    return f"notes/{user_folder}/{subject_folder}/{filename}"

def exam_papers_upload_path(instance, filename):
    """Organize exam papers by year and subject"""
    year = instance.year
    subject = slugify(instance.subject.name)
    return f"exam_papers/{year}/{subject}/{filename}"

def profile_picture_path(instance, filename):
    """Organize profile pictures by user"""
    user_folder = f"user_{instance.user.id}"
    return f"profiles/{user_folder}/{filename}"

def study_materials_path(instance, filename):
    """Organize study materials by type and subject"""
    material_type = slugify(instance.material_type)
    subject = slugify(instance.subject.name)
    return f"study_materials/{material_type}/{subject}/{filename}"

# Enhanced User Profile Model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    school = models.CharField(max_length=200, blank=True, null=True)
    grade_level = models.CharField(max_length=50, choices=[
        ('FORM_1', 'Form 1'),
        ('FORM_2', 'Form 2'),
        ('FORM_3', 'Form 3'),
        ('FORM_4', 'Form 4'),
        ('FORM_5', 'Form 5'),
        ('FORM_6', 'Form 6'),
    ], blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to=profile_picture_path,
        null=True, 
        blank=True,
        help_text="Upload profile picture (JPG, PNG)"
    )
    bio = models.TextField(max_length=500, blank=True)
    study_preferences = models.JSONField(default=dict, blank=True)
    notification_settings = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username

# Enhanced Subject Model
class Subject(models.Model):
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=10, unique=True, help_text="Subject code (e.g., MATH, ENG)")
    description = models.TextField(blank=True)
    grade_level = models.CharField(max_length=50, choices=[
        ('O_LEVEL', 'O Level'),
        ('A_LEVEL', 'A Level'),
        ('BOTH', 'Both Levels'),
    ], default='O_LEVEL')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_grade_level_display()})"
    
    def get_notes_count(self):
        return self.notes.count()
    
    def get_exam_papers_count(self):
        return self.exam_papers.count()

# Enhanced Notes Model
class Notes(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='notes')
    file_attachment = models.FileField(
        upload_to=notes_upload_path,
        null=True, 
        blank=True,
        help_text="Upload PDF, DOC, or image files"
    )
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    is_public = models.BooleanField(default=False, help_text="Make this note visible to other students")
    is_favorite = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Notes"
    
    def __str__(self):
        return self.title
    
    def get_file_extension(self):
        """Get file extension for display"""
        if self.file_attachment:
            return os.path.splitext(self.file_attachment.name)[1].lower()
        return None
    
    def is_pdf(self):
        """Check if file is PDF"""
        return self.get_file_extension() == '.pdf'
    
    def is_image(self):
        """Check if file is image"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        return self.get_file_extension() in image_extensions
    
    def get_tags_list(self):
        """Return tags as a list"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

# Enhanced Exam Paper Model
class ExamPaper(models.Model):
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exam_papers')
    year = models.IntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2030)])
    exam_type = models.CharField(max_length=50, choices=[
        ('O_LEVEL', 'O Level'),
        ('A_LEVEL', 'A Level'),
        ('MOCK', 'Mock Exam'),
        ('MID_TERM', 'Mid Term'),
        ('END_TERM', 'End Term'),
    ])
    paper_type = models.CharField(max_length=50, choices=[
        ('PAPER_1', 'Paper 1'),
        ('PAPER_2', 'Paper 2'),
        ('PAPER_3', 'Paper 3'),
        ('PAPER_4', 'Paper 4'),
        ('COMBINED', 'Combined Papers'),
    ], default='PAPER_1')
    file = models.FileField(
        upload_to=exam_papers_upload_path,
        help_text="Upload PDF exam papers only"
    )
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_exam_papers')
    download_count = models.IntegerField(default=0)
    is_approved = models.BooleanField(default=False, help_text="Admin approval required")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-year', '-created_at']
        unique_together = ['subject', 'year', 'exam_type', 'paper_type']
    
    def __str__(self):
        return f"{self.subject.name} - {self.year} ({self.get_exam_type_display()}) - {self.get_paper_type_display()}"
    
    def increment_download(self):
        """Track download count"""
        self.download_count += 1
        self.save(update_fields=['download_count'])

# Study Plan Model
class StudyPlan(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_plans')
    subjects = models.ManyToManyField(Subject, related_name='study_plans')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('PAUSED', 'Paused'),
        ('CANCELLED', 'Cancelled'),
    ], default='ACTIVE')
    priority = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ], default='MEDIUM')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def get_progress_percentage(self):
        """Calculate study plan progress"""
        total_days = (self.end_date - self.start_date).days
        days_elapsed = (timezone.now().date() - self.start_date).days
        if total_days > 0:
            return min(100, max(0, (days_elapsed / total_days) * 100))
        return 0

# Study Session Model
class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='study_sessions')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=0)
    topics_covered = models.TextField(blank=True)
    notes_used = models.ManyToManyField(Notes, blank=True, related_name='study_sessions')
    productivity_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True,
        help_text="Rate your productivity from 1-10"
    )
    notes = models.TextField(blank=True, help_text="Session notes and reflections")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.subject.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    def calculate_duration(self):
        """Calculate session duration in minutes"""
        if self.end_time:
            duration = self.end_time - self.start_time
            return int(duration.total_seconds() / 60)
        return 0
    
    def save(self, *args, **kwargs):
        if self.end_time:
            self.duration_minutes = self.calculate_duration()
        super().save(*args, **kwargs)

# Exam Date Model
class ExamDate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_dates')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exam_dates')
    exam_name = models.CharField(max_length=200)
    exam_date = models.DateTimeField()
    exam_type = models.CharField(max_length=50, choices=[
        ('O_LEVEL', 'O Level'),
        ('A_LEVEL', 'A Level'),
        ('MOCK', 'Mock Exam'),
        ('MID_TERM', 'Mid Term'),
        ('END_TERM', 'End Term'),
        ('QUIZ', 'Quiz'),
        ('ASSIGNMENT', 'Assignment'),
    ])
    priority = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ], default='MEDIUM')
    reminder_days = models.IntegerField(default=7, help_text="Days before exam to send reminder")
    is_reminder_sent = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['exam_date']
    
    def __str__(self):
        return f"{self.exam_name} - {self.subject.name} - {self.exam_date.strftime('%Y-%m-%d')}"
    
    def days_until_exam(self):
        """Calculate days until exam"""
        return (self.exam_date.date() - timezone.now().date()).days
    
    def should_send_reminder(self):
        """Check if reminder should be sent"""
        days_until = self.days_until_exam()
        return days_until <= self.reminder_days and not self.is_reminder_sent

# Study Goal Model
class StudyGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_goals')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='study_goals')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_date = models.DateField()
    goal_type = models.CharField(max_length=50, choices=[
        ('READ_CHAPTER', 'Read Chapter'),
        ('COMPLETE_ASSIGNMENT', 'Complete Assignment'),
        ('REVISE_TOPIC', 'Revise Topic'),
        ('PRACTICE_QUESTIONS', 'Practice Questions'),
        ('MEMORIZE_CONCEPTS', 'Memorize Concepts'),
        ('ACHIEVE_SCORE', 'Achieve Score'),
        ('STUDY_HOURS', 'Study Hours'),
    ])
    target_value = models.CharField(max_length=100, blank=True, help_text="Target value (e.g., 'Chapter 5', '80%', '2 hours')")
    current_progress = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    status = models.CharField(max_length=20, choices=[
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('OVERDUE', 'Overdue'),
    ], default='NOT_STARTED')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['target_date']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def is_overdue(self):
        """Check if goal is overdue"""
        return self.target_date < timezone.now().date() and self.status != 'COMPLETED'
    
    def update_progress(self, progress):
        """Update goal progress"""
        self.current_progress = min(100, max(0, progress))
        if self.current_progress >= 100:
            self.status = 'COMPLETED'
        elif self.current_progress > 0:
            self.status = 'IN_PROGRESS'
        self.save()

# Study Material Model
class StudyMaterial(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='study_materials')
    material_type = models.CharField(max_length=50, choices=[
        ('SUMMARY', 'Summary'),
        ('MIND_MAP', 'Mind Map'),
        ('FLASHCARDS', 'Flashcards'),
        ('FORMULA_SHEET', 'Formula Sheet'),
        ('VOCABULARY', 'Vocabulary'),
        ('TIMELINE', 'Timeline'),
        ('DIAGRAM', 'Diagram'),
        ('OTHER', 'Other'),
    ])
    file = models.FileField(
        upload_to=study_materials_path,
        null=True, 
        blank=True
    )
    content = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_materials')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_material_type_display()}"

# Notification Model
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=[
        ('EXAM_REMINDER', 'Exam Reminder'),
        ('STUDY_GOAL', 'Study Goal'),
        ('SYSTEM', 'System'),
        ('ACHIEVEMENT', 'Achievement'),
        ('REMINDER', 'Reminder'),
    ])
    is_read = models.BooleanField(default=False)
    related_object_type = models.CharField(max_length=50, blank=True, help_text="Type of related object (e.g., 'ExamDate', 'StudyGoal')")
    related_object_id = models.IntegerField(null=True, blank=True, help_text="ID of related object")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save(update_fields=['is_read'])

# Achievement Model
class Achievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=200)
    description = models.TextField()
    achievement_type = models.CharField(max_length=50, choices=[
        ('STUDY_STREAK', 'Study Streak'),
        ('GOAL_COMPLETION', 'Goal Completion'),
        ('EXAM_PREPARATION', 'Exam Preparation'),
        ('SUBJECT_MASTERY', 'Subject Mastery'),
        ('FIRST_NOTE', 'First Note'),
        ('FIRST_EXAM', 'First Exam'),
        ('PERFECT_SCORE', 'Perfect Score'),
    ])
    icon = models.CharField(max_length=100, blank=True, help_text="Icon class or emoji")
    points = models.IntegerField(default=0)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-unlocked_at']
        unique_together = ['user', 'achievement_type']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"

# User Statistics Model
class UserStatistics(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='statistics')
    total_study_hours = models.IntegerField(default=0)
    total_notes_created = models.IntegerField(default=0)
    total_goals_completed = models.IntegerField(default=0)
    current_streak_days = models.IntegerField(default=0)
    longest_streak_days = models.IntegerField(default=0)
    total_achievements = models.IntegerField(default=0)
    last_study_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Statistics"
    
    def update_study_hours(self, hours):
        """Update total study hours"""
        self.total_study_hours += hours
        self.save(update_fields=['total_study_hours'])
    
    def update_streak(self, study_date):
        """Update study streak"""
        if self.last_study_date:
            days_diff = (study_date - self.last_study_date).days
            if days_diff == 1:  # Consecutive day
                self.current_streak_days += 1
            elif days_diff > 1:  # Streak broken
                self.current_streak_days = 1
        else:
            self.current_streak_days = 1
        
        self.longest_streak_days = max(self.longest_streak_days, self.current_streak_days)
        self.last_study_date = study_date
        self.save()
    


