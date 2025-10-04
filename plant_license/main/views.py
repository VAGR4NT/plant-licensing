from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User  # or import your custom models
from django.db import connection 

def home_view(request):
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM suppliers")
        row = cursor.fetchone()

    total_posts = row[0]

    context = {
        'number_of_suppliers': total_posts,
    }

    return render(request, "main/index.html", context)


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


def database_check_view(request):
    try:
        # Simple test query
        user_count = User.objects.count()
        return HttpResponse(f"Database is working! User count: {user_count}")

    except Exception as e:
        return HttpResponse(f"Database error: {str(e)}")
