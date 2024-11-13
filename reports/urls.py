from django.urls import path
from . import views

urlpatterns = [
    path('provider-access-report/', views.Provider_access_view, name='provider-access-report'),
    path('backlog-report/', views.backlog_report, name='backlog-report'),
    path('export-provider-delivery-report/', views.ProviderDeliveryReportExportView.as_view(), name='export-provider-delivery-report'),
]
