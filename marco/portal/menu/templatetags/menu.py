from django import template
from django.template.loader import get_template
from portal.menu.models import Menu
from django.shortcuts import render

register = template.Library()

@register.simple_tag(takes_context=True)
def menus(context, kind='header', menu_type='dropdown'):
    """Template tag to render all available menus.
    """
    template_name = "menu/tags/%s.html" % menu_type
    t = get_template(template_name)

    footer = (kind == 'footer')
    menus = Menu.objects.filter(active=True, footer=footer)

    # path = context['request'].path
    # highlighted = any([path.startswith(e.destination) for e in menu.entries.all()])
    highlighted = False
    return_context = {
        # 'menu': menu,
        'menus': menus,
        'highlighted': highlighted,
        'request': context['request'],
    }

    return render(context['request'], template_name, return_context)
