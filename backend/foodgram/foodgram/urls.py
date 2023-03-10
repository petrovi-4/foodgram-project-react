from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    path('api/auth', include('users.urls')),
    path('api/users', include('users.urls')),
]
