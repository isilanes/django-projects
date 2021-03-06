# Django libs:
from django.urls import path, re_path, register_converter

# Our libs:
from . import converters, views


# Constants:
app_name = "projects"


# Register converters:
register_converter(converters.GeneralName, 'ip_name')
register_converter(converters.GeneralName, 'acc_name')
register_converter(converters.DateStamp, 'tstamp')
register_converter(converters.NameWithSpaces, 'sname')


# URL patterns:
urlpatterns = [
    # Main index:
    path('', views.index, name='index'),
    re_path(r'^(?P<show_projs>show)$', views.index, name='index'),

    # Project indices:
    path('projects/', views.project_index, name='project_index'),
    path('projects/<slug:status>', views.project_index, name='project_index'),

    # Details:
    path('project/<int:project_id>', views.detail, name='detail'),
    path('ip/<int:ip_id>', views.ip_detail, name='ip_detail'),

    # Info:
    path('readme', views.readme, name='readme'),
    path('reservations', views.reservations, name='reservations'),

    # Data:
    path('disk_accounting/<int:year>/<int:month>', views.disk_accounting, name='disk_accounting'),
    path('account_exists/<acc_name:account>', views.account_exists, name='account_exists'),
    path('ip_exists/<ip_name:name>', views.ip_exists, name='ip_exists'),
    path('reservation_plot_data', views.reservation_plot_data, name='reservation_plot_data'),

    # Actions:
    path('create_account/<slug:token>/<sname:ip>/<tstamp:end>/<sname:title>/<acc_name:account>/<slug:id>/<int:quota>',
         views.create_account, name='create_account'),
]
