from django.shortcuts import render
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required

@permission_required('wagtailadmin.access_admin')
def styleguide(request, template='marco_site/styleguide.html'):
    return render(request, template, RequestContext(request, {}))
