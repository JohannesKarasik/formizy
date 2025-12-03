from django.urls import path, re_path
from . import views
from .views import (
    login_view, register_view, logout_view,
    home, country,
    form_landing, form_editor,
    map_form,
    landingpdf_detail, create_landing_pdf_checkout_session,
    fill_pdf, save_fields, download_pdf,
    create_checkout_session, has_paid,
    store_pending_fields
)

urlpatterns = [

    # HOME
    path('', home, name='home'),

    # AUTH
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),

    # MAP-FORM (PDF mapping tool)
    re_path(
        r"^map-form/(?P<country_code>[a-zA-Z]{2})/(?P<form_slug>[-a-zA-Z0-9]+)/?$",
        map_form,
        name="map_form"
    ),

    # ============================
    # LP-PDF SPECIAL LANDING VIEWER
    # ============================

    path("<str:country_code>/lp-pdf/<slug:slug>/", landingpdf_detail, name="landingpdf_detail"),

    path("<str:country_code>/lp-pdf/<slug:slug>/create-checkout-session/",
         create_landing_pdf_checkout_session,
         name="create_landing_checkout"),

    # ============================
    # ACTION ROUTES (must be above form_landing)
    # ============================

    path("<str:country_code>/<str:form_slug>/store-pending-fields/",
         store_pending_fields, name="store_pending_fields"),

    path("<str:country_code>/<str:form_slug>/save-fields/",
         save_fields, name="save_fields"),

    path("<str:country_code>/<str:form_slug>/fill/",
         fill_pdf, name="fill_pdf"),

    path("<str:country_code>/<str:form_slug>/download/",
         download_pdf, name="download_pdf"),

    path("<str:country_code>/<str:form_slug>/has-paid/",
         has_paid, name="has_paid"),

    path("<str:country_code>/<str:form_slug>/create-checkout-session/",
         create_checkout_session, name="create_checkout_session"),

    # LANGUAGE SWITCHER
    path("lang/<str:lang_code>/", views.switch_lang, name="switch_lang"),

    # ============================
    # NEW FORM ROUTES
    # ============================

    # Landing page (clean SEO-friendly)
# ============================
# NEW FORM ROUTES
# ============================

# Main page (SEO + PDF editor) at /<country>/<slug>/
     path("<str:country_code>/<slug:form_slug>/",
          form_editor, name="form_editor"),

     # Optional: secondary URL /<country>/<slug>/editor/ pointing to same view
     path("<str:country_code>/<slug:form_slug>/editor/",
          form_editor, name="form_editor_alias"),


    # ============================
    # COUNTRY ROUTE
    # ============================
    re_path(r"^(?P<country_code>[a-z]{2})/$",
            country, name='country'),
]

# SITEMAP
from django.contrib.sitemaps.views import sitemap
from .sitemaps import FormSitemap

urlpatterns += [
    path("sitemap.xml", sitemap, {'sitemaps': {'forms': FormSitemap}}, name="sitemap"),
]
