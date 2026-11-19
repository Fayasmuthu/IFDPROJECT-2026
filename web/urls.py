from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = "web"

urlpatterns = [
    path("", views.indexView.as_view(), name="index"),
    path('About/', views.About, name='about'),
    
    # Books & Shop Catalog
    path('books/', views.BookListView.as_view(), name='book_list'),
    path('books/<slug:slug>/', views.BookDetailView.as_view(), name='book_detail'),
    path('book/', views.BookListView.as_view(), name='book'),
    path('shop/', views.BookListView.as_view(), name='shop'),
    path('shop/<slug:slug>/', views.BookDetailView.as_view(), name='product_detail'),
   
    path('blogs/', views.BlogListView.as_view(), name='blog_list'),
    path('blogs/<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path("courses/",views.CourseView.as_view(),name="course_list"),
    path('course/course-detail/<slug:slug>/',views.CourseDetailView.as_view(),name="course_detail"),
    path('course/<slug:slug>/checkout/',views.CourseCheckoutView.as_view(),name='course_checkout'),
    path('course/<slug:slug>/payment/',views.PaymentView.as_view(),name='course_payment'),
    path('login/', views.login_redirect, name='login'),
    path('admin-login/', views.admin_login_redirect, name='admin_login'),

    # Course Islam & Library
    path('course-library/', views.CourseLibraryView.as_view(), name='course_library'),
    path('course-library/pay-unlock/', views.enroll_and_unlock_course, name='course_pay_unlock'),
    path('course-islam/', views.CourseIslamView.as_view(), name='course_islam'),
    path('course-islam/toggle-progress/', views.toggle_chapter_progress, name='toggle_chapter_progress'),
    path('course-islam/send-chat/', views.send_course_chat, name='send_course_chat'),
    path('course-islam/<slug:slug>/', views.CourseIslamView.as_view(), name='course_islam_detail'),

    # Student Dashboard & Features
    path('dashboard/', views.StudentDashboardView.as_view(), name='student_dashboard'),
    path('dashboard/<str:tab>/', views.StudentDashboardView.as_view(), name='student_dashboard_tab'),
    path('student-dashboard/', views.dashboard_redirect, name='student_dashboard_legacy'),
    path('student-profile/', views.dashboard_redirect, {'tab': 'profile'}),
    path('student-enrolled-courses/', views.dashboard_redirect, {'tab': 'courses'}),
    path('student-wishlist/', views.dashboard_redirect, {'tab': 'wishlist'}),
    path('student-review/', views.dashboard_redirect, {'tab': 'reviews'}),
    path('student-attempts/', views.dashboard_redirect, {'tab': 'quiz'}),
    path('student-history/', views.dashboard_redirect, {'tab': 'orders'}),
    path('student-setting/', views.dashboard_redirect, {'tab': 'settings'}),

    # Instructor Dashboard & Features
    path('instructor-dashboard/', views.InstructorDashboardView.as_view(), name='instructor_dashboard'),
    path('instructor-dashboard/<str:tab>/', views.InstructorDashboardView.as_view(), name='instructor_dashboard_tab'),
    path('instructor-courses/', views.instructor_redirect, {'tab': 'courses'}, name='instructor_courses'),
    path('instructor-announcement/', views.instructor_redirect, {'tab': 'announcements'}, name='instructor_announcement'),
    path('instructor-quiz/', views.instructor_redirect, {'tab': 'quiz_attempts'}, name='instructor_quiz'),
    path('instructor-assignment/', views.instructor_redirect, {'tab': 'assignments'}, name='instructor_assignment'),
    path('instructor-setting/', views.instructor_redirect, {'tab': 'settings'}, name='instructor_setting'),
    path('instructor-review/', views.instructor_redirect, {'tab': 'reviews'}, name='instructor_review'),
    path('instructor-history/', views.instructor_redirect, {'tab': 'orders'}, name='instructor_history'),
    path('instructor-profile/', views.instructor_redirect, {'tab': 'profile'}, name='instructor_profile'),
    path('instructor-attempts/', views.instructor_redirect, {'tab': 'my_quiz_attempts'}, name='instructor_attempts'),
    path('instructor-wishlist/', views.instructor_redirect, {'tab': 'wishlist'}, name='instructor_wishlist'),
    path('instructor-enrolled-courses/', views.instructor_redirect, {'tab': 'enrolled_courses'}, name='instructor_enrolled_courses'),
    path('instructor-certificates/', views.instructor_redirect, {'tab': 'certificates'}, name='instructor_certificates'),
    path('instructor-students/', views.instructor_redirect, {'tab': 'students'}, name='instructor_students'),
    path('instructor-insights/', views.instructor_redirect, {'tab': 'insights'}, name='instructor_insights'),
    path('instructor-chat/', views.instructor_redirect, {'tab': 'chat'}, name='instructor_chat'),
    path('instructor-payments/', views.instructor_redirect, {'tab': 'payments'}, name='instructor_payments'),
]