# Django libs:
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin URL:
    path('admin/', admin.site.urls),

    # Default URL:
    path('', include('projects.urls', namespace="projects")),
]
