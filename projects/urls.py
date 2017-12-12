from django.conf.urls import url

from projects import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    # IP index:
    url(r'^(?P<showprojs>show)$', views.index, name='index'),

    # Project indices:
    url(r'^projects/$', views.project_index, name='project_index'),
    url(r'^projects/(?P<status>\w+)/$', views.project_index, name='project_index'),

    # Details:
    url(r'^project/(?P<project_id>\d+)/$', views.detail, name='detail'),
    url(r'^ip/(?P<ip_id>\d+)/$', views.ip_detail, name='ip_detail'),

    # Info:
    url(r'^readme$', views.readme, name='readme'),
    url(r'^reservations$', views.reservations, name='reservations'),

    # Data:
    url(r'^disk_accounting/(?P<year>\d{4})/(?P<month>\d{2})$', views.disk_accounting, name='disk_accounting'),
    url(r'^account_exists/(?P<account>\w+)/$', views.account_exists, name='account_exists'),
    url(r'^ip_exists/(?P<name>[\w ]+)/$', views.ip_exists, name='ip_exists'),
    url(r'^reservation_plot_data/$', views.reservation_plot_data, name='reservation_plot_data'),

    # Actions:
    url(r'^create_account/(?P<token>\w+)/(?P<ip>[\w ]+)/(?P<end>\d{12})/(?P<title>[\w ]+)/(?P<account>\w+)/(?P<id>[\w\d-]+)/(?P<quota>\d+)/$', views.create_account, name='create_account'),
]
