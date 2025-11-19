from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.sitemaps.views import sitemap
from main.sitemaps import FormSitemap

sitemaps = {
    'forms': FormSitemap,
}

urlpatterns = [
    # Language switcher endpoint
    path('i18n/', include('django.conf.urls.i18n')),

    # Admin and webhooks must NOT be translated
    path('admin/', admin.site.urls),
    path("webhook/stripe/", include('main.urls')),
]

# IMPORTANT: use a custom prefix to avoid conflicts with your country codes.
urlpatterns += i18n_patterns(
    path('lang/', include('main.urls')),  # ← LANG CODE prefix
    prefix_default_language=False,
)

# Static files (development)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
