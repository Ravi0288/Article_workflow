from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from .models import Provider_access_report, Provider_backlog_report
import csv
import openpyxl
from rest_framework.views import APIView
from django.http import HttpResponse
from datetime import datetime


# function to format the date
def format_date(date_str):
        if date_str:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%Y-%m-%d')  # Format date as string in 'yyyy-mm-dd'
        return None


# function to fill custom value to overdue_in_days fields
def format_overdue_days(data):
    if data >= 0:
        return 'On Schedule'
    else:
        return '0'

# This will show Provider access report in tabular format in UI
@login_required
@csrf_exempt
def Provider_access_view(request):
    report = Provider_access_report.objects.all().order_by('id')

    # Pagination
    paginator = Paginator(report, 20)  # Show 20 items per page
    page_number = request.GET.get('page')  # Get the current page number
    page_obj = paginator.get_page(page_number)  # Get the page object for the current page

    # prepare the date to be rendered on HTML page
    context = {
        'title' : 'Provider Access View',
        'page_obj' : page_obj
    }

    return render(request, 'reports/provider_access.html', context=context)



# This class will import Provider access report in .csv and .excel format
class ProviderDeliveryReportExportView(APIView):
    def get(self, request, format=None):
        # Check for the file type (Excel or CSV)
        export_type = request.query_params.get('type', 'csv').lower()

        if export_type == 'excel':
            return self.export_excel()
        elif export_type == 'csv':
            return self.export_csv()
        else:
            # prepare the error to be rendered on HTML page
            context = {
                'title' : 'Provider Access Report',
                'page_obj' : "Error Occured"
            }

            return render(request, 'reports/provider_access.html', context=context)

    def export_csv(self):
        # Prepare CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Provider_access_report.csv"'

        writer = csv.writer(response)
        writer.writerow(['Provider', 'Working Name', 'Frequency', 'Overdue in Days', 'Date-1', 'Date-2', 'Date-3', 'Date-4', 'Date-5', 'Date-6'])

        queryset = Provider_access_report.objects.all()
        for record in queryset:
            writer.writerow([record.provider, record.acronym, record.frequency, format_overdue_days(record.overdue_in_days),
                            format_date(record.date1),
                            format_date(record.date2),
                            format_date(record.date3),
                            format_date(record.date4),
                            format_date(record.date5),
                            format_date(record.date6)
                            ])
        
        return response


    def export_excel(self):
        # Prepare Excel response
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Provider Access Report"

        # Add headers
        headers = ['Provider', 'Working Name', 'Frequency', 'Overdue in Days', 'Date-1', 'Date-2', 'Date-3', 'Date-4', 'Date-5', 'Date-6']
        ws.append(headers)

        # Add data
        queryset = Provider_access_report.objects.all()
        for record in queryset:
            ws.append([record.provider, record.acronym, record.frequency, format_overdue_days(record.overdue_in_days),
                            format_date(record.date1),
                            format_date(record.date2),
                            format_date(record.date3),
                            format_date(record.date4),
                            format_date(record.date5),
                            format_date(record.date6)
                        ])

        # Create a file-like object to hold the data
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Provider_access_report.xlsx"'
        
        # Save the workbook to the response
        wb.save(response)
        
        return response




# This will show Provider backlog report in tabular format in UI
@login_required
@csrf_exempt
def backlog_report(request):
    report = Provider_backlog_report.objects.all().order_by('id')

    # Pagination
    paginator = Paginator(report, 20)  # Show 20 items per page
    page_number = request.GET.get('page')  # Get the current page number
    page_obj = paginator.get_page(page_number)  # Get the page object for the current page

    # prepare the date to be rendered on HTML page
    context = {
        'title' : 'Provider Backlog Report',
        'page_obj' : page_obj
    }

    return render(request, 'reports/backlog.html', context=context)


# This class will import Provider backlog report in .csv and .excel format
class backlogReportExportView(APIView):
    def get(self, request, format=None):
        # Check for the file type (Excel or CSV)
        export_type = request.query_params.get('type', 'csv').lower()

        if export_type == 'excel':
            return self.export_excel()
        elif export_type == 'csv':
            return self.export_csv()
        else:
            # prepare the error to be rendered on HTML page
            context = {
                'title' : 'Provider Backlog Report',
                'page_obj' : "Error Occured"
            }

            return render(request, 'reports/backlog.html', context=context)


    def export_csv(self):
        # Prepare CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Provider_backlog_report.csv"'

        writer = csv.writer(response)
        writer.writerow(['Provider', 'Working Name', 'Overdue in Days', 'Archive in Backlog', 'Articles Waiting'])

        queryset = Provider_backlog_report.objects.all()
        for record in queryset:
            writer.writerow([record.provider, record.acronym, format_overdue_days(record.overdue_in_days),
                             record.archive_in_backlog, record.articles_waiting])
        
        return response


    def export_excel(self):
        # Prepare Excel response
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Provider Delivery Report"

        # Add headers
        headers = ['Provider', 'Working Name', 'Overdue in Days', 'Archive in Backlog', 'Articles Waiting']
        ws.append(headers)

        # Add data
        queryset = Provider_backlog_report.objects.all()
        for record in queryset:
            ws.append([record.provider, record.acronym, format_overdue_days(record.overdue_in_days),
                       record.archive_in_backlog, record.articles_waiting])

        # Create a file-like object to hold the data
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Provider_backlog_report.xlsx"'
        
        # Save the workbook to the response
        wb.save(response)
        
        return response
