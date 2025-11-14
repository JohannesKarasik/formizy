from django.db import models



class Country(models.Model):
    code = models.CharField(max_length=5, unique=True)  # e.g. 'de', 'us', 'dk'
    name = models.CharField(max_length=100)
    language_code = models.CharField(max_length=5, default='en')

    def __str__(self):
        return self.name


class Form(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to='forms/', blank=True, null=True)

    fields_schema = models.JSONField(default=list, blank=True)

    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)

    seo_h1 = models.CharField(max_length=255, blank=True)
    seo_intro = models.TextField(blank=True)
    seo_sections = models.JSONField(default=list, blank=True)

    # FIXED ↓↓↓
    seo_faqs = models.JSONField(default=list, blank=True)

    seo_ctas = models.TextField(default="", blank=True)

    total_pages = models.IntegerField(default=1)

    def __str__(self):
        return self.title

