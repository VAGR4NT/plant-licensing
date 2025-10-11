from django.shortcuts import render
from django.http import HttpResponse
from .models import Suppliers
from .models import Businesses
from django.db import connection 
from .query_builder import MODEL_MAP, query_builder

def home_view(request):
    
    total_posts = Suppliers.objects.count()

    context = {
        'number_of_suppliers': total_posts *2,
    }   

    return render(request, "main/index.html", context)

def specific_view(request, param):
    context = {
        'model_map': MODEL_MAP.keys(),
        'operators': ['exact', 'iexact', 'icontains', 'gt', 'gte', 'lt', 'lte'],
        'headers': [],
        'rows': [],
        'error': None,
    }

    # --- Prepare data for easy re-population in the template ---
    form_rules = []
    for i in range(1, 6):
        form_rules.append({
            'num': i,
            'field': request.GET.get(f'field_{i}', ''),
            'operator': request.GET.get(f'operator_{i}', ''),
            'value': request.GET.get(f'value_{i}', ''),
        })
    context['form_rules'] = form_rules
    
    columns_text = request.GET.get('columns', '')

    columns_from_request = [line.strip() for line in columns_text.splitlines() if line.strip()]
 

    context['columns_text'] = "\n".join(columns_from_request)


    # Only run a query if the form has been submitted (we can check for a model_type)
    if 'model_type' in request.GET:
        model_name_from_request = request.GET.get('model_type')
        model_to_query = MODEL_MAP.get(model_name_from_request)

        if not model_to_query:
            context['error'] = f"Invalid model type specified: {model_name_from_request}"
            return render(request, 'main/view/specific_view.html', context)

        # --- Parse Filter Rules from the form ---
        filters_from_request = []
        for rule in form_rules:
            # Only add the rule if all parts are present and the value is not empty
            if rule['field'] and rule['operator'] and rule['value']:
                filters_from_request.append({
                    'field': rule['field'],
                    'operator': rule['operator'],
                    'value': rule['value']
                })
        
        if not columns_from_request:
            context['error'] = "Please select at least one column to display."
            return render(request, 'main/view/specific_view.html', context)

        # --- Call the Backend Service ---
        try:
            headers, rows = query_builder(
                model=model_to_query,
                filters=filters_from_request,
                select_columns=columns_from_request
            )
            context['headers'] = headers
            context['rows'] = rows
        except ValueError as e:
            context['error'] = f"Error building query: {e}"
    
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



