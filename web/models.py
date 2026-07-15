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
            self.slug = slugify(self.title)
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
    slug =models.SlugField()
    is_section =models.BooleanField()
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = _("Course Category")
        verbose_name_plural = _("Course Categories")
        ordering = ['-order']

class Course(models.Model):
    # category = models.ForeignKey(
    #     CourseCategory,
    #     on_delete=models.CASCADE,
    #     related_name='courses'
    # )
    PRICE_TYPE = (
        ('free', 'Free'),
        ('paid', 'Paid'),
        ('pay', 'Pay'),
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    instructor = models.CharField(max_length=100)
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
            self.slug = slugify(self.title)
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
    