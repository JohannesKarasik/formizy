from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.conf import settings
import stripe
from django.views.decorators.csrf import csrf_exempt


import json, io, os
import fitz  # PyMuPDF


from .models import Form




# ===========================
# BASIC PAGES
# ===========================


def home(request):
   countries = [
       {"code": "de", "name": "Germany", "flag": "🇩🇪"},
       {"code": "dk", "name": "Denmark", "flag": "🇩🇰"},
       {"code": "us", "name": "United States", "flag": "🇺🇸"},
       {"code": "fr", "name": "France", "flag": "🇫🇷"},
   ]
   return render(request, 'main/home.html', {"countries": countries})




def country(request, country_code):
   forms_by_country = {
       "de": [
           {"name": "Fragebogen zur steuerlichen Erfassung", "slug": "steuer-erfassung"},
           {"name": "Gewerbeanmeldung", "slug": "gewerbeanmeldung"},
       ],
       "dk": [
           {"name": "Ansøgning om SU", "slug": "su-application"},
           {"name": "CPR-registrering", "slug": "cpr-registration"},
       ],
       "us": [
           {"name": "W-9 Form", "slug": "w9"},
           {"name": "1040 Individual Income Tax Return", "slug": "1040"},
       ],
   }


   country_names = {
       "de": "Germany",
       "dk": "Denmark",
       "us": "United States",
       "fr": "France",
   }


   return render(request, 'main/country.html', {
       "country_code": country_code,
       "country_name": country_names.get(country_code, "Unknown Country"),
       "forms": forms_by_country.get(country_code, []),
   })




# ===========================
# FORM DETAIL (PDF viewer)
# ===========================


def form_detail(request, country_code, form_slug):
   form_info = get_object_or_404(Form, country__code=country_code, slug=form_slug)
   pdf_url = form_info.pdf_file.url


   # Load first page to get original width
   pdf_path = form_info.pdf_file.path
   doc = fitz.open(pdf_path)
   page = doc[0]
   pdf_original_width = page.rect.width
   doc.close()


   FIXED_WIDTH = 833   # must match mapper EXACTLY
   viewer_scale = FIXED_WIDTH / pdf_original_width


   return render(request, "main/pdf_clean_viewer.html", {
    "form_info": form_info,
    "pdf_url": pdf_url,
    "country_code": country_code,
    "viewer_scale": viewer_scale,
    "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
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

    # Parse JSON
    try:
        body = json.loads(request.body.decode("utf-8"))
        fields_data = body.get("fields_data", {})
    except Exception as e:
        return JsonResponse({"error": f"Invalid JSON: {e}"}, status=400)

    if not form_info.fields_schema:
        return JsonResponse({"error": "No field schema defined"}, status=400)

    # Load PDF
    doc = fitz.open(form_info.pdf_file.path)

    # Load the good font (✓ supported)
    font_path = os.path.join(settings.BASE_DIR, "main", "fonts", "Arial Unicode.ttf")
    FONT_NAME = "ArialUnicode"
    FONT_SIZE = 10

    OFFSET_X = 0
    OFFSET_Y = 8

    CHECKMARK = "\u2713"  # real ✓ character

    print("=== FILL_PDF DEBUG START ===")

    for field in form_info.fields_schema:

        value = fields_data.get(field.get("name"), "")
        if value is None:
            value = ""

        # Skip empty unless text field
        if field.get("type") != "checkbox" and value == "":
            continue

        # Determine page index
        try:
            page_index = int(field.get("page", 1)) - 1
        except:
            page_index = 0

        if not (0 <= page_index < len(doc)):
            continue

        page = doc[page_index]

        # Insert font ONCE per page (safe to call multiple times)
        page.insert_font(fontfile=font_path, fontname=FONT_NAME)

        # Coordinates
        px = float(field.get("pixel_x", 0))
        py = float(field.get("pixel_y", 0))
        x = px + OFFSET_X
        y = py + OFFSET_Y

        # -----------------------
        # CHECKBOX FIELD → draw ✓
        # -----------------------
        if field.get("type") == "checkbox":
            if str(value) == "1":  # checked
                page.insert_text(
                    (x, y),
                    CHECKMARK,
                    fontsize=14,
                    fontname=FONT_NAME,
                    color=(0, 0, 0),
                    overlay=True,
                )
            continue  # skip text printing for checkboxes

        # -----------------------
        # NORMAL TEXT FIELD
        # -----------------------
        page.insert_text(
            (x, y),
            str(value),
            fontsize=FONT_SIZE,
            fontname=FONT_NAME,
            color=(0, 0, 0),
            overlay=True,
        )

    print("=== FILL_PDF DEBUG END ===")

    # Output PDF
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    doc.close()

    return FileResponse(
        output,
        filename=f"{form_info.slug}_filled.pdf",
        as_attachment=True,
        content_type="application/pdf",
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
        return JsonResponse({"error": "method not allowed"}, status=405)

    print("REGISTER POST:", request.POST)

    email = request.POST.get("email")
    password = request.POST.get("password")
    next_url = request.POST.get("next", "/")

    if not email or not password:
        return JsonResponse({"error": "missing fields"}, status=400)

    if User.objects.filter(username=email).exists():
        return JsonResponse({"error": "exists"}, status=400)

    try:
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )
        login(request, user)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

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


@login_required
def create_checkout_session(request, country_code, form_slug):

    form_info = get_object_or_404(Form, country__code=country_code, slug=form_slug)

    # Pick correct Price ID based on Stripe mode
    if settings.STRIPE_MODE == "live":
        PRICE_ID = "price_1STXUlL5aHEScFcdpdISRojS"   # LIVE price
    else:
        PRICE_ID = "price_1STXpBL5aHEScFcdhakCN4R0"  # TEST price (replace with yours)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",

        # Use your predefined product price
        line_items=[
            {
                "price": PRICE_ID,
                "quantity": 1,
            }
        ],

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
    body = json.loads(request.body.decode("utf-8"))
    fields = body.get("fields_data")

    if not fields:
        return JsonResponse({"error": "no fields"}, status=400)

    paid_obj, created = PaidForm.objects.get_or_create(
        user=request.user,
        form_slug=form_slug
    )

    paid_obj.fields_json = fields
    paid_obj.save()

    return JsonResponse({"saved": True})
