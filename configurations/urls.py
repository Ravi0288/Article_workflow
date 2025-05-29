from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

# URL configurations
urlpatterns = [
    path('admin/', admin.site.urls),
    path('step1/', include('step1.urls')),
    path('step2/', include('step2.urls')),
    path('step3/', include('step3.urls')),
    path('step4/', include('step4.urls')),
    path('step5/', include('step5.urls')),
    path('step6/', include('step6.urls')),
    path('step7/', include('step7.urls')),
    path('step8/', include('step8.urls')),
    path('step9/', include('step9.urls')),
    path('step10/', include('step10.urls')),
    # path('step11/', include('step11.urls')),
    path('accounts/', include('accounts.urls')),
    path('', include('accounts.urls')),
    path('email/', include('mail_service.urls')),
    path('reports/', include('reports.urls')),
]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)