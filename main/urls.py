from django.urls import path
from . import views
from .views import login_view, register_view
from .views import download_pdf, create_checkout_session, has_paid
from .views import login_view, register_view
from .views import download_pdf, create_checkout_session, has_paid
from django.contrib.sitemaps.views import sitemap
from .sitemaps import FormSitemap
from django.urls import path, re_path
from .views import (
    home,
    country,
    form_detail,
    map_form,
    landingpdf_detail,
)


urlpatterns = [
    path('', views.home, name='home'),

    # AUTH
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),

    # MAP
    re_path(
        r"^map-form/(?P<country_code>[a-zA-Z]{2})/(?P<form_slug>[-a-zA-Z0-9]+)/?$",
        views.map_form,
        name="map_form"
    ),

    # =============================
    # ACTION ROUTES — must be ABOVE country & form_detail
    # =============================
    path('<str:country_code>/<str:form_slug>/store-pending-fields/',
         views.store_pending_fields,
         name="store_pending_fields"),

     # LOCALIZED landing page PDFs


     path("<str:country_code>/lp-pdf/<slug:slug>/", landingpdf_detail, name="landingpdf_detail"),


    path('<str:country_code>/<str:form_slug>/save-fields/',
         views.save_fields,
         name="save_fields"),

    path('<str:country_code>/<str:form_slug>/fill/',
         views.fill_pdf, name='fill_pdf'),

    path('<str:country_code>/<str:form_slug>/download/',
         download_pdf, name='download_pdf'),

    path('<str:country_code>/<str:form_slug>/has-paid/',
         has_paid, name='has_paid'),

    path('<str:country_code>/<str:form_slug>/create-checkout-session/',
         create_checkout_session, name='create_checkout_session'),

    path("lang/<str:lang_code>/", views.switch_lang, name="switch_lang"),

    # =============================
    # COUNTRY ROUTE
    # =============================
    re_path(r'^(?P<country_code>[a-z]{2})/$', views.country, name='country'),

    # =============================
    # FORM DETAIL (must ALWAYS be last)
    # =============================
     re_path(
         r'^(?P<country_code>[a-z]{2})/(?P<form_slug>[-a-zA-Z0-9]+)/?$',
         views.form_detail,
         name='form_detail'
     ),

        path(
        "<str:country_code>/lp-pdf/<slug:slug>/create-checkout-session/",
        views.create_landing_pdf_checkout_session,
        name="create_landing_checkout",
    )

]

sitemaps = {
    'forms': FormSitemap,
}

urlpatterns += [
    path("sitemap.xml", sitemap, {'sitemaps': sitemaps}, name="sitemap"),
]
