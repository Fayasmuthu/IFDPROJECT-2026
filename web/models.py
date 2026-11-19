from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.text import slugify
from accounts.models import User
from django.urls import reverse_lazy
from tinymce.models import HTMLField
from django.utils import timezone


# Create your models here.
class Contactmessage(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()

    def __str__(self):
        return self.first_name 
    


class Blog(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=100,blank=True, null=True)
    image = models.ImageField(upload_to='blogs/',blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.CharField(max_length=100, default='Admin',blank=True, null=True)
    other1 = models.BooleanField(default=False)
    other2 = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _("Blogs")
        verbose_name_plural = _("Blogs")
        ordering = ['-order', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'course'
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class Language(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Skill(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CourseCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True)
    is_section = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Course Category")
        verbose_name_plural = _("Course Categories")
        ordering = ['order', 'id']

class Course(models.Model):
    category = models.ForeignKey(
        CourseCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='category_courses'
    )
    PRICE_TYPE = (
        ('free', 'Free'),
        ('paid', 'Paid'),
        ('pay', 'Pay'),
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    instructor = models.CharField(max_length=100)
    instructor_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='authored_courses'
    )
    image = models.ImageField(upload_to='courses/')
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    offer_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    price_type = models.CharField(
        max_length=10,
        choices=PRICE_TYPE,
        default='paid'
    )
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    all_section =models.BooleanField(default=True)
    course_one =models.BooleanField(default=False)
    course_two =models.BooleanField(default=False)
    course_three =models.BooleanField(default=False)
    course_four =models.BooleanField(default=False)
    course_five =models.BooleanField(default=False)
    course_six =models.BooleanField(default=False)
   
    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'course'
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    def related_products(self):
        return Course.objects.filter().exclude(pk=self.pk).distinct()[0:12]

    def get_absolute_url(self):
        return reverse_lazy("web:course_detail", kwargs={"slug": self.slug})

    def get_update_url(self):
        return reverse_lazy("main:course_update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse_lazy("main:course_delete", kwargs={"pk": self.pk})

    @property
    def get_image_url(self):
        if self.image:
            try:
                import os
                if os.path.exists(self.image.path):
                    return self.image.url
            except Exception:
                pass
        return "/static/assets/img/courses/course_thumb01.jpg"

    def is_unlocked_for(self, user=None, session_key=None):
        """Returns True if course is free or if user/guest has an active paid enrollment."""
        if self.price == 0 or self.price_type == 'free':
            return True
        if user and user.is_authenticated:
            if self.enrollments.filter(user=user, is_paid=True).exists():
                return True
        if session_key:
            if self.enrollments.filter(session_key=session_key, is_paid=True).exists():
                return True
        return False


class CourseSection(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections', null=True, blank=True)
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Course Section")
        verbose_name_plural = _("Course Sections")
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.course.title if self.course else 'Course'} - {self.title}"


class CourseChapter(models.Model):
    section = models.ForeignKey(CourseSection, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=255)
    video_url = models.CharField(max_length=500, blank=True, null=True, help_text="Video URL or MP4 source")
    duration = models.CharField(max_length=50, default="10:00", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Course Chapter")
        verbose_name_plural = _("Course Chapters")
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.section.title} - {self.title}"


class ChapterProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chapter_progress', null=True, blank=True)
    session_key = models.CharField(max_length=100, blank=True, null=True)
    chapter = models.ForeignKey(CourseChapter, on_delete=models.CASCADE, related_name='progresses')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Chapter Progress")
        verbose_name_plural = _("Chapter Progresses")

    def __str__(self):
        identifier = self.user.get_full_name() if self.user else (self.session_key or "Anonymous")
        status_text = "Completed" if self.is_completed else "Incomplete"
        return f"{identifier} - {self.chapter.title}: {status_text}"


class CourseChatMessage(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chat_messages', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_chat_messages', null=True, blank=True)
    user_name = models.CharField(max_length=100, default='Student')
    message = models.TextField()
    is_instructor = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Course Chat Message")
        verbose_name_plural = _("Course Chat Messages")
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user_name}: {self.message[:30]}"


class CourseEnrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_enrollments', null=True, blank=True)
    session_key = models.CharField(max_length=100, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    is_paid = models.BooleanField(default=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=50, default='Online (Simulated)', blank=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Course Enrollment")
        verbose_name_plural = _("Course Enrollments")
        ordering = ['-created_at']

    def __str__(self):
        who = self.user.get_full_name() or self.user.username if self.user else (self.session_key or 'Guest')
        return f"{who} - {self.course.title} (Paid: {self.is_paid})"


class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quiz_attempts', null=True, blank=True)
    quiz_title = models.CharField(max_length=255)
    total_questions = models.PositiveIntegerField(default=10)
    total_marks = models.PositiveIntegerField(default=100)
    correct_answers = models.PositiveIntegerField(default=8)
    earned_marks = models.PositiveIntegerField(default=80)
    result = models.CharField(
        max_length=20,
        choices=(('Passed', 'Passed'), ('Failed', 'Failed'), ('In Progress', 'In Progress')),
        default='Passed'
    )
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-attempted_at']
        verbose_name = _('Quiz Attempt')
        verbose_name_plural = _('Quiz Attempts')

    def __str__(self):
        return f"{self.user.username} - {self.quiz_title} ({self.result})"


class CourseAnnouncement(models.Model):
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='announcements', null=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Course Announcement')
        verbose_name_plural = _('Course Announcements')

    def __str__(self):
        return self.title


class CourseAssignment(models.Model):
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    total_marks = models.PositiveIntegerField(default=100)
    total_submit = models.PositiveIntegerField(default=0)
    due_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Course Assignment')
        verbose_name_plural = _('Course Assignments')

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class CourseCertificate(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    certificate_id = models.CharField(max_length=100, unique=True)
    issued_date = models.DateField(auto_now_add=True)
    grade = models.CharField(max_length=50, default='A (Distinction)')
    download_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-issued_date']
        verbose_name = _('Course Certificate')
        verbose_name_plural = _('Course Certificates')

    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.certificate_id})"




    