from django.db import models
from django.db import models
from django.contrib.auth.models import User



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


        # ✅ ADD THIS METHOD
    def get_absolute_url(self):
        return reverse(
            'form_detail',
            kwargs={
                'country_code': self.country.code,
                'form_slug': self.slug,
            }
        )

    def __str__(self):
        return self.title


class PaidForm(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    form_slug = models.CharField(max_length=200)

    # Existing field
    paid_at = models.DateTimeField(auto_now_add=True)

    # ✅ NEW — store user-entered fields before payment
    fields_json = models.JSONField(null=True, blank=True)

    # ✅ NEW — store the generated PDF after webhook
    filled_pdf = models.FileField(
        upload_to="filled_pdfs/",
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ("user", "form_slug")

    def __str__(self):
        return f"{self.user.username} - {self.form_slug}"
    

class GeneratedPDF(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    form_slug = models.CharField(max_length=200)
    pdf_file = models.FileField(upload_to="generated_pdfs/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.form_slug}"


