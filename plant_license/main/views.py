from django.shortcuts import render
from django.db import connection 

from io import BytesIO
from pathlib import Path
from django.conf import settings
from django.http import HttpResponse, Http404
from django.utils import timezone

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, BooleanObject, DictionaryObject

from .models import Businesses, Locations, Licenses, Suppliers, BusinessSuppliers

def home_view(request):
    
    total_posts = Suppliers.objects.count()

    context = {
        'number_of_suppliers': total_posts *2,
    }   

    return render(request, "main/index.html", context)

def specific_view(request, category):
    ALLOWED_SEARCH_FIELDS = ['business_name', 'business_id']

    if category not in ALLOWED_SEARCH_FIELDS:
        raise Http404("Invalid search category")

    query = request.GET.get('q')
    businesses = Businesses.objects.none()

    if query:
        filter_kwargs = {f"{category}__icontains": query}
        businesses = Businesses.objects.filter(**filter_kwargs)

    context = {
        'businesses': businesses,
        'category': category, 
        'query': query,
    } 
    
    return render(request, 'main/view/specific_view.html', context)

def direct_access_view(request):
    return render(request, "main/direct-access/index.html")


def view_db_view(request):
    return render(request, "main/view/index.html")


def generate_forms_view(request):
    return render(request, "main/generate-forms/index.html")


def update_view(request):
    return render(request, "main/update/index.html")


def user_info_view(request):
    return render(request, "main/user-info/index.html")

def dealer_generate(request):
    return render(request, "main/dealer_generate/index.html")

def nursery_generate(request):
    businesses = Businesses.objects.order_by("business_name")
    return render(request, "main/nursery_generate/index.html", {"businesses": businesses})

TEMPLATE_PATH = Path(settings.BASE_DIR) / "pdfs" / "nursery_renewal_fillable.pdf"

def _fill_pdf(template_path: str, field_map: dict) -> bytes:
    reader = PdfReader(template_path)

    # 1) Guard: template must have AcroForm
    root = reader.trailer.get("/Root", {})
    acroform = root.get("/AcroForm")
    if not acroform:
        raise ValueError(
            f"{template_path} has no AcroForm (not a fillable PDF). "
            "Be sure you are using the *fillable* template."
        )

    writer = PdfWriter()

    # 2) Copy pages first
    for p in reader.pages:
        writer.add_page(p)

    # 3) Copy the AcroForm from reader to writer *before* updating values
    writer._root_object.update({NameObject("/AcroForm"): acroform})

    # 4) Now it's safe to set field values
    #    (adjust page index if your fields are on a later page)
    writer.update_page_form_field_values(writer.pages[0], field_map)

    # 5) Make sure appearances render in viewers
    writer._root_object["/AcroForm"].update({NameObject("/NeedAppearances"): BooleanObject(True)})

    out = BytesIO()
    writer.write(out)
    return out.getvalue()

def download_nursery_pdf(request, business_id: int):
    # Get the business row by business_id (this is your “key”)
    try:
        biz = Businesses.objects.get(pk=business_id)
    except Businesses.DoesNotExist:
        raise Http404("Business not found")

    # Choose a representative location (adjust selection rule if needed)
    location = (Locations.objects
                .filter(business=biz)
                .order_by("location_id")
                .first())

    # Suppliers (many-to-many via join)
    supplier_names = (Suppliers.objects
                      .filter(businesssuppliers__business=biz)
                      .values_list("supplier_name", flat=True))
    suppliers_text = "\n".join([s for s in supplier_names if s])

    # Fees: $40 + $1.50 per acre
    acreage = float(biz.acreage or 0)
    amount_due_val = 40.00 + 1.50 * acreage
    amount_due_str = f"${amount_due_val:,.2f}"

    # Field locations: split notes across up to 4 lines (or synthesize)
    location_lines = []
    if location and (location.field_location_notes or "").strip():
        for line in (location.field_location_notes or "").splitlines():
            line = line.strip()
            if line:
                location_lines.append(line)
            if len(location_lines) == 4:
                break
    else:
        qs = (Locations.objects
              .filter(business=biz)
              .order_by("location_id")
              .values("city", "county", "zip_code"))[:4]
        for rec in qs:
            parts = [p for p in [rec.get("city"), rec.get("county"), rec.get("zip_code")] if p]
            if parts:
                location_lines.append(", ".join(parts))
    while len(location_lines) < 4:
        location_lines.append("")

    # Checkbox (email vs USPS) — set as you wish or leave "Off"
    prefers_email = True
    checkbox_val = "Yes" if prefers_email else "Off"

    # Today’s date for the certification line
    today_str = timezone.localdate().strftime("%m/%d/%Y")

    # Map DB → THIS form’s fields
    field_map = {
        # Header: put business_id into “License Number”
        "License Number":       str(business_id),
        "current_license_year1": "",  

        # Mailing Information
        "business_name":        biz.business_name or "",
        "mailing_address":      biz.mo_address or "",
        "main_office_city1":     biz.mo_city or "",
        "main_office_state":    biz.mo_state or "",
        "main_office_zip1":      biz.mo_zip or "",
        "main_office_county":   (location.county if location and location.county else ""),

        # Contact
        "main_contact_name":    biz.main_contact_name or "",
        "main_office_city2":     biz.mo_city or "",
        "main_office_zip2":      biz.mo_zip or "",
        "phone_number":         biz.main_contact_phone or "",
        "fax":                  "",
        "main_contact_email":   biz.main_contact_email or "",

        # Field locations (4 lines on this form)
        "field_location1":      location_lines[0],
        "field_location2":      location_lines[1],
        "field_location3":      location_lines[2],
        "field_location4":      location_lines[3],

        # Fees
        "acreage":              f"{acreage:g}",
        "amount_due":           amount_due_str,
        "Amt":                  amount_due_str,  # mirror into bottom box if desired

        # Checkbox + date
        "Check Box17":          checkbox_val,
        "Date":                 today_str,

        # Bottom admin box
        "Lic Year":             "",
        "Date Recd":            "",
        "Check":                "",
    }

    filled = _fill_pdf(str(TEMPLATE_PATH), field_map)
    resp = HttpResponse(filled, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="nursery_renewal_{business_id}.pdf"'
    return resp
