from housing_affordability.models import *
import asana


def search_vars(request):

    sgovs = Government.objects.prefetch_related('gov_demographic_set')\
                             .filter(Q(gov_demographic__var__var_name='population_total') &\
                                     Q(gov_demographic__value__gt=30000) &\
                                     Q(gov_demographic__var__year=2016))

    return {
        'govs': sgovs
        }
