from django.shortcuts import render
from django.http import HttpResponse
from .models import Suppliers
from .models import Businesses
from django.db import connection 

def home_view(request):
    
    total_posts = Suppliers.objects.count()

    context = {
        'number_of_suppliers': total_posts *2,
    }   

    return render(request, "main/index.html", context)

def specific_view(request, param):

    PARAMS = {
        'business_name' : 0,
        'mo_address' : 1,
        'mo_city' : 2,
        'supplier_name' : 3
    }

    table = Businesses
    attribute = ""

    match PARAMS[param]:
        case 0:
            attribute = "business_name"
        case 1:
            attribute = "mo_address"
        case 2:
            attribute = "mo_city"
        case 3: 
            attribute = "supplier_name"
            table = Suppliers
        case _:
            raise Http404("Invalid search category")

    query = request.GET.get('q')
    subset = table.objects.none()

    if query:
        filter_kwargs = {f"{attribute}__icontains": query}
        subset  = table.objects.filter(**filter_kwargs)

    context = {
        'results': subset,
        'param': param, 
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



