# mysite/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Sitemap imports
from django.contrib.sitemaps.views import sitemap
from main.sitemaps import FormSitemap

# ➜ Required for Django i18n
from django.conf.urls.i18n import i18n_patterns

sitemaps = {
    'forms': FormSitemap,
}

urlpatterns = [
    # Language switcher endpoint (required)
    path('i18n/', include('django.conf.urls.i18n')),

    # Admin stays OUTSIDE language patterns
    path('admin/', admin.site.urls),

    # Stripe webhook also stays OUTSIDE
    path("webhook/stripe/", include('main.urls')),
]

# ➜ Wrap your main URLs in i18n_patterns
urlpatterns += i18n_patterns(
    path("", include("main.urls")),
    path("sitemap.xml", sitemap, {'sitemaps': sitemaps}, name="sitemap"),
)

# Static files (dev only)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
