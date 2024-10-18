from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
import datetime

class DateRangeFilter(SimpleListFilter):
    title = _('incident date range')  # or use any title you want

    parameter_name = 'incident_date_range'  # URL parameter

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each tuple is the coded value 
        for the option that will appear in the URL query. The second element is the 
        human-readable name for the option that will appear in the right sidebar.
        """
        return (
            ('today', _('Today')),
            ('past_7_days', _('Past 7 days')),
            ('this_month', _('This month')),
            # Add more options here
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value provided in the query string 
        and retrievable via `self.value()`.
        """
        if self.value() == 'today':
            return queryset.filter(incident_date=datetime.date.today())
        if self.value() == 'past_7_days':
            return queryset.filter(incident_date__gte=datetime.date.today() - datetime.timedelta(days=7))
        if self.value() == 'this_month':
            month = datetime.date.today().month
            year = datetime.date.today().year
            return queryset.filter(incident_date__month=month, incident_date__year=year)
        # Add more filters here
