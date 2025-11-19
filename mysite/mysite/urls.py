# mysite/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main.views import stripe_webhook

# ➜ ADD THESE
from django.contrib.sitemaps.views import sitemap
from main.sitemaps import FormSitemap

sitemaps = {
    'forms': FormSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path("webhook/stripe/", stripe_webhook, name="stripe_webhook"),
    path('', include('main.urls')),

    # ➜ ADD THIS LINE
    path("sitemap.xml", sitemap, {'sitemaps': sitemaps}, name="sitemap"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
