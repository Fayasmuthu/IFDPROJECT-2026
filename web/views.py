import json
from multiprocessing import context
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Min, Max
from collections import defaultdict
from django.views import View
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
import urllib.parse
from web.models import Blog, Contactmessage, Course, CourseCategory, Language
from web.forms import ContactForm
from orders.models import Wishlist
from orders.forms import WhatsAppOrderForm
from product.forms import ReviewForm
from product.models import Available, AvailableSize, Banner, Brand, Category,Product,Producttype,Subcategory
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import urllib
from orders.models import WhatsAppOrder
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

class indexView(TemplateView):
    template_name = "web/home/index.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["blogs"] = Blog.objects.filter(status=True).order_by('order', '-created_at')[:4]
        context["course_categories"] = CourseCategory.objects.filter(is_section=True).order_by('order')[:4]
        context["courses"] = Course.objects.filter(status=True).order_by('-created_at')[:10]

        for section in context["course_categories"]:
            if section.slug == "Duas":
                section.courses = Course.objects.filter(course_five=True)
            elif section.slug == "story_prophets":
                section.courses = Course.objects.filter(course_four=True)
            elif section.slug == "islamic_studies":
                section.courses = Course.objects.filter(course_three=True)
            elif section.slug == "history":
                section.courses = Course.objects.filter(course_two=True)
            elif section.slug == "arabic":
                section.courses = Course.objects.filter(course_one=True)
            elif section.slug == "all":
                section.courses = Course.objects.filter(all_section=True)
        # context["categories"] = Category.objects.filter(status='Published')
        # context["subcategories"] = Subcategory.objects.filter(active=True)
        # context["product_type"] = Producttype.objects.all()
        # products = Product.objects.filter(is_active=True)
        # context["brands"] = Brand.objects.all()
        # context["popular_products"] = products.filter(is_popular=True)
        # context["best_seller_products"] = products.filter(is_best_seller=True)
        wishlist_count = Wishlist.objects.filter(user=self.request.user.id).count()
        context["wishlist_count"] = wishlist_count
        # context["recent_products"] = products.order_by('-created_at')[:10]
        # context["recent_products"] = products.order_by('-id')[:10]
        if self.request.user.is_authenticated:
                context["wishlist_count"] = Wishlist.objects.filter(
                    user=self.request.user
                ).count()
        else:
            context["wishlist_count"] = 0
        return context
        
    # In your product detail view
    def product_detail(request, slug):
        product = get_object_or_404(Product, slug=slug)
        viewed = request.session.get('recently_viewed', [])
        if product.id not in viewed:
            viewed.insert(0, product.id)
            request.session['recently_viewed'] = viewed[:10]  # Keep only last 10
        return render(request, "product/detail.html", {"product": product})
  

    
class CourseView(ListView):
    model = Course
    template_name = "web/pages/all_courses.html"
    context_object_name = "courses"
    paginate_by = 3

    def get_queryset(self):
            courses = Course.objects.filter(status=True)
            sort_by = self.request.GET.get("sort_by")
            category = self.request.GET.get("category")
            language = self.request.GET.get("language")
            price_type = self.request.GET.get("price_type")
            category_title = None


            if category:
                courses = courses.filter(category__slug=category)

            if language:
                courses = courses.filter(language__id=language)

            # Price Filter
            if price_type == "free":
                courses = courses.filter(price=0)

            elif price_type == "paid":
                courses = courses.filter(price__gt=0)

            if sort_by:
                if sort_by == "low_to_high":
                    annotated_queryset = courses.annotate(
                        min_sale_price_size=Min("price"),
                    )
                    courses = annotated_queryset.order_by("min_sale_price_size")

                elif sort_by == "high_to_low":
                    annotated_queryset = courses.annotate(
                        max_sale_price_size=Max("price"),
                    )
                    courses = annotated_queryset.order_by("-max_sale_price_size")

                elif sort_by == "rating":
                    courses = courses.order_by("-rating")

                elif sort_by == "a_to_z":
                    courses = courses.order_by("title")

                elif sort_by == "z_to_a":
                    courses = courses.order_by("-title")

                elif sort_by == "latest":
                    courses = courses.order_by("-created_at")

                else:
                    courses = courses.order_by("-id")

            self.category_title = category_title if category_title else None

            return courses

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["languages"] = Language.objects.all()
        context["price_types"] = ["free", "paid"]
        context["title"] = self.category_title
        context["total_courses"] = self.get_queryset().count()

        return context


def coming_soon(request):
    context = {'is_contact': True} 
    return render(request, 'web/coming-soon.html', context)


class CourseDetailView(DetailView):
    model = Course
    template_name = "web/pages/course-details.html"
    context_object_name = "course"

    def get_queryset(self):
        return Course.objects.filter(status=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["related_courses"] = (
            Course.objects.filter(status=True)
            .exclude(pk=self.object.pk)
            .order_by("-created_at")[:3]
        )
        return context

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            product = self.get_object()
            user = request.user
            form = ReviewForm(request.POST, request.FILES)

            if form.is_valid():
                review = form.save(commit=False)
                review.product = product
                review.user = user
                review.save()

                response_data = {
                    "status": "true",
                    "title": "Successfully Submitted",
                    "message": "Message successfully Submitted",
                }
            else:
                print(form.errors)
                response_data = {
                    "status": "false",
                    "title": "Form validation error",
                    "message": str(form.errors),
                }
        else:
            response_data = {
                "status": "false",
                "title": "User not authenticated",
                "message": "User must be authenticated to submit a review.",
            }

        return JsonResponse(response_data)


# ✅ ADD THIS NEW VIEW FOR WHATSAPP ORDERS
@require_POST
def save_whatsapp_order(request):
    try:
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        variant_type = request.POST.get('variant_type')
        variant_id = request.POST.get('variant_id')

        # Validate required fields
        if not all([product_id, quantity, variant_type, variant_id]):
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required fields'
            }, status=400)

        # Get the product
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Product not found'
            }, status=404)

        # Save the order (adjust based on your model structure)
        # Example:
        whatsapp_order = WhatsAppOrder.objects.create(
            user=request.user if request.user.is_authenticated else None,
            product=product,
            quantity=quantity,
            variant_type=variant_type,
            variant_id=variant_id,
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Order saved successfully',
            'order_id': whatsapp_order.id
        })

    except Exception as e:
        print(f"Error saving WhatsApp order: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to save order'
        }, status=500)


def coming_soon(request):
    context = {'is_contact': True} 
    return render(request, 'web/coming-soon.html', context)


@csrf_exempt
def save_whatsapp_order(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        variant_type = request.POST.get('variant_type')
        variant_id = request.POST.get('variant_id')

        product = get_object_or_404(Product, id=product_id)
        variant_label = None

        if variant_type == 'size':
            size_obj = get_object_or_404(AvailableSize, id=variant_id)
            variant_label = f"{size_obj.weight}{size_obj.unit}"
        elif variant_type == 'available':
            available_obj = get_object_or_404(Available, id=variant_id)
            variant_label = f"Price AED {available_obj.sale_price}"

        WhatsAppOrder.objects.create(
            product=product,
            quantity=int(quantity),
            selected_size=variant_label
        )

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

@require_POST
@csrf_exempt
def update_order_status(request):
    order_id = request.POST.get('order_id')
    status = request.POST.get('status')
    order = get_object_or_404(WhatsAppOrder, id=order_id)
    order.status = status
    order.save()
    return JsonResponse({'success': True})

def search_view(request):
    query = request.GET.get('q', '').strip()
    categories = subcategories = producttypes = products = None

    if query:
        # Search Categories
        categories = Category.objects.filter(
            Q(title__icontains=query) | Q(slug__icontains=query)
        )

        # Search Subcategories
        subcategories = Subcategory.objects.filter(
            Q(title__icontains=query) | Q(slug__icontains=query)
        )

        # Search Product Types
        producttypes = Producttype.objects.filter(
            Q(title__icontains=query) | Q(slug__icontains=query)
        )

        # Search Products
        products = Product.objects.filter(
            Q(title__icontains=query) | Q(slug__icontains=query) | Q(brand__title__icontains=query)
        )

    context = {
        'query': query,
        'categories': categories,
        'subcategories': subcategories,
        'producttypes': producttypes,
        'products': products,
    }
    return render(request, 'web/search_results.html', context)


class BlogListView(ListView):
    model = Blog
    template_name = 'blog/blog_list.html'
    context_object_name = 'blogs'


class BlogDetailView(DetailView):
    model = Blog
    template_name = 'blog/blog_detail.html'
    context_object_name = 'blog'

class CourseCheckoutView(DetailView):
    model = Course
    template_name = 'web/course/checkout.html'
    context_object_name = 'course'


class PaymentView(DetailView):
    model = Course
    template_name = 'web/course/payment.html'
    context_object_name = 'course'

def About(request):
    context = {'is_contact': True} 
    return render(request, 'web/pages/about-us.html', context)
