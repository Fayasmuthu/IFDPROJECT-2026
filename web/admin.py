from django.contrib import admin

from web.models import Blog, Contactmessage

# Register your models here.
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'created_at']
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Contactmessage)