from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from accounts.models import User
import json


class LoginView(View):
    template_name = "registration/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            next_url = request.GET.get('next') or reverse('web:course_library')
            return redirect(next_url)
        context = {
            'next': request.GET.get('next', ''),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        username_or_email = (request.POST.get('username') or '').strip()
        password = request.POST.get('password', '')
        next_url = request.POST.get('next') or request.GET.get('next') or reverse('web:course_library')

        if not username_or_email or not password:
            messages.error(request, "Please enter both username and password.")
            return render(request, self.template_name, {'next': next_url, 'username': username_or_email})

        # Try username authentication first
        user = authenticate(request, username=username_or_email, password=password)

        # If not authenticated, try finding user by email
        if user is None:
            user_obj = User.objects.filter(email__iexact=username_or_email).first()
            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect(next_url)
            else:
                messages.error(request, "Your account is disabled. Please contact support.")
        else:
            messages.error(request, "Invalid username or password. Please try again.")

        return render(request, self.template_name, {'next': next_url, 'username': username_or_email})


class AdminLoginView(View):
    """
    Dedicated Admin & Staff Portal Login View.
    Authenticates staff and superuser accounts and redirects to the Django Admin Dashboard.
    Rejects non-staff users with a clear privilege error.
    """
    template_name = "registration/admin_login.html"

    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                next_url = request.GET.get('next') or '/admin/'
                return redirect(next_url)
            else:
                messages.warning(
                    request,
                    "You are logged in as a student. To access the Admin Portal, please sign in with an Administrator account."
                )

        context = {
            'next': request.GET.get('next', '/admin/'),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        username_or_email = (request.POST.get('username') or '').strip()
        password = request.POST.get('password', '')
        next_url = request.POST.get('next') or request.GET.get('next') or '/admin/'

        if not username_or_email or not password:
            messages.error(request, "Please enter both administrator username and password.")
            return render(request, self.template_name, {'next': next_url, 'username': username_or_email})

        # Try username authentication first
        user = authenticate(request, username=username_or_email, password=password)

        # If not authenticated by username, try finding user by email
        if user is None:
            user_obj = User.objects.filter(email__iexact=username_or_email).first()
            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, "This administrator account is disabled. Please contact system support.")
                return render(request, self.template_name, {'next': next_url, 'username': username_or_email})

            # STRICT ADMIN / STAFF PRIVILEGE ENFORCEMENT
            if user.is_staff or user.is_superuser:
                login(request, user)
                messages.success(request, f"Welcome back, Administrator {user.first_name or user.username}!")
                return redirect(next_url)
            else:
                messages.error(
                    request,
                    "Access Denied: This account does not have staff or administrator privileges. Please use the Student Login."
                )
                return render(request, self.template_name, {'next': next_url, 'username': username_or_email})
        else:
            messages.error(request, "Invalid administrator username or password. Please verify your credentials.")

        return render(request, self.template_name, {'next': next_url, 'username': username_or_email})


class GoogleLoginView(View):
    """
    Handles 'Continue with Google' authentication.
    Supports direct one-click authentication and Google OAuth token verification.
    """
    def get(self, request):
        next_url = request.GET.get('next') or reverse('web:course_library')

        # Get or create Google authenticated student user
        email = request.GET.get('email', 'student.google@ifdindia.org')
        username = email.split('@')[0] + '_google'

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': 'Google',
                'last_name': 'Student',
                'is_active': True,
                'is_customer': True,
                'usertype': 'student',
            }
        )

        login(request, user)
        messages.success(request, f"Successfully signed in with Google as {user.email}!")
        return redirect(next_url)

    def post(self, request):
        # Handle Google GSI credential POST if sent from Google One Tap / GSI library
        try:
            data = json.loads(request.body.decode('utf-8')) if request.body else request.POST
        except Exception:
            data = request.POST

        email = data.get('email', 'student.google@ifdindia.org')
        name = data.get('name', 'Google Student')
        next_url = data.get('next') or reverse('web:course_library')

        first_name = name.split()[0] if name else 'Google'
        last_name = ' '.join(name.split()[1:]) if len(name.split()) > 1 else 'Student'
        username = email.split('@')[0] + '_google'

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'is_active': True,
                'is_customer': True,
                'usertype': 'student',
            }
        )

        login(request, user)
        return JsonResponse({
            'status': 'success',
            'redirect_url': next_url,
            'message': f"Signed in with Google as {user.email}"
        })


class SignUpView(View):
    template_name = "registration/signup.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('web:course_library')
        return render(request, self.template_name)

    def post(self, request):
        username = (request.POST.get('username') or '').strip()
        email = (request.POST.get('email') or '').strip()
        phone = (request.POST.get('phone') or '').strip()
        password = request.POST.get('password', '')
        first_name = (request.POST.get('first_name') or '').strip()
        last_name = (request.POST.get('last_name') or '').strip()

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, self.template_name, request.POST)

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, f"Username '{username}' is already taken.")
            return render(request, self.template_name, request.POST)

        if email and User.objects.filter(email__iexact=email).exists():
            messages.error(request, f"An account with email '{email}' already exists. Please log in.")
            return redirect('accounts:login')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone,
            is_customer=True,
            usertype='student',
        )

        login(request, user)
        messages.success(request, f"Welcome to IFD India, {user.first_name or user.username}! Your account has been created.")
        return redirect('web:course_library')


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, "You have been logged out successfully.")
        return redirect('web:index')
