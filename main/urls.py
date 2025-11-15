from django.urls import path
from . import views
from .views import login_view, register_view
from .views import download_pdf, create_checkout_session, has_paid
from .views import login_view, register_view
from .views import download_pdf, create_checkout_session, has_paid

urlpatterns = [

    path('', views.home, name='home'),

    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),

    path("map-form/<str:country_code>/<slug:form_slug>/", views.map_form, name="map_form"),

    # 🔥 ACTION ROUTES MUST COME BEFORE form_detail
    path('<str:country_code>/<str:form_slug>/store-pending-fields/', 
         views.store_pending_fields,
         name="store_pending_fields"),

    path('<str:country_code>/<str:form_slug>/save-fields/',
         views.save_fields,
         name="save_fields"),

    path('<str:country_code>/<str:form_slug>/fill/', views.fill_pdf, name='fill_pdf'),
    path('<str:country_code>/<str:form_slug>/download/', download_pdf, name='download_pdf'),
    path('<str:country_code>/<str:form_slug>/has-paid/', has_paid, name='has_paid'),
    path('<str:country_code>/<str:form_slug>/create-checkout-session/', create_checkout_session, name='create_checkout_session'),

    # 🔥 MUST BE LAST
    path('<str:country_code>/<str:form_slug>/', views.form_detail, name='form_detail'),

    path('<str:country_code>/', views.country, name='country'),
]
