from django.contrib import admin
from .models import Product, Review, Category, Subcategory, Brand, Banner, Available


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'fullname', 'user', 'product', 'rating', 'headline', 'approval', 'created_at')
    list_filter = ('rating', 'approval', 'created_at')
    search_fields = ('fullname', 'user__username', 'headline', 'content', 'product__title')
    list_editable = ('approval',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'product_type', 'is_popular', 'is_best_seller', 'created_at')
    list_filter = ('is_popular', 'is_best_seller', 'product_type')
    search_fields = ('title', 'details', 'description')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'active', 'created_at')
    list_filter = ('status', 'active')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'active')
    list_filter = ('active', 'category')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'content')
