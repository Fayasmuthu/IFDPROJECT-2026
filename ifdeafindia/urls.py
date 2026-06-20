from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView


urlpatterns = i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("web.urls", namespace="web")),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("", include("product.urls", namespace="product")),
    # path("", include("orders.urls", namespace="orders")),
    path("tinymce/", include("tinymce.urls")),
    path("translate/", include("rosetta.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("sitemap.xml", TemplateView.as_view(template_name="sitemap.xml", content_type="text/xml")),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('accounts/', include('registration.backends.simple.urls')),
    prefix_default_language=True,
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

