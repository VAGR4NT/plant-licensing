from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.urls import reverse
from django import forms
from .models import Suppliers
from .models import Businesses, Locations, Licenses
from django.db import connection 
from .query_builder import MODEL_MAP, query_builder, format_table, _validate_and_get_field
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
        'checked_columns': request.GET.getlist('columns'),
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


def update_view(request, pk):
    # 1. Get the main object and the columns to edit from the request
    business = get_object_or_404(Businesses, pk=pk)
    columns_to_edit = request.GET.getlist('columns')

    # A helper to get related objects without duplicates
    def get_instance_from_path(root_instance, path):
        instance = root_instance
        parts = path.split('__')
        for part in parts[:-1]: # Go through relations (e.g., 'locations')
            instance = getattr(instance, part).first() # Or other logic to get the right one
            if not instance: return None
        return instance

    if request.method == 'POST':
        # 4. Handle SAVING the data
        instances_to_save = {}
        for field_path, value in request.POST.items():
            if field_path == 'csrfmiddlewaretoken':
                continue

            instance = get_instance_from_path(business, field_path)
            field_name = field_path.split('__')[-1]

            if instance:
                setattr(instance, field_name, value)
                # Store the instance to save it only once
                instances_to_save[instance.pk] = instance
        
        for instance in instances_to_save.values():
            instance.save()
            
        return redirect("success")

    # 2. Dynamically build the form
    class DynamicForm(forms.Form):
        pass

    form = DynamicForm()
    
    for field_path in columns_to_edit:
        try:
            # Get the final model field object to know its type
            field_object = _validate_and_get_field(Businesses, field_path)
            
            # Find the actual instance and its current value
            instance = get_instance_from_path(business, field_path)
            field_name = field_path.split('__')[-1]
            initial_value = getattr(instance, field_name) if instance else ''

            # Create a form field and add it to our dynamic form
            # The field's name in the form is the full path, which is crucial for saving
            form.fields[field_path] = forms.CharField(label=field_object.verbose_name.title(), initial=initial_value)
        
        except (ValueError, AttributeError):
            # Skip fields that can't be found or resolved
            continue
            
    # 3. Render the page with the dynamically generated form
    context = {
        'form': form,
        'business': business
    }


    return render(request, "main/update/index.html", context)

def update_success(request):
    return render(request, "main/update/success.html")

def user_info_view(request):
    return render(request, "main/user-info/index.html")



