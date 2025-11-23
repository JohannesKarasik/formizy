# main/admin.py
from django.contrib import admin
from .models import Country, Form
from .models import LandingPDF   # << ADD THIS

from django.db import models
from django.urls import reverse
from .models import Country   # make sure this import points to your Country model

admin.site.register(Country)


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ("title", "country", "slug")
    search_fields = ("title", "country__name")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {
            "fields": ("country", "title", "slug", "description", "pdf_file", "fields_schema"),
        }),
        ("SEO Meta", {
            "fields": ("seo_title", "seo_description"),
        }),
        ("SEO Page Content (Structured)", {
            "description": (
                "Provide your own content. "
                "Sections = list of {heading, body}. "
                "FAQs = list of {q, a}. "
                "CTAs = list of {label, url}."
            ),
            "fields": ("seo_h1", "seo_intro", "seo_sections", "seo_faqs", "seo_ctas"),
        }),
    )



class LandingPDF(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    description = models.TextField(blank=True)

    # NEW — so landing PDFs behave like normal forms
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="landing_pdfs",
        null=True,
        blank=True
    )

    pdf_file = models.FileField(upload_to="landing_pdfs/", blank=True, null=True)

    fields_schema = models.JSONField(default=list, blank=True)
    total_pages = models.IntegerField(default=1)

    def get_absolute_url(self):
        return reverse("landingpdf_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title
