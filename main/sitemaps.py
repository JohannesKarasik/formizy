from django.contrib.sitemaps import Sitemap
from .models import Form  # Your form model

class FormSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Form.objects.all()

    # lastmod removed because Form does not have updated_at
