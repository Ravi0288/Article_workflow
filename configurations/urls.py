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
    path('email/', include('mail_service.urls')),
    path('accounts/', include('accounts.urls')),
    # path('', include('accounts.urls')),
    # path('', include('authentication.urls')),
    path('', include('step1.urls')),
    path('step2/', include('step2.urls')),
    path('step3/', include('step3.urls')),
    path('email/', include('mail_service.urls')),
    path('handles/', include('model.urls'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
