from django.urls import path
from . import views
from django.urls import path
from . import views
from django.urls import path
from . import views
from .views import login_view, register_view
from .views import download_pdf
from .views import create_checkout_session
from .views import has_paid




urlpatterns = [
    path('', views.home, name='home'),

    # 🔥 FIX: put auth BEFORE <str:country_code>
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),


    path('<str:country_code>/', views.country, name='country'),
    path('<str:country_code>/<str:form_slug>/', views.form_detail, name='form_detail'),
    path('<str:country_code>/<str:form_slug>/fill/', views.fill_pdf, name='fill_pdf'),

    path("map-form/<str:country_code>/<slug:form_slug>/", views.map_form, name="map_form"),
    path("<str:country_code>/<str:form_slug>/download/", download_pdf, name="download_pdf"),
    path("<str:country_code>/<str:form_slug>/has-paid/", has_paid, name="has_paid"),
    path("<str:country_code>/<str:form_slug>/create-checkout-session/", create_checkout_session, name="create_checkout_session"),



]
