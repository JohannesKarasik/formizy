from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.sitemaps.views import sitemap
from main.sitemaps import FormSitemap
from main.views import stripe_webhook


sitemaps = {
    'forms': FormSitemap,
}

urlpatterns = [

    # Language switch endpoint (required)
    path('i18n/', include('django.conf.urls.i18n')),

    # Admin & webhook outside translations
    path('admin/', admin.site.urls),
    path("webhook/stripe/", stripe_webhook, name="stripe_webhook"),

    # MAIN ROUTES WITHOUT LANG PREFIX
    # <-- This keeps: /  /de  /es /dk  etc. working
    path('', include('main.urls')),
]

# TRANSLATED VERSION OF ROUTES UNDER /lang/
# This does NOT replace your existing routes
urlpatterns += i18n_patterns(
    path('lang/', include('main.urls')),
    prefix_default_language=False,
)

# Static (dev mode)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
