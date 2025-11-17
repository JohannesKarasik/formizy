from django.contrib.sitemaps import Sitemap
from .models import Form  # or whatever model you want indexed

class FormSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Form.objects.all()

    def lastmod(self, obj):
        return obj.updated_at  # optional if you track updates
