"""
URL configuration for nal_library_conf project.

Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


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
    path('', include('accounts.urls')),
    # path('', include('authentication.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
