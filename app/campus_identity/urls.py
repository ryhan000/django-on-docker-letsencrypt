from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


admin.site.site_title = 'Campus Admin Panel'
admin.site.site_header = 'Campus'
admin.site.index_title = 'Campus Site administration'

site_title = admin.site.site_title
site_header = admin.site.site_header
index_title = admin.site.index_title


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('registration_api.urls')),
    path('enrollment/', include('enrollment_api.urls')),
]
if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
