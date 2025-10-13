from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from .models import Suppliers
from .models import Businesses, Locations, Licenses
from django.db import connection 
from .query_builder import MODEL_MAP, query_builder, format_table
import json

def home_view(request):
    
    total_posts = Suppliers.objects.count()

    context = {
        'number_of_suppliers': total_posts *2,
    }   

    return render(request, "main/index.html", context)

def specific_view(request):
    table_fields_data = {}
    
    significant_tables = {
        'Business Details': {'model': Businesses, 'prefix': ''},
        'Location Details': {'model': Locations,  'prefix': 'locations__'},
        'License Details':  {'model': Licenses,   'prefix': 'locations__licenses__'},
        'Supplier Details': {'model': Suppliers,  'prefix': 'suppliers__'},
    }

    for table, info in significant_tables.items():
        fields_for_group = []
        model_class = info['model']
        path_prefix = info['prefix']

        for field in model_class._meta.fields:
            clean_label = field.name.replace("_", " ").title()
            fields_for_group.append({
                'name': f"{path_prefix}{field.name}",
                'label': clean_label
            })
        table_fields_data[table] = fields_for_group
    
    context = {
        'table_fields': table_fields_data, 
        'operators': ['exact', 'iexact', 'icontains', 'gt', 'gte', 'lt', 'lte'],
        'headers': [],
        'rows': [],
        'error_message': None,
        'result_count': None,
        'request_get': request.GET, 
    }

    search_type = request.GET.get('search_type')
    if search_type:
        root_model = MODEL_MAP.get(search_type)
        if root_model:
            try:
                filters = []
                if request.GET.get('q'):
                    primary_search_fields = {
                        'business': 'business_name', 'supplier': 'suppliers__supplier_name', 'location': 'locations__address'
                    }
                    search_field = primary_search_fields.get(search_type)
                    if search_field:
                        filters.append({'field': search_field, 'operator': 'icontains', 'value': request.GET.get('q')})

                for i in range(1, 6): 
                    field = request.GET.get(f'adv_field_{i}')
                    op = request.GET.get(f'adv_op_{i}')
                    val = request.GET.get(f'adv_val_{i}')
                    if field and op and val:
                        filters.append({'field': field, 'operator': op, 'value': val})
                
                select_columns = request.GET.getlist('columns')
                if not select_columns:
                    select_columns = ['business_name', 'mo_city'] if search_type == 'business' else ['suppliers__supplier_name', 'suppliers__city']

                queryset = query_builder(Businesses, filters=filters)
                context['result_count'] = queryset.count()
                
                display_data = format_table(
                    queryset, 
                    select_columns 
                )
                context.update(display_data)

            except ValueError as e:
                context['error_message'] = f"Error building query: {e}"

    return render(request, 'main/view/specific_view.html', context)

def direct_access_view(request):
    return render(request, "main/direct-access/index.html")


def view_db_view(request):
    return render(request, "main/view/index.html")


def generate_forms_view(request):
    return render(request, "main/generate-forms/index.html")


def update_view(request, model_name, pk):
    """
    Handles displaying and processing the edit form for a single database object.
    """
    model_class = MODEL_MAP.get(model_name)
    if not model_class:
        raise Http404(f"Invalid model type '{model_name}' specified.")

    # Use get_object_or_404 to safely fetch the object or return a Not Found page
    instance = get_object_or_404(model_class, pk=pk)

    if request.method == 'POST':
        # --- Handle the SAVE action ---
        for field in model_class._meta.fields:
            # Don't try to change the primary key
            if not field.primary_key:
                submitted_value = request.POST.get(field.name)
                # This check is important. It ensures that if a field isn't in the form,
                # we don't accidentally overwrite its value with None.
                if submitted_value is not None:
                    setattr(instance, field.name, submitted_value)
        instance.save()
        # Redirect back to the same page to show a confirmation or the updated data
        return redirect('update_page', model_name=model_name, pk=pk)

    # --- Handle the initial GET request to display the form ---
    fields_to_edit = []
    for field in model_class._meta.fields:
        fields_to_edit.append({
            'name': field.name,
            'label': field.verbose_name.title(),
            'value': getattr(instance, field.name),
            'is_readonly': field.primary_key, # Make the ID field read-only in the form
        })

    context = {
        'instance': instance,
        'fields': fields_to_edit,
        'model_name': model_name,
    }
    return render(request, "main/update/index.html")


def user_info_view(request):
    return render(request, "main/user-info/index.html")



