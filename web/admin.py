from django.contrib import admin
from django.utils.safestring import mark_safe

from web.models import Blog, Contactmessage, Course, CourseCategory

# Register your models here.
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title','order','category', 'author', 'created_at', 'image_preview']
    prepopulated_fields = {'slug': ('title',)}

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img loading="lazy" src="{obj.image.url}" style="width:50px;height:50px;object-fit:contain;">'
            )
        return None

    image_preview.short_description = "Image Preview"

admin.site.register(Contactmessage)

admin.site.register(CourseCategory)
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'instructor',
        'price',
        'status',
        'image_preview'
    )

    prepopulated_fields = {'slug': ('title',)}

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" width="60" height="60">'
            )
        return '-'

    image_preview.short_description = 'Image'