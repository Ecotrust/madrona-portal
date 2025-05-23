from django import template
from django.template.loader import get_template
from portal.welcome_snippet.models import WelcomePage

register = template.Library()

@register.simple_tag(takes_context=True)
def welcome_entry(context):
    t = get_template("welcome_snippet/welcome_entry.html")
    try:
        welcome_entry = WelcomePage.objects.get(active=True)
    except WelcomePage.DoesNotExist:
        return ""

    return t.render({
        'welcome_entry': welcome_entry,
    },context['request'])

@register.simple_tag(takes_context=True)
def welcome_title(context):
    try:
        welcome_entry = WelcomePage.objects.get(active=True)
    except WelcomePage.DoesNotExist:
        return ""

    return welcome_entry.title
