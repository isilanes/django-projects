from django.contrib import admin
from .models import Project, IP, Period, Reservation

class PeriodInline(admin.StackedInline):
    model = Period
    extra = 1

class ProjectAdmin(admin.ModelAdmin):
    fields = [ 'name', 'finished', 'in_buffer', 'ip', 'cpuh', 'user', 'proj_id' ]
    list_display = ('name', 'ip')
    list_filter = [ 'ip' ]
    search_fields = [ 'name' ]
    inlines = [ PeriodInline ]


admin.site.register(IP)
admin.site.register(Period)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Reservation)
