from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.urls import reverse
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms import modelform_factory
from .models import Suppliers
from .models import Businesses, Locations, Licenses
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
        "independent_models" : {},
    }

    django_junk = [
        'DjangoAdminLog',
        'DjangoContentType',
        'DjangoMigrations',
        'DjangoSession',
    
        'AuthUser',
        'AuthGroup',
        'Businesses',
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
        context['error'] = "Problem"

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
        form = DynamicModelForm(request.POST, instance=master_object)
        
        if form.is_valid():
            form.save()
            return redirect(request.path)
    else:
        form = DynamicModelForm(instance=master_object)

    related_sections = {}
    
    all_models = apps.get_models()
    
    for other_model in all_models:
        if other_model == model_class or getattr(other_model, "is_through_table", False):
            continue
            
        for field in other_model._meta.get_fields():
            
            # Check if this field is a ForeignKey pointing to our 'model'
            if isinstance(field, (ForeignKey, ManyToManyField)) and field.related_model == model_class:
                if getattr(field, "through", None) and not field.remote_field.through._meta.auto_created:
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
        'master_object': master_object,
        'form': form,
        'related_sections': related_sections,
        'master_model_name': model_class._meta.model_name
    }

    return render(request, "main/update/index.html", context)


def update_success(request):
    return render(request, "main/update/success.html")

def user_info_view(request):
    return render(request, "main/user-info/index.html")

def account_view(request):
    return render(request, "main/account/index.html")
