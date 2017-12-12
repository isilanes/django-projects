# Standard libs:
import os
import pytz
from datetime import datetime, timedelta

# Django libs:
from django.utils import timezone
from django.shortcuts import render
from django.http import JsonResponse

# Our libs:
from WebProjects import settings
from projects.models import Project, IP, Reservation, Period

# Indices:
def index(request, showprojs="noshow"):
    project_list = Project.objects.filter(finished=False).order_by('id')
    ip_list = set([x.ip for x in project_list])

    # Sort ip_list by quota:
    dsu = []
    for ip in ip_list:
        dsu.append([ip.get_quota_raw(), ip.ip_name, ip])
    dsu.sort()
    dsu.reverse()

    ip_list = [z for x,y,z in dsu]

    quotas = [x.get_quota() for x in project_list]
    tot_quota = '{0:.2f}'.format(sum(quotas)/1000.0)
    
    context = {
        'project_list': project_list,
        'nprojs': len(project_list),
        'nips': len(ip_list),
        'tot_quota': tot_quota,
        'ip_list': ip_list,
        'show': showprojs,
    }
    
    return render(request, 'projects/index.html', context)

def project_index(request, status="open"):
    """Show a list of project in diferent states."""

    if status == 'expired':
        # Order expired projects by expiration date, not ID:
        dsu = [(p.how_long_ago_expired, p) for p in Project.objects.filter(finished=False, in_buffer=False) if p.is_expired]
        dsu = sorted(dsu, reverse=True)
        project_list = [y for x,y in dsu]
    elif status == 'frozen':
        project_list = []
        dsu = []
        for p in  Project.objects.order_by('id'):
            if p.in_buffer:
                dsu.append([p.how_long_ago_expired, p])
        dsu.sort()
        dsu.reverse()
        project_list = [ y for x,y in dsu ]
    elif status == 'all':
        project_list = Project.objects.order_by('id')
    else: # abiertos
        project_list = Project.objects.filter(finished=False).filter(in_buffer=False).order_by("id")

    ips = set([ x.ip.ip_name for x in project_list ])

    quotas = [ x.get_quota() for x in project_list ]
    tot_quota = '{0:.2f}'.format(sum(quotas)/1000.0)
    
    context = {
        'project_list': project_list,
        'nprojs': len(project_list),
        'nips': len(ips),
        'tot_quota': tot_quota,
        'status': status,
    }

    if status == 'expired':
        return render(request, 'projects/project_index_expired.html', context)
    elif status == 'frozen':
        return render(request, 'projects/project_index_frozen.html', context)
    else:
        return render(request, 'projects/project_index.html', context)


# Details:
def detail(request, project_id=None):
    prj = Project.objects.get(pk=project_id)

    context = {
        'project': prj,
    }

    return render(request, 'projects/detail.html', context)

def ip_detail(request, ip_id=None):
    ip = IP.objects.get(pk=ip_id)

    context = {
        'ip': ip,
    }

    return render(request, 'projects/ip_detail.html', context)
 

# Info:
def readme(request):
    context = {}

    return render(request, 'projects/README', context)

def reservations(request):
    """Show view for Reservations."""

    reservation_list = []
    for r in Reservation.objects.order_by("start"):
        reservation_list.append(r)

    context = {
        'reservation_list': reservation_list,
    }
    
    return render(request, 'projects/reservations.html', context)


# Data:
def disk_accounting(request, year, month):
    """Return JSON with disk accounting data."""

    # Base data:
    year = int(year)
    month = int(month)
    tz = timezone.get_default_timezone()

    # Build period data:
    start = timezone.datetime(year=year, month=month, day=1, tzinfo=tz)
    if month == 12:
        end = timezone.datetime(year=year+1, month=1, day=1, tzinfo=tz)
    else:
        end = timezone.datetime(year=year, month=month+1, day=1, tzinfo=tz)

    # Filter Periods overlapping with requested period, and gather data:
    disk_cost_of, ip_of, name_of, id_of, account_of = {}, {}, {}, {}, {}
    for period in Period.objects.filter(end__gt=start, start__lt=end):
        k = period.proj.pk
        disk_cost_of[k] = disk_cost_of.get(k, 0.0) + period.disk_cost(start, end)
        id_of[k] = period.proj.proj_id
        ip_of[k] = period.proj.ip.ip_name
        name_of[k] = period.proj.name
        account_of[k] = period.proj.user

    # Encapsulate data to return:
    data = {
        "disk_cost_of": disk_cost_of,
        "ip_of": ip_of,
        "name_of": name_of,
        "id_of": id_of,
        "account_of": account_of,
    }

    return JsonResponse(data)

def reservation_plot_data(request):
    """Return JSON with reservation data to be plotted."""

    data = {
        "data": get_reservation_plot_data(),
        "borderColor": "rgba(50, 50, 255, 1.0)",
        "backgroundColor": "rgba(100, 100, 255, 0.5)",
        "label": "Nodos reservados",
    }

    return JsonResponse(data)

def account_exists(request, account):
    """Return whether or not account named 'account' exists."""

    try:
        Project.objects.filter(finished=False).get(user=account)
        exists = True
    except:
        exists = False

    data = {
        "response": exists,
    }

    return JsonResponse(data)

def ip_exists(request, name):
    """Use 'name' name fragment to find a single IP (investigador principal)
    with that name. Return a single IP object. Anything else returns None.
    """
    ip = get_ip(name)

    exists = ip is not None

    data = {
        "response": exists,
    }

    return JsonResponse(data)


# Actions:
def create_account(request, token, ip, end, title, account, id, quota):
    """Create account."""

    # Poor-man's authentication:
    if token != settings.J["ACTION_TOKEN"]:
        return JsonResponse({})

    # Get the IP for the project:
    proj_ip = get_ip(ip)

    # Starting and ending dates:
    #start_date, end_date = generate_period(opts.start_date, opts.end_date)
    tz = pytz.timezone("Europe/Madrid")
    start_date = datetime.now(tz)
    end_date = datetime.strptime(end, "%Y%m%d%H%M")
    end_date = timezone.make_aware(end_date, timezone=tz)

    # Create Project object:
    P = Project(ip = proj_ip,
                name = title,
                user = account,
                proj_id = id.replace("-", "/"))
    P.save()

    # Create Period object:
    Pe = Period(proj = P,
                start = start_date,
                end = end_date,
                quota = quota,
                status = "active")
    Pe.save()

    # Success:
    return JsonResponse({"response": True})


# Utility functions:
def get_reservation_plot_data():
    """Return data for reservation data plot."""
    
    timezone = pytz.timezone("Europe/Madrid")
    t0 = datetime.now(timezone)

    # Get all "milestones" (reservation starts or ends):
    milestones = []
    for res in Reservation.objects.all():
        if not res.passed:
            m = (res.start, res.nodes)
            milestones.append(m)
            m = (res.end, -res.nodes)
            milestones.append(m)

    #current_date = sorted(milestones)[0][0]
    current_nodes = 0
    X, Y = [], []
    for t, n in sorted(milestones):
        pre, post = current_nodes, current_nodes + n
        current_nodes += n

        # Discard dates before "now":
        if t < t0:
            X = [t]
            Y = [post]
        else:
            # Pre- and post- bump:
            X.append(t)
            X.append(t)
            Y.append(pre)
            Y.append(post)
    
    X = [t.strftime("%Y-%m-%d %H:%M") for t in X]

    data = [{"x": x, "y": y} for x, y in zip(X, Y)]

    return data

def get_ip(name):
    """Use 'name' name fragment to find a single IP (investigador principal)
    with that name. Return a single IP object. Anything else returns None.
    """
    try:
        ip = IP.objects.get(ip_name__contains=name)
        return ip
    except IP.MultipleObjectsReturned:
        return None
    except IP.DoesNotExist:
        return None

