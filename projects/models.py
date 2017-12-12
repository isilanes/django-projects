# Django stuff:
from django.db import models
from django.utils import timezone

# Standard libs:
from datetime import datetime, date
from dateutil.relativedelta import relativedelta as rdelta

# Constants:
DISK_PRICE = 0.50 # euros per TB day
PENALTY_EXPIRED = 1.50 # multiplier for DISK_PRICE over expired periods
BONUS_BUFFER = 0.50 # multiplier (< 1) for price_disk when in IHBuffer

# Functions:
def num2eng(num, decimals=2):
    """Take a float "num" and return in engineer scale, with "decimals" amount of decimals.
    E.g.:
    num2eng(10,1) = 10.0
    num2eng(23000,2) = 23.00 k
    num2eng(1500000,1) = 1.5 M
    """
    fmt = '{0:.' + str(decimals) + 'f}'
    if num > 10**6:
        return fmt.format(num/10**6) + ' M'
    elif num > 10**3:
        return fmt.format(num/10**3) + ' k'
    else:
        return fmt.format(num)


# Classes:
class IP(models.Model):
    ip_name = models.CharField('Name of IP', max_length=200)

    # Public methods:
    def get_n_projs(self):
        """Return x,y, where x = amount of open projects, and y = total
        amount of projects.
        """
        ntot = len(self.project_set.all())
        nopen = len([ x for x in self.project_set.all() if not x.finished ])

        return nopen, ntot

    def get_cpuh(self):
        cpuh_active = 0
        cpuh_total = 0
        for p in self.project_set.all():
            c = p.cpuh
            cpuh_total += c
            if not p.finished:
                cpuh_active += c

        return [ num2eng(x,1) for x in [ cpuh_active, cpuh_total ] ]

    def get_disk_usage(self):
        gbd_active = 0
        gbd_total = 0
        for p in self.project_set.all():
            c = p.get_disk_usage()
            gbd_total += c
            if not p.finished:
                gbd_active += c

        return [ num2eng(x,1) for x in [ gbd_active, gbd_total ] ]

    def get_quota_raw(self):
        """Return x,y, where x = aggregated quota of all open projects
        of IP. y = aggregated quota of all projects of IP, open or
        closed. Units are GB.
        """
        q_active = 0
        q_total = 0
        for p in self.project_set.all():
            c = p.get_quota()
            q_total += c
            if not p.finished:
                q_active += c

        return q_active, q_total

    def get_quota(self):
        q_active, q_total = self.get_quota_raw()
        return [ num2eng(x,1) for x in [ q_active, q_total ] ]

    def get_open_projs(self):
        return [ x for x in self.project_set.all() if not x.finished ]


    # Special methods:
    def __unicode__(self):
        return self.ip_name

    def __str__(self):
        return self.ip_name

class Project(models.Model):
    ip = models.ForeignKey(IP)
    name = models.CharField(max_length=200)
    user = models.CharField(max_length=20)
    finished = models.BooleanField(default=False)
    in_buffer = models.BooleanField(default=False)
    cpuh = models.FloatField(default=0.0)
    proj_id = models.CharField(max_length=100)

    # Public methods:
    def get_max_quota(self):
        """Return the largest quota the Project has ever had."""

        max_q = 0
        for p in self.period_set.all():
            if p.quota > max_q:
                max_q = p.quota

        return max_q

    def get_duration(self):
        """Return duration of Project, in days."""

        end = self.get_end()
        if end < timezone.now():
            end = timezone.now()

        return (end - self.get_start()).days

    def mk_periods(self):
        """Generate list of periods the Project contains.
        Each element of the list is a list of four elements:
        [start, end, dta, q, status]
        start: datetime() of start of period
        end: datetime() of end of period
        dta: duration of period, in days (yes, redundant)
        q: quota, in GB
        status: either 'ok', 'ko' or 'buffer'
        """
        periods = []
        old_end, old_q = None, None
        for p in Period.objects.filter(proj=self.id).order_by("start"):
            start_date = p.start
            if old_end and start_date.date() == old_end.date():
                start_date += rdelta(days=1)

            # Check for a possible expired period in
            # between end of previous period and start
            # of current one:
            if old_end and (p.start - old_end).days > 0:
                dta = (p.start - old_end).total_seconds()/86400.
                q = old_q
                periods.append([old_end, p.start, dta, q, 'ko'])

            dta = (p.end - p.start).total_seconds()/86400.
            status2str = {
                "expired": "ko",
                "frozen": "buffer",
                "active": "ok",
            }
            periods.append([start_date, p.end, dta, p.quota, status2str[p.status]])

            old_end = p.end
            old_q = p.quota

        # If project finished, that's it. Else:
        if not self.finished:
            now = timezone.now()
            if old_end < now:
                dta = (now - old_end).total_seconds()/86400.
                if self.in_buffer:
                    periods.append([old_end, now, dta, old_q, 'buffer'])
                else:
                    periods.append([old_end, now, dta, old_q, 'ko'])

        return periods

    def get_disk_usage(self):
        """Returns amount of GB*day used throughout the Project."""

        ordered_projects = self.period_set.order_by("start")

        gbd = 0
        prev_q = None
        prev_end = ordered_projects[0].start
        for p in ordered_projects:
            dta = (p.end - prev_end).days
            gbd += dta*p.quota
            prev_end = p.end
            prev_q = p.quota

        # Does last period cover up to now? i.e.: is the
        # project expired? Only relevant if project not
        # finished:
        if not self.finished:
            now = timezone.now()
            if prev_end < now:
                dta = (now - prev_end).days
                gbd += dta*prev_q

        return gbd

    def get_disk_usage_str(self):
        """Return disk usage, as a string."""

        gbd = self.get_disk_usage()

        return num2eng(gbd,1)

    def get_start(self):
        """Returns starting date, or None."""

        try:
            return Period.objects.filter(proj=self).filter(status="active").order_by("start")[0].start
        except:
            return None

    def get_start_str(self):
        """Use get_start() to return date in custom string format."""

        try:
            return datetime.strftime(self.get_start(), "%Y-%m-%d")
        except:
            return None

    def get_end(self):
        """Return end date, as defined by ending of latest active period."""

        try:
            return Period.objects.filter(proj=self).filter(status="active").order_by("-end")[0].end
        except:
            return None

    def get_end_str(self):
        """Use get_end() to return date in custom string format."""

        try:
            return datetime.strftime(self.get_end(), "%Y-%m-%d")
        except:
            return None

    def get_neptuno_end(self):
        """Return end date, as defined by ending of latest
        period, either active or expired, not frozen (that is
        the date on which the project leaves Neptuno).
        """
        end = None
        for period in self.period_set.all():
            if period.status in [ "active", "expired" ]:
                d = period.end
                if not end or d > end:
                    end = d

        now = timezone.now()
        if not self.finished and not self.in_buffer:
            if now > end:
                end = now

        return end

    def get_definitive_end(self):
        """Return end date, as defined by ending of latest
        period, either active, expired, or frozen.
        """
        end = None
        for period in self.period_set.all():
            d = period.end
            if not end or d > end:
                end = d

        now = timezone.now()
        if not self.finished:
            if now > end:
                end = now

        return end

    def get_quota(self):
        """Return current quota of active Project.
        Return 0 for finished Projects.
        """
        # Finished Projects don't count:
        if self.finished:
            return 0

        return Period.objects.filter(proj=self.pk).order_by("-end")[0].quota

    def get_status(self):
        """Return status of Project, as a string.

        Terminado -> closed and deleted
        Congelado -> moved to IHBuffer
        Expirado  -> expired, but still in Neptuno
        Activo    -> active
        """
        if self.finished:
            return 'Terminado'
        elif self.in_buffer:
            return 'Congelado'
        elif self.is_expired:
            return "Expirado"
        else:
            return "Activo"

    def get_cpuh_str(self):
        return num2eng(self.cpuh,1)


    # Public properties:
    @property
    def is_expired(self):
        """Return 1 if expired, 0 if still active."""

        if self.get_end() < timezone.now():
            return 1

        return 0

    @property
    def how_long_ago_expired(self):
        """How many days ago it expired. Return 0 if not expired."""

        if not self.is_expired:
            return 0

        return (timezone.now() - self.get_end()).days

    @property
    def ihbuffer_date(self):
        """Date in which project will go to IHBuffer."""

        return self.get_end() + rdelta(months=+6)

    @property
    def ihbuffer_date_str(self):
        """Date YYYY-MM-DD string in which project will go to IHBuffer."""

        return datetime.strftime(self.ihbuffer_date, "%Y-%m-%d")

    @property
    def deletion_date(self):
        """Return date in which project will be deleted from IHBuffer."""

        return self.get_end()+rdelta(months=+18)

    @property
    def deletion_date_str(self):
        """Return date in which project will be deleted from IHBuffer."""

        return datetime.strftime(self.deletion_date, "%Y-%m-%d")


    # Special methods:
    def __unicode__(self):
        fmt  = u"Account {s.user} for project '{s.name}' with ID '{s.proj_id}' and IP {s.ip}."
        fmt += u" Opens on {sd}, closes on {se}."
        string = fmt.format(s=self, sd=self.get_start_str(), se=self.get_end_str())

        return string
    
    def __str__(self):
        return self.__unicode__()
    
    def __lt__(self, other):
        return self.proj_id < other.proj_id

class Period(models.Model):
    proj = models.ForeignKey(Project)
    start = models.DateTimeField("Starting date")
    end = models.DateTimeField("Ending date")
    quota = models.FloatField(default=0)

    # Whether during this period the project was:
    # active - not expired yet
    # expired - already expired (still in Neptuno)
    # frozen - in IHBuffer
    status = models.CharField(max_length=25, default="active")

    # Public methods:
    def overlap(self, start, end):
        """Returns days of overlap of Period with (start, end) period."""

        if self.end < start or self.start > end:
            return 0

        max_start = max(self.start, start)
        min_end = min(self.end, end)

        return (min_end - max_start).total_seconds()/86400.

    def disk_cost(self, start, end):
        """Return monetary cost associated with given (start, end) period.
        Cost is a price (DISK_PRICE), times overlap days, 
        times a recharge (PENALTY_EXPIRED) if expired, 
        or a bonus (BONUS_BUFFER) if in IHBuffer.
        """
        cost = DISK_PRICE*self.overlap(start, end)*self.quota/1000. # GB -> TB

        if self.status == "expired":
            return cost*PENALTY_EXPIRED
        elif self.status == "frozen":
            return cost*BONUS_BUFFER
        else:
            return cost


    # Special methods:
    def __unicode__(self):
        fmt  = u"{s.quota:.0f} GB for {s.status} project '{s.proj.name}' from {s.start:%Y-%m-%d %H:%M} "
        fmt += u"to {s.end:%Y-%m-%d %H:%M}"

        return fmt.format(s=self)

    def __str__(self):
        return self.__unicode__()
    
class Reservation(models.Model):
    name = models.CharField("Name of reservation", max_length=50, default="reservation")
    start = models.DateTimeField("Starting date", default=timezone.now)
    end = models.DateTimeField("Ending date", default=timezone.now)
    nodes = models.IntegerField("Amount of nodes", default=1)

    # Public methods:
    def is_active_on(self, day):
        """Return True if reservation is active on day 'day'."""

        return self.start <= day < self.end


    # Public properties:
    @property
    def passed(self):
        """Return True if Reservation is in the past. False otherwise."""

        return self.end < timezone.now()

    @property
    def days(self):
        """Amount of days of duration."""

        return (self.end - self.start).total_seconds()/86400.

    @property
    def style(self):
        """Style for template."""

        if self.passed:
            return 'class="Atenuado"'
        
        return ""

    @property
    def size(self):
        """Amount of nodes*days."""

        return self.nodes * self.days


    # Special methods:
    def __lt__(self, other):
        return self.name < other.name

    def __str__(self):
        return "{s.name}: {s.nodes} nodes from {s.start:%Y-%m-%d} to {s.end:%Y-%m-%d}".format(s=self)

