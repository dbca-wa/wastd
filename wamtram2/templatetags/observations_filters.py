from django import template
from wamtram2.models import TrtObservations

register = template.Library()

@register.filter
def get_observation(observation_id):
    try:
        return TrtObservations.objects.get(pk=observation_id)
    except TrtObservations.DoesNotExist:
        return None
