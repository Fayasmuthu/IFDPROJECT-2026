from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = "web"

urlpatterns = [
    path("", views.indexView.as_view(), name="index"),
    path('About/', views.About, name='about'),
    # path("shop/", views.shopView.as_view(), name="shop"),
    # path('search/', views.search_view, name='search'),
    # path('order/<slug:product_slug>/whatsapp/', views.order_via_whatsapp, name='order_via_whatsapp'),
    # path('coming-soon/', views.coming_soon, name='coming_soon'),
   
    path('blogs/', views.BlogListView.as_view(), name='blog_list'),
    path('blogs/<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path("courses/",views.CourseView.as_view(),name="course_list"),
    path('course/course-detail/<slug:slug>/',views.CourseDetailView.as_view(),name="course_detail"),
    path('course/<slug:slug>/checkout/',views.CourseCheckoutView.as_view(),name='course_checkout'),
    path('course/<slug:slug>/payment/',views.PaymentView.as_view(),name='course_payment'),

]