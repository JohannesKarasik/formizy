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


def register_view(request):
   if request.method == 'POST':
       username = request.POST['username']
       password = request.POST['password']
       user = User.objects.create_user(username=username, password=password)
       login(request, user)
       return redirect(request.POST.get('next', '/'))
   return render(request, 'auth/register.html')




def login_view(request):
   if request.method == 'POST':
       username = request.POST['username']
       password = request.POST['password']
       user = authenticate(request, username=username, password=password)
       if user:
           login(request, user)
           return redirect(request.POST.get('next', '/'))
       return render(request, 'auth/login.html', {"error": "Invalid credentials"})
   return render(request, 'auth/login.html')




@require_POST
def login_view(request):
   email = request.POST.get("email")
   password = request.POST.get("password")
   next_url = request.POST.get("next", "/")


   user = authenticate(request, username=email, password=password)
   if user:
       login(request, user)
       return redirect(next_url)


   return redirect(f"{next_url}?login_error=1")




@require_POST
def register_view(request):
   email = request.POST.get("email")
   password = request.POST.get("password")
   next_url = request.POST.get("next", "/")


   if User.objects.filter(username=email).exists():
       return redirect(f"{next_url}?register_error=exists")


   user = User.objects.create_user(username=email, password=password)
   login(request, user)
   return redirect(next_url)