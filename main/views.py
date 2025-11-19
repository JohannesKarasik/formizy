from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.conf import settings
import stripe
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import logout
from .models import Form, Country



import json, io, os
import fitz  # PyMuPDF


from .models import Form



from django.views.decorators.http import require_POST
import json

from django.http import JsonResponse


def get_ui_language(request):
    code = request.COOKIES.get("site_lang", "en")
    return LANGUAGE_TEXT.get(code, LANGUAGE_TEXT["en"])


def switch_lang(request, lang_code):
    # only allow the languages you have in LANGUAGE_TEXT
    if lang_code not in LANGUAGE_TEXT:
        lang_code = "en"

    response = redirect(request.META.get("HTTP_REFERER", "/"))
    response.set_cookie("site_lang", lang_code, max_age=60*60*24*365)  # 1 year

    return response


LANGUAGE_TEXT = {
    "en": {
        "login_title": "Login",
        "register_title": "Create Account",
        "email": "Email",
        "password": "Password",
        "password_create": "Create Password",
        "login_btn": "Login",
        "register_btn": "Create Account",
        "no_account": "Don't have an account?",
        "yes_account": "Already have an account?",
        "switch_login": "Login",
        "switch_register": "Create Account",
        "login_failed": "Login failed. Check email or password.",
        "register_failed": "Registration failed",
        "server_error": "Server error: Unexpected response.",
        "other_forms": "Other important forms",
        "footer_tagline": "Build, share, and automate forms in minutes.",
        "nav_home": "Home",
        "nav_about": "About us",
        "nav_contact": "Contact",
        "nav_blog": "Blog",
        "legal_privacy": "Privacy",
        "legal_terms": "Terms",
        "legal_cookies": "Cookies",
        "legal_rights": "All rights reserved."

    },

    "de": {
        "login_title": "Einloggen",
        "register_title": "Konto erstellen",
        "email": "E-Mail",
        "password": "Passwort",
        "password_create": "Passwort erstellen",
        "login_btn": "Einloggen",
        "register_btn": "Konto erstellen",
        "no_account": "Noch kein Konto?",
        "yes_account": "Schon ein Konto?",
        "switch_login": "Einloggen",
        "switch_register": "Konto erstellen",
        "login_failed": "Login fehlgeschlagen. Bitte E-Mail oder Passwort prüfen.",
        "register_failed": "Registrierung fehlgeschlagen",
        "server_error": "Serverfehler: Unerwartete Antwort vom Server.",
        "other_forms": "Weitere wichtige Formulare",
        "footer_tagline": "Erstellen, teilen und automatisieren Sie Formulare in wenigen Minuten.",
        "nav_home": "Startseite",
        "nav_about": "Über uns",
        "nav_contact": "Kontakt",
        "nav_blog": "Blog",
        "legal_privacy": "Datenschutz",
        "legal_terms": "Nutzungsbedingungen",
        "legal_cookies": "Cookies",
        "legal_rights": "Alle Rechte vorbehalten."

    },

    "es": {
        "login_title": "Iniciar sesión",
        "register_title": "Crear cuenta",
        "email": "Correo electrónico",
        "password": "Contraseña",
        "password_create": "Crear contraseña",
        "login_btn": "Iniciar sesión",
        "register_btn": "Crear cuenta",
        "no_account": "¿Aún no tienes cuenta?",
        "yes_account": "¿Ya tienes una cuenta?",
        "switch_login": "Iniciar sesión",
        "switch_register": "Crear cuenta",
        "login_failed": "Error al iniciar sesión. Verifica correo o contraseña.",
        "register_failed": "Error en el registro",
        "server_error": "Error del servidor: respuesta inesperada.",
        "other_forms": "Otros formularios importantes",
        "footer_tagline": "Crear, compartir y automatizar formularios en minutos.",
        "nav_home": "Inicio",
        "nav_about": "Sobre nosotros",
        "nav_contact": "Contacto",
        "nav_blog": "Blog",
        "legal_privacy": "Privacidad",
        "legal_terms": "Términos",
        "legal_cookies": "Cookies",
        "legal_rights": "Todos los derechos reservados."

    },


    "it": {
        "other_forms": "Altri moduli importanti",
        "footer_tagline": "Creare, condividere e automatizzare moduli in pochi minuti.",
        "nav_home": "Home",
        "nav_about": "Chi siamo",
        "nav_contact": "Contatti",
        "nav_blog": "Blog",
        "legal_privacy": "Privacy",
        "legal_terms": "Termini",
        "legal_cookies": "Cookie",
        "legal_rights": "Tutti i diritti riservati."

    }



}



def store_pending_fields(request, country, slug):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)
    request.session["pending_fields"] = data.get("fields_data", {})

    return JsonResponse({"ok": True})



def home(request):
    countries = Country.objects.all().order_by("name")

    return render(request, "main/home.html", {
        "countries": countries,
        "lang": get_ui_language(request)
    })




def country(request, country_code):
    # Get matching country object
    country_obj = get_object_or_404(Country, code=country_code)

    # Get all forms assigned to this country
    forms = Form.objects.filter(country=country_obj)

    # Load language (fallback to EN)
    lang = get_ui_language(request)

    return render(request, "main/country.html", {
        "country_code": country_code,
        "country_name": country_obj.name,
        "forms": forms,
        "lang": get_ui_language(request)
    })





# ===========================
# FORM DETAIL (PDF viewer)
# ===========================

from .models import Form

def form_detail(request, country_code, form_slug):
    form_info = get_object_or_404(Form, country__code=country_code, slug=form_slug)

    # Fetch other forms from the same country, excluding the current one
    related_forms = Form.objects.filter(
        country__code=country_code
    ).exclude(slug=form_slug)

    # Existing logic...
    import time
    pdf_url = f"{form_info.pdf_file.url}?v={int(time.time())}"
    pdf_path = form_info.pdf_file.path
    doc = fitz.open(pdf_path)
    width = doc[0].rect.width
    doc.close()
    viewer_scale = 833 / width

    lang = get_ui_language(request)

    return render(request, "main/pdf_clean_viewer.html", {
        "form_info": form_info,
        "pdf_url": pdf_url,
        "country_code": country_code,
        "viewer_scale": viewer_scale,
        "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
        "lang": get_ui_language(request),
        "related_forms": related_forms,
    })





from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.conf import settings


import json, io, os
import fitz  # PyMuPDF


from .models import Form


# ... other views above ...



from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.conf import settings

import json, io, os
import fitz  # PyMuPDF

from .models import Form


@login_required
def fill_pdf(request, country_code, form_slug):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    form_info = get_object_or_404(Form, country__code=country_code, slug=form_slug)

    # Parse JSON from frontend
    try:
        body = json.loads(request.body.decode("utf-8"))
        fields_data = body.get("fields_data", {})
    except Exception as e:
        return JsonResponse({"error": f"Invalid JSON: {e}"}, status=400)

    if not form_info.fields_schema:
        return JsonResponse({"error": "No field schema defined"}, status=400)

    # ---------------------------------------------------
    # ❗ NEVER OPEN THE ORIGINAL PDF DIRECTLY FOR WRITING
    # Instead: create an in-memory clone
    # ---------------------------------------------------
    original_pdf_bytes = open(form_info.pdf_file.path, "rb").read()
    doc = fitz.open("pdf", original_pdf_bytes)

    # Load font only INSIDE the new PDF
    font_path = os.path.join(settings.BASE_DIR, "main", "fonts", "Arial Unicode.ttf")
    FONT_NAME = "ArialUnicode"
    FONT_SIZE = 10

    OFFSET_X = 0
    OFFSET_Y = 8
    CHECKMARK = "\u2713"

    for field in form_info.fields_schema:

        value = fields_data.get(field.get("name"), "")
        if value is None:
            value = ""

        # skip empty normal text fields
        if field.get("type") != "checkbox" and value == "":
            continue

        try:
            page_index = int(field.get("page", 1)) - 1
        except:
            page_index = 0

        if not (0 <= page_index < len(doc)):
            continue

        page = doc[page_index]

        page.insert_font(fontfile=font_path, fontname=FONT_NAME)

        px = float(field.get("pixel_x", 0))
        py = float(field.get("pixel_y", 0))
        x = px + OFFSET_X
        y = py + OFFSET_Y

        # Checkbox
        if field.get("type") == "checkbox":
            if str(value) == "1":
                page.insert_text(
                    (x, y),
                    CHECKMARK,
                    fontsize=14,
                    fontname=FONT_NAME,
                    color=(0, 0, 0),
                    overlay=True,
                )
            continue

        # Text field
        page.insert_text(
            (x, y),
            str(value),
            fontsize=FONT_SIZE,
            fontname=FONT_NAME,
            color=(0, 0, 0),
            overlay=True,
        )

    # ---------------------------------------------------
    # ✔ ALWAYS SAVE TO MEMORY — NEVER SAVE TO DISK
    # ---------------------------------------------------
    output = io.BytesIO()
    doc.save(output, incremental=False)   # important fix
    output.seek(0)
    doc.close()

    return FileResponse(
        output,
        filename=f"{form_info.slug}_filled.pdf",
        as_attachment=True,
        content_type="application/pdf"
    )



def map_form(request, country_code, form_slug):


   form_info = get_object_or_404(Form, country__code=country_code, slug=form_slug)


   if request.method == "POST":
       try:
           fields_json = json.loads(request.body.decode("utf-8"))
       except:
           return JsonResponse({"status": "error", "message": "invalid JSON"})


       form_info.fields_schema = fields_json
       form_info.save()


       return JsonResponse({"status": "ok", "count": len(fields_json)})


   pdf_url = form_info.pdf_file.url


   return render(request, "main/form_mapper.html", {
       "form_info": form_info,
       "pdf_url": pdf_url,
       "country_code": country_code,
   })




# ===========================
# AUTH
# ===========================

from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login

def register_view(request):
    if request.method != "POST":
        print("❌ register_view hit with GET")
        return JsonResponse({"error": "method not allowed"}, status=405)

    print("🟦 REGISTER VIEW HIT — POST DATA:", dict(request.POST))
    print("🟦 USER-AGENT:", request.META.get("HTTP_USER_AGENT"))
    print("🟦 COOKIES RECEIVED:", request.COOKIES)
    print("🟦 SESSION KEY:", request.session.session_key)
    print("🟦 SESSION BEFORE ANYTHING:", dict(request.session.items()))

    email = request.POST.get("email")
    password = request.POST.get("password")
    next_url = request.POST.get("next", "/")

    print("🟦 email:", email)
    print("🟦 password length:", len(password) if password else 0)
    print("🟦 next_url:", next_url)

    if not email or not password:
        print("❌ missing email or password")
        return JsonResponse({"error": "missing fields"}, status=400)

    if User.objects.filter(username=email).exists():
        print("❌ user already exists:", email)
        return JsonResponse({"error": "exists"}, status=400)

    try:
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )
        login(request, user)
        print("✅ REGISTER SUCCESS — user id:", user.id)

        # ---------------------------------------------------
        #  RESTORE PENDING FIELD DATA AFTER REGISTRATION
        # ---------------------------------------------------
        pending = request.session.get("pending_fields")
        form_slug = request.session.get("pending_form_slug")

        print("🟨 SESSION AT RESTORE — pending_fields:", pending)
        print("🟨 SESSION AT RESTORE — pending_form_slug:", form_slug)

        if pending and form_slug:
            try:
                from .models import PaidForm

                print("🟩 Attempting to parse pending_fields JSON…")
                fields_json = json.loads(pending)
                print("🟩 Parsed fields_json:", fields_json)

                paid_obj, created = PaidForm.objects.get_or_create(
                    user=user,
                    form_slug=form_slug
                )

                print(f"🟩 PaidForm object → created={created}, obj={paid_obj}")

                paid_obj.fields_json = fields_json
                paid_obj.save()

                print("✅ Fields restored into PaidForm!")

                # Clean session
                del request.session["pending_fields"]
                del request.session["pending_form_slug"]
                request.session.modified = True
                print("🟦 Cleared pending session fields")

            except Exception as e:
                print("🟥 Restore fields error (register):", e)
        else:
            print("⚠ No pending fields found in session")

        print("🟦 SESSION AFTER RESTORE:", dict(request.session.items()))

    except Exception as e:
        print("🟥 REGISTER EXCEPTION:", e)
        return JsonResponse({"error": str(e)}, status=400)

    print("✅ Registration completed — redirecting to:", next_url)
    return JsonResponse({"success": True, "next": next_url})


from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_POST
from django.shortcuts import redirect, render
def login_view(request):
    next_url = request.GET.get("next", "/")
    print("LOGIN VIEW — METHOD:", request.method)

    if request.method == "POST":
        print("LOGIN HIT — POST DATA:", request.POST)

        email = request.POST.get("email")
        password = request.POST.get("password")
        next_url = request.POST.get("next", "/")

        print("LOGIN email:", email)
        print("LOGIN password length:", len(password) if password else "NO PASSWORD")

        user = authenticate(request, username=email, password=password)
        print("AUTH RESULT:", user)

        if user:
            login(request, user)
            print("LOGIN SUCCESS — user id:", user.id)

            # -------------------------------
            # RESTORE PENDING FIELDS FROM SESSION
            # -------------------------------
            pending = request.session.get("pending_fields")
            form_slug = request.session.get("pending_form_slug")

            if pending and form_slug:
                try:
                    from .models import PaidForm
                    fields_json = json.loads(pending)

                    paid_obj, _ = PaidForm.objects.get_or_create(
                        user=user,
                        form_slug=form_slug
                    )
                    paid_obj.fields_json = fields_json
                    paid_obj.save()

                    print("Restored fields into PaidForm!")
                except Exception as e:
                    print("Restore fields error:", e)

                # Clean up
                del request.session["pending_fields"]
                del request.session["pending_form_slug"]

            return redirect(next_url)

        print("LOGIN FAILED — wrong credentials")
        return render(request, "auth/login.html", {
            "error": "Invalid email or password",
            "next": next_url,
        })

    print("LOGIN VIEW GET")
    return render(request, "auth/login.html", {"next": next_url})







# Make sure your STRIPE_WEBHOOK_SECRET is loaded from settings
stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def stripe_webhook(request):
    # Stripe sends ONLY POST
    if request.method != "POST":
        return HttpResponse("Webhook endpoint", status=200)

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print("Payment successful:", session)

        user_id = session["metadata"]["user_id"]
        form_slug = session["metadata"]["form_slug"]

        from .models import PaidForm
        PaidForm.objects.get_or_create(
            user_id=user_id,
            form_slug=form_slug
        )

    return HttpResponse(status=200)


import traceback

@login_required
def create_checkout_session(request, country_code, form_slug):

    form_info = get_object_or_404(Form, country__code=country_code, slug=form_slug)

    # Pick correct Price ID based on Stripe mode
    if settings.STRIPE_MODE == "live":
        PRICE_ID = "price_1STc0oL5aHEScFcdbcdX3o0j"   # LIVE price
    else:
        PRICE_ID = "price_1STXpBL5aHEScFcdhakCN4R0"  # TEST price

    # 🔥 NEW: get current user's email
    user_email = request.user.email

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",

        line_items=[
            {
                "price": PRICE_ID,
                "quantity": 1,
            }
        ],

        # 🔥🔥 Pre-fill user’s email in Stripe Checkout
        customer_email=user_email,

        metadata={
            "user_id": request.user.id,
            "form_slug": form_slug,
        },

        success_url=request.build_absolute_uri(
            f"/{country_code}/{form_slug}/?paid=1"
        ),
        cancel_url=request.build_absolute_uri(
            f"/{country_code}/{form_slug}/"
        ),
    )

    return JsonResponse({"id": session.id})





from .models import PaidForm

@login_required
def download_pdf(request, country_code, form_slug):

    # Check if user paid
    has_paid = PaidForm.objects.filter(
        user=request.user,
        form_slug=form_slug
    ).exists()

    if not has_paid:
        # Redirect back to form with flag “payment required”
        return redirect(f"/{country_code}/{form_slug}/?payment_required=1")

    # ---- CALL YOUR EXISTING FILL_PDF LOGIC ----
    return fill_pdf(request, country_code, form_slug)


@login_required
def has_paid(request, country_code, form_slug):
    from .models import PaidForm

    paid = PaidForm.objects.filter(
        user=request.user,
        form_slug=form_slug
    ).exists()

    return JsonResponse({"has_paid": paid})




@login_required
@require_POST
def save_fields(request, country_code, form_slug):

    try:
        body = json.loads(request.body.decode("utf-8"))
    except:
        return JsonResponse({"error": "invalid JSON"}, status=400)

    fields = body.get("fields_data")

    if not fields:
        return JsonResponse({"error": "no fields"}, status=400)

    # ❌ DO NOT CREATE PaidForm HERE
    # Only save to user's session, or store in a different model

    request.session["saved_fields"] = fields
    request.session.modified = True

    return JsonResponse({"saved": True})





@login_required
@require_POST
def pre_generate_pdf(request, country_code, form_slug):
    form_info = get_object_or_404(Form, country__code=country_code, slug=form_slug)

    try:
        body = json.loads(request.body.decode("utf-8"))
        fields_data = body.get("fields_data", {})
    except:
        return JsonResponse({"error": "invalid JSON"}, status=400)

    # ❗ READ ORIGINAL PDF AS BYTES — NEVER OPEN FILE DIRECTLY
    original_bytes = open(form_info.pdf_file.path, "rb").read()
    doc = fitz.open("pdf", original_bytes)

    font_path = os.path.join(settings.BASE_DIR, "main", "fonts", "Arial Unicode.ttf")
    FONT_NAME = "ArialUnicode"
    FONT_SIZE = 10
    OFFSET_X = 0
    OFFSET_Y = 8
    CHECKMARK = "\u2713"

    # Fill fields
    for field in form_info.fields_schema:
        name = field.get("name")
        value = str(fields_data.get(name, ""))

        page_index = max(0, int(field.get("page", 1)) - 1)
        page = doc[page_index]

        page.insert_font(fontfile=font_path, fontname=FONT_NAME)

        x = float(field["pixel_x"]) + OFFSET_X
        y = float(field["pixel_y"]) + OFFSET_Y

        if field.get("type") == "checkbox":
            if value == "1":
                page.insert_text((x, y), CHECKMARK, fontsize=14, fontname=FONT_NAME)
        else:
            if value.strip():
                page.insert_text((x, y), value, fontsize=FONT_SIZE, fontname=FONT_NAME)

    # ALWAYS SAVE TO MEMORY ONLY
    output = io.BytesIO()
    doc.save(output, incremental=False)
    doc.close()
    output.seek(0)

    # Save generated file
    filename = f"{form_slug}_filled_{request.user.id}.pdf"

    from django.core.files.base import ContentFile
    from .models import GeneratedPDF

    GeneratedPDF.objects.filter(user=request.user, form_slug=form_slug).delete()

    GeneratedPDF.objects.create(
        user=request.user,
        form_slug=form_slug,
        pdf_file=ContentFile(output.getvalue(), name=filename)
    )

    return JsonResponse({"ok": True})


@login_required
def download_prepared_pdf(request, country_code, form_slug):
    from .models import GeneratedPDF

    pdf = GeneratedPDF.objects.filter(
        user=request.user,
        form_slug=form_slug
    ).first()

    if not pdf:
        return HttpResponse("No generated PDF found", status=404)

    return FileResponse(
        pdf.pdf_file.open("rb"),
        filename=f"{form_slug}_filled.pdf",
        as_attachment=True,
        content_type="application/pdf"
    )


def logout_view(request):
    logout(request)
    return redirect('home')


from django.http import HttpResponse
from django.conf import settings

def debug_stripe(request):
    return HttpResponse(f"""
        MODE={settings.STRIPE_MODE}<br>
        PK={settings.STRIPE_PUBLIC_KEY}<br>
        SK={settings.STRIPE_SECRET_KEY}<br>
    """)
