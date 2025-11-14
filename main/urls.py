from django.urls import path
from . import views
from django.urls import path
from . import views
from django.urls import path
from . import views
from .views import login_view, register_view

urlpatterns = [
    path('', views.home, name='home'),

    # 🔥 FIX: put auth BEFORE <str:country_code>
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),


    path('<str:country_code>/', views.country, name='country'),
    path('<str:country_code>/<str:form_slug>/', views.form_detail, name='form_detail'),
    path('<str:country_code>/<str:form_slug>/fill/', views.fill_pdf, name='fill_pdf'),

    path("map-form/<str:country_code>/<slug:form_slug>/", views.map_form, name="map_form"),

]
