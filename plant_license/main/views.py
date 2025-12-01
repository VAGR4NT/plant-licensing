from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.urls import reverse
from django import forms
import csv
from django.contrib.contenttypes.models import ContentType
from django.forms import modelform_factory
from django.db import connection
from .query_builder import (
    MODEL_MAP,
    query_builder,
    format_table,
    _validate_and_get_field,
)
import json
from django.apps import apps
from django.db.models import ForeignKey, OneToOneField, ManyToManyField

from io import BytesIO
from pathlib import Path
from django.conf import settings
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Protection, PatternFill

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, BooleanObject, DictionaryObject

from .models import Businesses, Locations, Licenses, Suppliers, BusinessSuppliers


def home_view(request):
    total_posts = Suppliers.objects.count()

    context = {
        "number_of_suppliers": total_posts * 2,
    }

    return render(request, "main/index.html", context)


def specific_view(request):
    table_fields_data = {}

    significant_tables = {
        "Business Details": {"model": Businesses, "prefix": ""},
        "Location Details": {"model": Locations, "prefix": "locations__"},
        "License Details": {"model": Licenses, "prefix": "locations__licenses__"},
        "Supplier Details": {"model": Suppliers, "prefix": "suppliers__"},
    }

    for table, info in significant_tables.items():
        fields_for_group = []
        model_class = info["model"]
        path_prefix = info["prefix"]

        for field in model_class._meta.fields:
            clean_label = field.name.replace("_", " ").title()
            fields_for_group.append(
                {"name": f"{path_prefix}{field.name}", "label": clean_label}
            )
        table_fields_data[table] = fields_for_group

    context = {
        "table_fields": table_fields_data,
        "operators": ["exact", "iexact", "icontains", "gt", "gte", "lt", "lte"],
        "headers": [],
        "rows": [],
        "business_model_id": ContentType.objects.get_for_model(Businesses).id,
        "error_message": None,
        "result_count": None,
        "request_get": request.GET,
        "checked_columns": request.GET.getlist("columns"),
    }

    search_type = request.GET.get("search_type")
    if search_type:
        root_model = MODEL_MAP.get(search_type)
        if root_model:
            try:
                filters = []
                if request.GET.get("q"):
                    primary_search_fields = {
                        "business": "business_name",
                        "supplier": "suppliers__supplier_name",
                        "location": "locations__address",
                    }
                    search_field = primary_search_fields.get(search_type)
                    if search_field:
                        filters.append(
                            {
                                "field": search_field,
                                "operator": "icontains",
                                "value": request.GET.get("q"),
                            }
                        )

                for i in range(1, 6):
                    field = request.GET.get(f"adv_field_{i}")
                    op = request.GET.get(f"adv_op_{i}")
                    val = request.GET.get(f"adv_val_{i}")
                    if field and op and val:
                        filters.append({"field": field, "operator": op, "value": val})

                select_columns = request.GET.getlist("columns")
                if not select_columns:
                    select_columns = (
                        ["business_name", "mo_city"]
                        if search_type == "business"
                        else ["suppliers__supplier_name", "suppliers__city"]
                    )

                queryset = query_builder(Businesses, filters=filters)
                context["result_count"] = queryset.count()

                display_data = format_table(queryset, select_columns)
                context.update(display_data)

            except ValueError as e:
                context["error_message"] = f"Error building query: {e}"

    return render(request, "main/view/specific_view.html", context)


def direct_access_view(request):
    return render(request, "main/direct-access/index.html")


def view_db_view(request):
    context = {
        "independent_models": {},
    }

    django_junk = [
        "DjangoAdminLog",
        "DjangoContentType",
        "DjangoMigrations",
        "DjangoSession",
        "AuthUser",
        "AuthGroup",
        "Businesses",
    ]

    try:
        # Get a list of all our tables
        all_models = apps.get_app_config("main").get_models()

        # Loop through each model and check if it is dependent
        for model in all_models:
            if model._meta.object_name in django_junk:
                continue

            is_independent = True
            for field in model._meta.fields:
                if isinstance(field, (ForeignKey, OneToOneField)):
                    is_independent = False
                    break

            if is_independent:
                context["independent_models"][model._meta.verbose_name.title()] = model

    except LookupError:
        context["error"] = "Problem"

    return render(request, "main/view/index.html", context)


def generate_forms_view(request):
    return render(request, "main/generate-forms/index.html")


def update_view(request, ct, pk):
    """
    A dynamic view to display and update any model instance ("master_object")
    and list its related "child" objects.
    """
    model_class = ContentType.objects.get(id=ct).model_class()

    master_object = get_object_or_404(model_class, pk=pk)

    local_field_names = [field.name for field in model_class._meta.fields if not field.is_relation]
    DynamicModelForm = modelform_factory(model_class, fields=local_field_names) 


    if request.method == 'POST':
        if 'delete' in request.POST:
            master_object.delete()
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        form = DynamicModelForm(request.POST, instance=master_object)

        if form.is_valid():
            form.save()
            return redirect(request.path)
 
    else:
        form = DynamicModelForm(instance=master_object)

    related_sections = {}

    all_models = apps.get_models()

    for other_model in all_models:
        if other_model == model_class or getattr(
            other_model, "is_through_table", False
        ):
            continue

        for field in other_model._meta.get_fields():
            # Check if this field is a ForeignKey pointing to our 'model'
            if (
                isinstance(field, (ForeignKey, ManyToManyField))
                and field.related_model == model_class
            ):
                if (
                    getattr(field, "through", None)
                    and not field.remote_field.through._meta.auto_created
                ):
                    continue

                accessor_name = field.remote_field.get_accessor_name()

                if not accessor_name or not hasattr(master_object, accessor_name):
                    continue

                queryset = getattr(master_object, accessor_name).all()

                related_sections[other_model._meta.verbose_name.title()] = {
                    'items': queryset,
                    'model': ContentType.objects.get_for_model(other_model).id
                }

    for field in model_class._meta.get_fields():
        if isinstance(field, ManyToManyField):
            accessor_name = field.name
            queryset = getattr(master_object, accessor_name).all()
            related_sections[field.related_model._meta.verbose_name.title()] = {
                'items': queryset,
                'model': ContentType.objects.get_for_model(field.related_model).id
            }

    context = {
        "master_object": master_object,
        "form": form,
        "related_sections": related_sections,
        "master_model_name": model_class._meta.model_name,
    }

    return render(request, "main/update/index.html", context)


def update_success(request):
    return render(request, "main/update/success.html")


def user_info_view(request):
    return render(request, "main/user-info/index.html")


def account_view(request):
    return render(request, "main/account/index.html")


def dealer_generate(request):
    return render(request, "main/dealer_generate/index.html")


def nursery_generate(request):
    businesses = Businesses.objects.order_by("business_name")
    return render(
        request, "main/nursery_generate/index.html", {"businesses": businesses}
    )


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
    writer._root_object["/AcroForm"].update(
        {NameObject("/NeedAppearances"): BooleanObject(True)}
    )

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
    location = Locations.objects.filter(business=biz).order_by("location_id").first()

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
        qs = (
            Locations.objects.filter(business=biz)
            .order_by("location_id")
            .values("city", "county", "zip_code")
        )[:4]
        for rec in qs:
            parts = [
                p
                for p in [rec.get("city"), rec.get("county"), rec.get("zip_code")]
                if p
            ]
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
        "License Number": str(business_id),
        "current_license_year1": "",
        # Mailing Information
        "business_name": biz.business_name or "",
        "mailing_address": biz.mo_address or "",
        "main_office_city1": biz.mo_city or "",
        "main_office_state": biz.mo_state or "",
        "main_office_zip1": biz.mo_zip or "",
        "main_office_county": (location.county if location and location.county else ""),
        # Contact
        "main_contact_name": biz.main_contact_name or "",
        "main_office_city2": biz.mo_city or "",
        "main_office_zip2": biz.mo_zip or "",
        "phone_number": biz.main_contact_phone or "",
        "fax": "",
        "main_contact_email": biz.main_contact_email or "",
        # Field locations (4 lines on this form)
        "field_location1": location_lines[0],
        "field_location2": location_lines[1],
        "field_location3": location_lines[2],
        "field_location4": location_lines[3],
        # Fees
        "acreage": f"{acreage:g}",
        "amount_due": amount_due_str,
        "Amt": amount_due_str,  # mirror into bottom box if desired
        # Checkbox + date
        "Check Box17": checkbox_val,
        "Date": today_str,
        # Bottom admin box
        "Lic Year": "",
        "Date Recd": "",
        "Check": "",
    }

    filled = _fill_pdf(str(TEMPLATE_PATH), field_map)
    resp = HttpResponse(filled, content_type="application/pdf")
    resp["Content-Disposition"] = (
        f'attachment; filename="nursery_renewal_{business_id}.pdf"'
    )
    return resp


def export_table_as_csv(request):

    # Create the HttpResponse object with the appropriate CSV header.
    # This tells the browser to treat the response as a file to be downloaded.
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="data.csv"'},
    )

    # Get all data from your model
    # This assumes your model is SampleData. Replace with your actual model.
    queryset = Businesses.objects.all()

    # Check if there is any data to write
    if not queryset.exists():
        response.write("No data found.")
        return response

    # Get the model's field names
    # We use _meta.fields to get all field objects
    # and then get the name for each field.
    field_names = [field.name for field in Businesses._meta.fields]

    # Create a CSV writer object using the response as the file
    writer = csv.writer(response)

    # Write the header row
    writer.writerow(field_names)

    # Iterate over the queryset and write each row to the CSV
    for obj in queryset:
        # Create a list of values for the current object
        row = [getattr(obj, field) for field in field_names]
        writer.writerow(row)

    return response


def export_table_as_xlsx(request):
    # 1. Create a new Workbook and get the active worksheet
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Business Data" 

    PROTECTION_PASSWORD = 'LockHeader'

    # 2. Configure the HTTP Response for XLSX
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename="data_protected.xlsx"'},
    )

    # 3. Get all data and field names
    queryset = Businesses.objects.all()
    if not queryset.exists():
        pass # Handle empty queryset as before

    field_names = [field.name for field in Businesses._meta.fields]
    num_columns = len(field_names)

    # 4. Write the header row (This row will remain locked by default)
    worksheet.append(field_names)

    # 5. Write data rows AND UNLOCK the data cells
    
    # We start iterating from row 2 (index 1) for data
    row_num = 2 
    for obj in queryset:
        row_data = [getattr(obj, field) for field in field_names]
        worksheet.append(row_data)

        # Unlock all cells in the current data row (row_num)
        for col_index in range(1, num_columns + 1):
            col_letter = get_column_letter(col_index)
            cell = worksheet[f'{col_letter}{row_num}']
            
            # Key Step 1: Set the protection to 'unlocked'
            cell.protection = Protection(locked=False)
            
        
        row_num += 1


    worksheet.protection.sheet = True 
    worksheet.protection.password = PROTECTION_PASSWORD
    
    # You can configure what the user is allowed to do while the sheet is protected
    worksheet.protection.sort = True        
    worksheet.protection.autofilter = True  
    worksheet.protection.insertRows = True  
    worksheet.protection.insertColumns = True

    # 7. Save the workbook to the HttpResponse file-like object
    workbook.save(response)

    return response



