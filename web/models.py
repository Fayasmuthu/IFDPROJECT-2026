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

    class Meta:
        verbose_name = _("Blogs")
        verbose_name_plural = _("Blogs")
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title