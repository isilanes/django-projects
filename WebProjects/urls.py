from django.conf.urls import include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Admin URL:
    url(r'^admin/', include(admin.site.urls)),

    # Default URL:
    url(r'^', include('projects.urls', namespace="projects")),
]
