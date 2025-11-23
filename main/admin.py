# main/admin.py
from django.contrib import admin
from .models import Country, Form
from .models import LandingPDF   # << ADD THIS

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




@admin.register(LandingPDF)
class LandingPDFAdmin(admin.ModelAdmin):
    list_display = ("title", "slug")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    fields = (
        "title",
        "slug",
        "description",
        "pdf_file",
        "fields_schema",
        "total_pages",
    )
