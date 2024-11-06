from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from .models import Provider_access_report, Provider_delivery_report
from django.core import serializers

@login_required
@csrf_exempt
def Provider_access_view(request):
    report = Provider_access_report.objects.all()

    # Pagination
    paginator = Paginator(report, 20)  # Show 20 items per page
    page_number = request.GET.get('page')  # Get the current page number
    page_obj = paginator.get_page(page_number)  # Get the page object for the current page

    # prepare the date to be rendered on HTML page
    context = {
        'title' : 'Provider Acccess View',
        'page_obj' : page_obj
    }

    return render(request, 'reports/provider_access.html', context=context)


@login_required
@csrf_exempt
def delivery_view(request):
    report = Provider_delivery_report.objects.all()

    # Pagination
    paginator = Paginator(report, 20)  # Show 20 items per page
    page_number = request.GET.get('page')  # Get the current page number
    page_obj = paginator.get_page(page_number)  # Get the page object for the current page

    # prepare the date to be rendered on HTML page
    context = {
        'title' : 'Provider Delivery Report',
        'page_obj' : page_obj
    }

    return render(request, 'reports/backlog.html', context=context)

