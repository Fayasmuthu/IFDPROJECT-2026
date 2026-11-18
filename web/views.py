import json
import uuid
from multiprocessing import context
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.db.models import Min, Max
from collections import defaultdict
from django.views import View
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
import urllib.parse
from web.models import (
    Blog,
    Contactmessage,
    Course,
    CourseCategory,
    Language,
    CourseSection,
    CourseChapter,
    ChapterProgress,
    CourseChatMessage,
    CourseEnrollment,
)
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


def get_or_create_default_islamic_course():
    """Ensure a default Islamic course with 3 sections & 41 chapters exists."""
    course, created = Course.objects.get_or_create(
        slug="course-islam",
        defaults={
            "title": "Islamic Studies & Values for the Deaf",
            "instructor": "Ustadh Farooq & IFD Faculty",
            "description": "Comprehensive Islamic studies designed specifically for Deaf individuals using Indian Sign Language (ISL), visual aids, and interactive assessments.",
            "price": 0,
            "price_type": "free",
            "course_three": True,
            "status": True,
            "image": "courses/1.jpg",
        }
    )

    if not course.sections.exists():
        curriculum_data = [
            {
                "title": "Islamic Foundations & Aqeedah (Faith)",
                "chapters": [
                    ("Introduction to Islamic Studies for the Deaf", "08:15", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("The Concept of Tawheed (Oneness of Allah) in Sign Language", "12:30", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("The Six Pillars of Iman Explained Visually", "14:20", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Belief in the Angels and Their Roles", "10:45", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("The Holy Books and Divine Revelations", "11:10", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Belief in All Prophets and Messengers", "13:50", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("The Day of Judgment: Understanding Akhirah", "15:05", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Divine Decree (Al-Qadr) and Acceptance", "09:40", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Aqeedah Review & Knowledge Check", "10:00", "https://www.w3schools.com/html/mov_bbb.mp4"),
                ],
            },
            {
                "title": "Prophetic Traditions & Daily Adhkar (Hadith & Duas)",
                "chapters": [
                    ("Importance of Sunnah & Hadith in Daily Life", "11:00", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Hadith 1: Actions are by Intentions (Niyyah)", "09:25", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Morning and Evening Supplications in Sign Language", "14:15", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Duas for Eating, Sleeping, and Travel", "10:30", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Kindness to Parents and Elders in Islam", "12:00", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Truthfulness, Honesty, and Good Character (Akhlaq)", "13:40", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Hadith Review & Practical Signs Assessment", "11:15", "https://www.w3schools.com/html/mov_bbb.mp4"),
                ],
            },
            {
                "title": "Practical Fiqh & Sign Language Quran Studies",
                "chapters": [
                    ("Taharah (Purification): Step-by-Step Wudu", "15:20", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Common Mistakes in Wudu & Solutions", "08:45", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("The Five Daily Prayers (Salah): Timings & Preparation", "12:10", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Step-by-Step Prayer Demonstration for the Deaf", "18:30", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Fajr and Dhuhr Prayers Step-by-Step", "14:00", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Asr, Maghrib, and Isha Prayers Step-by-Step", "16:20", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Congregational Prayer (Jama'ah) Guidelines for Deaf Muslims", "11:50", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Jumu'ah (Friday) Prayer and Khutbah in Sign Language", "13:15", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("The Fasting of Ramadan (Sawm): Rules & Wisdom", "15:00", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Zakat and Sadaqah: Purifying Your Wealth", "12:40", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Hajj and Umrah: Visual Step-by-Step Guide", "20:10", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Halal and Haram Food Guidelines", "10:15", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Surah Al-Fatiha: Translation and Signs (Part 1)", "12:00", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Surah Al-Fatiha: Translation and Signs (Part 2)", "11:30", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Surah Al-Ikhlas in Indian Sign Language", "09:45", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Surah Al-Falaq in Indian Sign Language", "10:20", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Surah An-Nas in Indian Sign Language", "10:10", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Surah Al-Kawthar in Indian Sign Language", "08:50", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Surah Al-Asr in Indian Sign Language", "09:15", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Islamic Etiquette in Social Gatherings", "11:40", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Rights of Neighbors and the Community", "12:30", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Patience (Sabr) and Gratitude (Shukr)", "13:10", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Repentance (Tawbah) and Forgiveness", "11:55", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Comprehensive Course Review & Sign Language Summary", "22:00", "https://www.w3schools.com/html/mov_bbb.mp4"),
                    ("Final Assessment & Certification Examination", "15:00", "https://www.w3schools.com/html/mov_bbb.mp4"),
                ],
            },
        ]

        for s_idx, sec_data in enumerate(curriculum_data, 1):
            sec = CourseSection.objects.create(
                course=course,
                title=sec_data["title"],
                order=s_idx,
            )
            for c_idx, ch_data in enumerate(sec_data["chapters"], 1):
                CourseChapter.objects.create(
                    section=sec,
                    title=ch_data[0],
                    duration=ch_data[1],
                    video_url=ch_data[2],
                    order=c_idx,
                )

    if not course.chat_messages.exists():
        CourseChatMessage.objects.create(
            course=course,
            user_name="Ustadh Farooq (Instructor)",
            message="Assalamu Alaikum wa Rahmatullah! Welcome to Course Islam. This course is specially created with Islamic Sign Language and visual lessons. You can ask any question here!",
            is_instructor=True,
        )
        CourseChatMessage.objects.create(
            course=course,
            user_name="Fatima Zahra (Student)",
            message="Alhamdulillah, the sign language videos for Salah (prayer) are very clear and helpful. Barakallahu feekum!",
            is_instructor=False,
        )
        CourseChatMessage.objects.create(
            course=course,
            user_name="Bilal Ahmed (Student)",
            message="Can we download the certificate once we complete all 41 chapters?",
            is_instructor=False,
        )
        CourseChatMessage.objects.create(
            course=course,
            user_name="Ustadh Farooq (Instructor)",
            message="Yes Bilal! Once your progress bar reaches 100%, the Certificate tab will unlock your verified completion certificate automatically.",
            is_instructor=True,
        )

    return course


class CourseIslamView(View):
    def get(self, request, slug='course-islam'):
        if not request.session.session_key:
            request.session.create()

        course = Course.objects.filter(slug=slug).first()
        if not course:
            course = get_or_create_default_islamic_course()
        else:
            if not course.sections.exists():
                get_or_create_default_islamic_course()

        # Check if course is unlocked: if locked and unpaid, redirect to course library payment
        if not course.is_unlocked_for(request.user, request.session.session_key):
            return redirect(f"{reverse('web:course_library')}?need_payment={course.slug}")

        # Track completed chapters
        if request.user.is_authenticated:
            # Transfer any guest session progress to authenticated user
            if request.session.session_key:
                guest_progs = ChapterProgress.objects.filter(
                    session_key=request.session.session_key,
                    user__isnull=True,
                )
                for gp in guest_progs:
                    up, created = ChapterProgress.objects.get_or_create(
                        user=request.user,
                        chapter=gp.chapter,
                        defaults={'is_completed': gp.is_completed},
                    )
                    if not created and gp.is_completed:
                        up.is_completed = True
                        up.save()
                    gp.delete()

            completed_chapter_ids = set(
                ChapterProgress.objects.filter(
                    user=request.user,
                    chapter__section__course=course,
                    is_completed=True,
                ).values_list('chapter_id', flat=True)
            )
        else:
            if not request.session.session_key:
                request.session.create()
            completed_chapter_ids = set(
                ChapterProgress.objects.filter(
                    session_key=request.session.session_key,
                    chapter__section__course=course,
                    is_completed=True,
                ).values_list('chapter_id', flat=True)
            )

        sections = course.sections.prefetch_related('chapters').all()
        total_chapters = 0
        total_completed = 0

        sections_data = []
        for sec in sections:
            ch_list = []
            sec_completed_count = 0
            for ch in sec.chapters.all():
                total_chapters += 1
                is_comp = ch.id in completed_chapter_ids
                if is_comp:
                    sec_completed_count += 1
                    total_completed += 1
                ch_list.append({
                    'id': ch.id,
                    'title': ch.title,
                    'duration': ch.duration,
                    'video_url': ch.video_url,
                    'is_completed': is_comp,
                    'order': ch.order,
                })

            is_sec_completed = (len(ch_list) > 0 and sec_completed_count == len(ch_list))
            sections_data.append({
                'id': sec.id,
                'title': sec.title,
                'order': sec.order,
                'chapters': ch_list,
                'chapter_count': len(ch_list),
                'completed_count': sec_completed_count,
                'is_completed': is_sec_completed,
            })

        progress_percent = int((total_completed / total_chapters) * 100) if total_chapters > 0 else 0
        all_completed = (total_completed == total_chapters and total_chapters > 0)

        # Chat messages
        chat_messages = course.chat_messages.all().order_by('created_at')

        # Student name for certificate
        if request.user.is_authenticated:
            student_name = request.user.get_full_name() or request.user.username
        else:
            student_name = "Deaf Learner"

        first_video = None
        if sections_data and sections_data[0]['chapters']:
            first_video = sections_data[0]['chapters'][0]

        context = {
            'course': course,
            'sections': sections_data,
            'total_sections': len(sections_data),
            'total_chapters': total_chapters,
            'total_completed': total_completed,
            'progress_percent': progress_percent,
            'all_completed': all_completed,
            'chat_messages': chat_messages,
            'student_name': student_name,
            'first_video': first_video,
        }
        return render(request, 'web/pages/Course_islam.html', context)


@csrf_exempt
def toggle_chapter_progress(request):
    if request.method != 'POST':
        return redirect('web:course_islam')

    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else request.POST
    except Exception:
        data = request.POST

    chapter_id = data.get('chapter_id')
    if not chapter_id:
        return JsonResponse({'status': 'error', 'message': 'Missing chapter_id'}, status=400)

    chapter = get_object_or_404(CourseChapter, id=chapter_id)
    course = chapter.section.course

    if request.user.is_authenticated:
        prog, _ = ChapterProgress.objects.get_or_create(
            user=request.user,
            chapter=chapter,
        )
    else:
        if not request.session.session_key:
            request.session.create()
        prog, _ = ChapterProgress.objects.get_or_create(
            session_key=request.session.session_key,
            chapter=chapter,
        )

    if 'completed' in data:
        prog.is_completed = bool(data.get('completed'))
    else:
        prog.is_completed = not prog.is_completed
    prog.save()

    # Recalculate
    if request.user.is_authenticated:
        completed_ids = set(
            ChapterProgress.objects.filter(
                user=request.user,
                chapter__section__course=course,
                is_completed=True,
            ).values_list('chapter_id', flat=True)
        )
    else:
        completed_ids = set(
            ChapterProgress.objects.filter(
                session_key=request.session.session_key,
                chapter__section__course=course,
                is_completed=True,
            ).values_list('chapter_id', flat=True)
        )

    total_chapters = CourseChapter.objects.filter(section__course=course).count()
    completed_chapters = len(completed_ids)
    progress_percent = int((completed_chapters / total_chapters) * 100) if total_chapters > 0 else 0
    all_completed = (completed_chapters == total_chapters and total_chapters > 0)

    sec_chapters = chapter.section.chapters.all()
    sec_total = sec_chapters.count()
    sec_completed = sum(1 for c in sec_chapters if c.id in completed_ids)
    sec_is_completed = (sec_total > 0 and sec_completed == sec_total)

    return JsonResponse({
        'status': 'success',
        'chapter_id': chapter.id,
        'is_completed': prog.is_completed,
        'completed_chapters': completed_chapters,
        'total_chapters': total_chapters,
        'progress_percent': progress_percent,
        'all_completed': all_completed,
        'section_id': chapter.section.id,
        'section_total': sec_total,
        'section_completed_count': sec_completed,
        'section_is_completed': sec_is_completed,
    })


@csrf_exempt
def send_course_chat(request):
    if request.method != 'POST':
        return redirect('web:course_islam')

    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else request.POST
    except Exception:
        data = request.POST

    course_id = data.get('course_id')
    message_text = data.get('message', '').strip()
    user_name = data.get('user_name', '').strip()

    if not message_text:
        return JsonResponse({'status': 'error', 'message': 'Message cannot be empty'}, status=400)

    course = None
    if course_id:
        course = Course.objects.filter(id=course_id).first()
    if not course:
        course = Course.objects.filter(slug='course-islam').first()
        if not course:
            course = get_or_create_default_islamic_course()

    user = request.user if request.user.is_authenticated else None
    if user:
        author_name = user_name or user.get_full_name() or user.username
        is_instructor = user.is_staff or user.is_superuser
    else:
        author_name = user_name or 'Deaf Learner'
        is_instructor = False

    message_text = message_text[:1000]
    author_name = author_name[:50]

    msg = CourseChatMessage.objects.create(
        course=course,
        user=user,
        user_name=author_name,
        message=message_text,
        is_instructor=is_instructor,
    )

    return JsonResponse({
        'status': 'success',
        'message': {
            'id': msg.id,
            'user_name': msg.user_name,
            'message': msg.message,
            'time': msg.created_at.strftime('%I:%M %p, %b %d'),
            'is_instructor': msg.is_instructor,
        },
    })


class CourseLibraryView(View):
    def get(self, request):
        if not request.session.session_key:
            request.session.create()

        category_slug = request.GET.get('category', 'all').strip()
        search_query = request.GET.get('q', '').strip()

        courses_qs = Course.objects.filter(status=True).select_related('category').prefetch_related('enrollments').order_by('id')

        if category_slug and category_slug != 'all':
            courses_qs = courses_qs.filter(category__slug=category_slug)

        if search_query:
            courses_qs = courses_qs.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(instructor__icontains=search_query)
            )

        categories = CourseCategory.objects.all().order_by('order', 'id')

        # Check unlocked/locked status for each course for current user/session
        courses_data = []
        for c in courses_qs:
            is_unlocked = c.is_unlocked_for(request.user, request.session.session_key)
            courses_data.append({
                'course': c,
                'is_unlocked': is_unlocked,
                'is_locked': not is_unlocked,
                'price_int': int(c.price),
                'target_url': reverse('web:course_islam') if c.slug == 'course-islam' else reverse('web:course_islam_detail', kwargs={'slug': c.slug}),
            })

        need_payment_slug = request.GET.get('need_payment', '').strip()
        pending_course = None
        if need_payment_slug:
            pending_course = Course.objects.filter(slug=need_payment_slug).first()

        context = {
            'courses': courses_data,
            'total_courses': len(courses_data),
            'categories': categories,
            'active_category': category_slug,
            'search_query': search_query,
            'pending_course': pending_course,
        }
        return render(request, 'web/pages/course_library.html', context)


@csrf_exempt
def enroll_and_unlock_course(request):
    """
    Simulates / processes payment and immediately unlocks the course for the user/session.
    Redirects to the course video player page upon success.
    """
    if request.method != 'POST':
        return redirect('web:course_library')

    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else request.POST
    except Exception:
        data = request.POST

    course_id = data.get('course_id')
    course_slug = data.get('course_slug')

    course = None
    if course_id:
        course = Course.objects.filter(id=course_id).first()
    elif course_slug:
        course = Course.objects.filter(slug=course_slug).first()

    if not course:
        return JsonResponse({'status': 'error', 'message': 'Course not found'}, status=404)

    if not request.session.session_key:
        request.session.create()

    # Save enrollment
    enrollment, created = CourseEnrollment.objects.get_or_create(
        user=request.user if request.user.is_authenticated else None,
        session_key=None if request.user.is_authenticated else request.session.session_key,
        course=course,
        defaults={
            'is_paid': True,
            'amount_paid': course.price,
            'payment_method': data.get('payment_method', 'Online Payment'),
            'payment_id': f"PAY_{uuid.uuid4().hex[:10].upper()}",
        }
    )
    if not created and not enrollment.is_paid:
        enrollment.is_paid = True
        enrollment.amount_paid = course.price
        enrollment.save()

    # Learning target URL
    if course.slug == 'course-islam':
        target_url = reverse('web:course_islam')
    else:
        target_url = reverse('web:course_islam_detail', kwargs={'slug': course.slug})

    return JsonResponse({
        'status': 'success',
        'message': f'Payment successful! You have unlocked {course.title}.',
        'course_id': course.id,
        'course_title': course.title,
        'target_url': target_url,
    })


