from django.contrib import admin
from django.utils.safestring import mark_safe

from web.models import (
    Blog,
    Contactmessage,
    Course,
    CourseCategory,
    CourseSection,
    CourseChapter,
    ChapterProgress,
    CourseChatMessage,
    CourseEnrollment,
    QuizAttempt,
    CourseAnnouncement,
    CourseAssignment,
    CourseCertificate,
)

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

@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name','order', 'is_section']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'title',
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


class CourseChapterInline(admin.TabularInline):
    model = CourseChapter
    extra = 1


@admin.register(CourseSection)
class CourseSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'created_at')
    list_filter = ('course',)
    inlines = [CourseChapterInline]


@admin.register(CourseChapter)
class CourseChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'duration', 'order')
    list_filter = ('section__course', 'section')


@admin.register(ChapterProgress)
class ChapterProgressAdmin(admin.ModelAdmin):
    list_display = ('chapter', 'user', 'session_key', 'is_completed', 'completed_at')
    list_filter = ('is_completed',)


@admin.register(CourseChatMessage)
class CourseChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'course', 'is_instructor', 'created_at')
    list_filter = ('course', 'is_instructor')


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('course', 'user', 'session_key', 'is_paid', 'amount_paid', 'payment_method', 'created_at')
    list_filter = ('is_paid', 'payment_method', 'course')
    search_fields = ('user__username', 'session_key', 'payment_id', 'course__title')


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('quiz_title', 'user', 'course', 'earned_marks', 'total_marks', 'result', 'attempted_at')
    list_filter = ('result', 'course', 'attempted_at')
    search_fields = ('quiz_title', 'user__username', 'user__email')


@admin.register(CourseAnnouncement)
class CourseAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'instructor', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'content')


@admin.register(CourseAssignment)
class CourseAssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'total_marks', 'total_submit', 'due_date', 'created_at')
    list_filter = ('course', 'due_date')
    search_fields = ('title', 'description')


@admin.register(CourseCertificate)
class CourseCertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'student', 'course', 'grade', 'issued_date')
    list_filter = ('course', 'issued_date')
    search_fields = ('certificate_id', 'student__username', 'student__email')
